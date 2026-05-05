# Nuwa-HP60C + MyCobot Pro 450 All-in-One Docker

All-in-one Docker image with:
- **Nuwa-HP60C depth camera** (Angstrong Ascamera) — ROS2 driver
- **MyCobot Pro 450** arm control — ROS2 bridge via pymycobot

## Prerequisites

- Docker
- USB camera connected to host
- MyCobot Pro 450 arm on Ethernet (192.168.0.232:4500)
- SDK source code (see below)

## Getting the SDK Source

Download `ascam_ros2_ws.zip` from:
https://drive.google.com/drive/folders/1xEWNVc3yzJcQfptW3G8RhnVioCZK4Uxh

Extract the `ascamera/` folder into this directory.

## Build

```bash
docker build -t robot-all-in-one .
```

## Run

```bash
docker run --rm -it --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  --network host \
  robot-all-in-one
```

## ROS2 Topics

### Depth Camera
| Topic | Description |
|-------|-------------|
| `/camera_publisher/depth0/image_raw` | Depth 640×480 16-bit |
| `/camera_publisher/rgb0/image` | RGB 640×480 |
| `/camera_publisher/depth0/points` | Point cloud |

### MyCobot Arm
| Topic | Description |
|-------|-------------|
| `/mycobot/coords` | Current coordinates (Pose) |
| `/mycobot/angles` | Current joint angles (JointState) |
| `/mycobot/status` | Status string |
| `/mycobot/cmd_coords` | Command: send_coords (Pose) |
| `/mycobot/cmd_angles` | Command: send_angles (JointState) |
| `/mycobot/cmd_gripper` | Command: "open" / "close" / "angle 50" (String) |

## Network

Use `--network host` so the container can reach the arm at 192.168.0.232:4500.
