# Nuwa-HP60C / Angstrong Ascamera ROS2 Docker Image

## Build

```bash
# 1. Get the SDK source from Yahboom Google Drive:
#    https://drive.google.com/drive/folders/1xEWNVc3yzJcQfptW3G8RhnVioCZK4Uxh
#    Download ascam_ros2_ws.zip, extract the ascamera/ folder here.

# 2. Build
docker build -t ascamera-ros2 .
```

## Run

```bash
docker run --rm --privileged -v /dev/bus/usb:/dev/bus/usb ascamera-ros2 \
  bash -c "source /opt/ros/jazzy/setup.bash && source /workspace/ascam_ws/install/setup.bash && \
    ros2 run ascamera ascamera_node --ros-args \
      -p confiPath:=/workspace/ascam_ws/src/ascamera/configurationfiles \
      -p rgb_width:=640 -p rgb_height:=480 \
      -p depth_width:=640 -p depth_height:=480 -p fps:=15"
```

## Topics

| Topic | Description |
|-------|-------------|
| `/camera_publisher/depth0/image_raw` | Depth image 640×480 16-bit |
| `/camera_publisher/rgb0/image` | RGB image 640×480 |
| `/camera_publisher/depth0/points` | Point cloud |
| `/camera_publisher/rgb0/camera_info` | RGB camera info |
| `/camera_publisher/depth0/camera_info` | Depth camera info |
