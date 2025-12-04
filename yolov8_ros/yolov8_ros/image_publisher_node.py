import rclpy 
from rclpy.node import Node 
from sensor_msgs.msg import Image 
from std_msgs.msg import Header
from cv_bridge import CvBridge
from yolov8_ros import get_path

from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSDurabilityPolicy, QoSReliabilityPolicy

import sys
import cv2
import os

#---------------Variable Setting---------------
PUB_TOPIC_NAME = 'image_raw' #'/camera/rgb/image_bgr8'
DATA_SOURCE = 'video' #'camera'
CAM_NUM = 0
IMAGE_DIRECTORY_PATH = 'src/camera_perception_pkg/lib/Collected_Datasets/sample_dataset'
VIDEO_FILE_PATH = get_path("driving_simulation.mp4")
SHOW_IMAGE = False
TIMER = 0.03
#----------------------------------------------

class ImagePublisherNode(Node):
    def __init__(self, data_source=DATA_SOURCE, cam_num=CAM_NUM,
                 img_dir=IMAGE_DIRECTORY_PATH, video_path=VIDEO_FILE_PATH,
                 pub_topic=PUB_TOPIC_NAME, logger=SHOW_IMAGE, timer=TIMER):
        
        super().__init__('image_publisher_node')

        # Declare parameters
        self.declare_parameter('data_source', data_source)
        self.declare_parameter('cam_num', cam_num)
        self.declare_parameter('img_dir', img_dir)
        self.declare_parameter('video_path', video_path)
        self.declare_parameter('pub_topic', pub_topic)
        self.declare_parameter('logger', logger)
        self.declare_parameter('timer', timer)

        # Get parameters
        self.data_source = self.get_parameter('data_source').get_parameter_value().string_value
        self.cam_num = self.get_parameter('cam_num').get_parameter_value().integer_value
        self.img_dir = self.get_parameter('img_dir').get_parameter_value().string_value
        self.video_path = self.get_parameter('video_path').get_parameter_value().string_value
        self.pub_topic = self.get_parameter('pub_topic').get_parameter_value().string_value
        self.logger = self.get_parameter('logger').get_parameter_value().bool_value
        self.timer_period = self.get_parameter('timer').get_parameter_value().double_value

        # QoS
        self.qos_profile = QoSProfile(
            reliability=QoSReliabilityPolicy.RELIABLE,
            history=QoSHistoryPolicy.KEEP_LAST,
            durability=QoSDurabilityPolicy.VOLATILE,
            depth=1
        )

        self.br = CvBridge()

        # Select Data Source
        if self.data_source == 'camera':
            self.cap = self.open_camera_force(self.cam_num)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        elif self.data_source == 'video':
            self.cap = cv2.VideoCapture(self.video_path)
            if not self.cap.isOpened():
                self.get_logger().error(f"Cannot open video file: {self.video_path}")
                rclpy.shutdown()
                sys.exit(1)

        elif self.data_source == 'image':
            if os.path.isdir(self.img_dir):
                self.img_list = sorted(os.listdir(self.img_dir))
                self.img_num = 0
            else:
                self.get_logger().error(f"Not a directory: {self.img_dir}")
                rclpy.shutdown()
                sys.exit(1)

        else:
            self.get_logger().error(f"Invalid data source: {self.data_source}")
            rclpy.shutdown()
            sys.exit(1)

        self.publisher = self.create_publisher(Image, self.pub_topic, self.qos_profile)
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

    # 🔧 CAM_NUM만 무조건 재시도하는 함수
    def open_camera_force(self, cam_num):
        while True:
            self.get_logger().info(f"Trying to open /dev/video{cam_num} ...")
            cap = cv2.VideoCapture(cam_num)

            if cap.isOpened():
                self.get_logger().info(f"Camera /dev/video{cam_num} opened successfully!")
                return cap

            self.get_logger().warn(f"Failed to open /dev/video{cam_num}. Retrying...")
            rclpy.sleep(0.5)

    def timer_callback(self):
        if self.data_source == 'camera':
            ret, frame = self.cap.read()

            # read 실패 시 재연결
            if not ret:
                self.get_logger().warn(f"Frame read failed. Reopening /dev/video{self.cam_num} ...")
                self.cap.release()
                self.cap = self.open_camera_force(self.cam_num)
                return

            # Resize + Publish
            frame = cv2.resize(frame, (640, 480))
            image_msg = self.br.cv2_to_imgmsg(frame, encoding='bgr8')
            image_msg.header.stamp = self.get_clock().now().to_msg()
            image_msg.header.frame_id = 'camera_frame'
            self.publisher.publish(image_msg)

            if self.logger:
                cv2.imshow('Camera', frame)
                cv2.waitKey(1)

        elif self.data_source == 'image':
            if self.img_num >= len(self.img_list):
                self.img_num = 0

            img_path = os.path.join(self.img_dir, self.img_list[self.img_num])
            img = cv2.imread(img_path)

            if img is not None:
                img = cv2.resize(img, (640, 480))
                image_msg = self.br.cv2_to_imgmsg(img, encoding='bgr8')
                image_msg.header.stamp = self.get_clock().now().to_msg()
                image_msg.header.frame_id = 'image_frame'
                self.publisher.publish(image_msg)

                if self.logger:
                    cv2.imshow('Image', img)
                    cv2.waitKey(1)

            self.img_num += 1

        elif self.data_source == 'video':
            ret, img = self.cap.read()

            if not ret:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return

            img = cv2.resize(img, (640, 480))
            image_msg = self.br.cv2_to_imgmsg(img, encoding='bgr8')
            image_msg.header.stamp = self.get_clock().now().to_msg()
            image_msg.header.frame_id = 'video_frame'
            self.publisher.publish(image_msg)

            if self.logger:
                cv2.imshow('Video', img)
                cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisherNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print("\nshutdown\n")

    node.destroy_node()
    if hasattr(node, 'cap') and node.cap.isOpened():
        node.cap.release()
    cv2.destroyAllWindows()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
