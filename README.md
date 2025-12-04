# 설명  
ROS 2 Humble 노드에서 HuggingFace 모델을 연동하는 방법을 정리한 레포지토리입니다.  
YOLOv8 인스턴스 세그멘테이션 모델(.pt)을 웹에서 다운로드하고, ROS 2 노드에서 추론을 수행하는 예제를 포함합니다.

How to connect a huggingface to ROS2 nodes    
How to download and predict yolov8 instance segmentation .pt file from the web  

<br>  

# 빌드
```
sudo apt install vlc -y
sudo apt install ubuntu-restricted-extras -y
pip3 install ultralytics
pip3 install huggingface_hub
```
```
cd ~/ros2_ws/src
git clone https://github.com/Jinsun-Lee/ros2_huggingface_pkg.git camera
```
```
cd ~/ros2_ws
colcon build --packages-select interfaces_pkg
source ./install/setup.bash
```
```
cd ~/ros2_ws
colcon build --packages-select interfaces_pkg --allow-overriding interfaces_pkg
source ./install/setup.bash
```
```
cd ~/ros2_ws
colcon build --packages-select yolov8_ros --symlink-install
source ./install/setup.bash
```

<br>

# 사용
full video: https://youtu.be/RxBEsf8UcXo  
huggingface link: https://huggingface.co/gogoring/simulation_ws/tree/main
```
cd ~/ros2_ws
source ./install/setup.bash
ros2 run yolov8_ros image_pub 
```
```
cd ~/ros2_ws
source ./install/setup.bash
ros2 run yolov8_ros predict_pub 
```
