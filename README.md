# How to connect a huggingface to ROS2 nodes
How to download and predict yolov8 instance segmentation .pt file from the web  
```
cd ros2_ws/src
git clone https://github.com/Jinsun-Lee/yolov8_pkg
cd ~/ros2_ws
colcon build --packages-select yolov8_ros --symlink-install
source ./install/setup.bash 
ros2 run yolov8_ros image_pub 
ros2 run yolov8_ros predict_pub 
```

full video: https://youtu.be/RxBEsf8UcXo  
huggingface link: https://huggingface.co/gogoring/simulation_ws/tree/main

