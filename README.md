# 🚀 Rokey Last-Mile Delivery System

YOLOv8과 Turtlebot4 2대를 이용한 지능형 배송 서비스 시스템입니다.

## 📋 프로젝트 개요

본 프로젝트는 다음과 같은 기능을 제공합니다:

- **객체 감지**: YOLOv8 모델을 이용한 실시간 객체 인식
- **QR 코드 인식**: 배송 목적지 식별을 위한 QR 코드 스캔
- **자율 내비게이션**: 2대의 Turtlebot4를 이용한 협력 배송
- **Following Car 시스템**: 선행 로봇을 따라가는 후행 로봇

## 🏗️ 시스템 아키텍처

```
├── mini_project/          # 메인 프로젝트 모듈
│   ├── detection/         # 객체 감지 모듈
│   ├── navigation/        # 내비게이션 모듈
│   └── model/            # YOLOv8 모델 파일
├── qr_detector_camera/    # QR 코드 감지 모듈
├── qr_interfaces/         # ROS2 메시지/서비스 인터페이스
└── test_website/          # 웹 기반 모니터링 시스템
```

## 🛠️ 설치 및 설정

### 1. 필수 요구사항

- ROS2 Humble/Foxy
- Python 3.8+
- Turtlebot4 패키지
- OpenCV
- PyTorch

### 2. 모바일 앱 설치 (Android)

카메라 스트리밍을 위해 IP-Webcam 앱을 설치하세요:

- [IP-Webcam 다운로드](https://play.google.com/store/apps/details?id=com.pas.webcam&hl=ko&pli=1)

### 3. YOLOv8 모델 다운로드

```bash
cd ~/rokey_c3_mini/src/mini_project/model/
# 모델 파일을 해당 경로에 배치
# real_final_best.pt 파일이 필요합니다
```

### 4. 워크스페이스 빌드

```bash
cd ~/rokey_c3_mini
colcon build
source install/setup.bash
```

## � 실행 방법

### 1. 감지 시스템 실행

```bash
ros2 launch mini_project detection_system.launch.py
```

### 2. 내비게이션 시스템 실행 (순서 중요!)

#### (1) Turtlebot4 Navigation 실행

```bash
# Robot 8 (선행 로봇)
ros2 launch turtlebot4_navigation localization.launch.py namespace:=robot8 map:=$HOME/rokey_c3_mini/src/mini_project/map/map.yaml
ros2 launch turtlebot4_navigation nav2.launch.py namespace:=/robot8
ros2 launch turtlebot4_viz view_robot.launch.py namespace:=/robot8

# Robot 9 (후행 로봇)
ros2 launch turtlebot4_navigation localization.launch.py namespace:=robot9 map:=$HOME/rokey_c3_mini/src/mini_project/map/map.yaml
ros2 launch turtlebot4_navigation nav2.launch.py namespace:=/robot9
ros2 launch turtlebot4_viz view_robot.launch.py namespace:=/robot9
```

#### (2) 커스텀 ROS2 노드 실행

```bash
# Action Manager (각 로봇별)
ros2 run mini_project action_manager --ros-args -r __ns:=/robot8 -r /tf:=/robot8/tf -r /tf_static:=/robot8/tf_static
ros2 run mini_project action_manager --ros-args -r __ns:=/robot9 -r /tf:=/robot9/tf -r /tf_static:=/robot9/tf_static

# Following Car (후행 로봇)
ros2 run mini_project following_car --ros-args -r __ns:=/robot8 -r /tf:=/robot8/tf -r /tf_static:=/robot8/tf_static

# Task Manager (전체 시스템 관리)
ros2 run mini_project task_manager
```

### 3. 설정 시스템 실행

```bash
ros2 launch mini_project setting_system.launch.py
```

## 📊 모니터링

웹 기반 모니터링 시스템을 통해 시스템 상태를 확인할 수 있습니다:

```bash
cd src/test_website
python app.py
```

브라우저에서 `http://localhost:5000`에 접속하여 대시보드를 확인하세요.

## 🗺️ 맵 파일

프로젝트에는 다음과 같은 맵 파일들이 포함되어 있습니다:

- `map.yaml`: 메인 맵 설정 파일
- `map.pgm`: 맵 이미지 파일
- `best_1.json`, `best_2.json`, `best_3.json`: 최적화된 경로 파일
