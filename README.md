# Nuwa-HP60C + MyCobot Pro 450 All-in-One Docker

## Architecture: How Arm Control Works

```
┌─────────────────────────────────────────────────┐
│                  DOCKER CONTAINER                │
│                                                  │
│  ┌─────────────────┐     ┌──────────────────┐    │
│  │  mycobot_bridge  │     │  ascamera_node   │    │
│  │  (ROS2 node)     │     │  (ROS2 node)     │    │
│  │                  │     │                  │    │
│  │  Publishes:      │     │  Publishes:      │    │
│  │  /mycobot/coords │     │  /camera/...     │    │
│  │  /mycobot/angles │     │  /depth/...      │    │
│  │                  │     │                  │    │
│  │  Subscribes:     │     │                  │    │
│  │  /mycobot/cmd_*  │     │                  │    │
│  └────────┬─────────┘     └──────────────────┘    │
│           │                                       │
│           │ pymycobot (Python library)            │
│           │                                       │
│  ┌────────▼─────────┐                             │
│  │ MyCobot Pro 450  │                             │
│  │ 192.168.0.232    │                             │
│  └──────────────────┘                             │
└─────────────────────────────────────────────────┘
```

**The arm is controlled by ROS2 topics, but the bridge uses pymycobot (Python) internally.**

## 3 Ways to Control

### 1. ROS2 topic pub (most common)
```bash
docker exec robot_container ros2 topic pub --once /mycobot/cmd_coords geometry_msgs/Pose \
  "{position: {x: 307, y: -85, z: 507}, orientation: {x: -151.7, y: -29.5, z: -47.6}}"
```

### 2. Python inside Docker (scripts in the container)
```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose

class MyArm(Node):
    def __init__(self):
        super().__init__('arm_ctl')
        self.pub = self.create_publisher(Pose, '/mycobot/cmd_coords', 10)

    def move(self, x, y, z, rx, ry, rz):
        msg = Pose()
        msg.position.x = x; msg.position.y = y; msg.position.z = z
        msg.orientation.x = rx; msg.orientation.y = ry; msg.orientation.z = rz
        self.pub.publish(msg)

rclpy.init()
arm = MyArm()
arm.move(307, -85, 507, -151.7, -29.5, -47.6)
```

### 3. Python directly via pymycobot (inside container)
```python
from pymycobot import Pro450Client
mc = Pro450Client('192.168.0.232', 4500)
mc.send_coords([307, -85, 507, -151.7, -29.5, -47.6], 30)
mc.set_pro_gripper_close()
```

**All 3 approaches work inside the container.** The ROS2 bridge just wraps pymycobot into ROS2 topics so everything (camera + arm) speaks the same language.

## Quick Start

```bash
# Build
docker build -t robot-all-in-one .
```

### Run everything:
```bash
docker run --rm -it --privileged --network host --name robot robot-all-in-one
```

### In another terminal, control the arm:
```bash
# Via ROS2 topic
docker exec robot ros2 topic pub --once /mycobot/cmd_coords geometry_msgs/Pose \
  "{position: {x: 307, y: -85, z: 507}, orientation: {x: -151.7, y: -29.5, z: -47.6}}"

# Gripper
docker exec robot ros2 topic pub --once /mycobot/cmd_gripper std_msgs/String "data: 'open'"

# Check status
docker exec robot ros2 topic echo /mycobot/coords --once
```

## Topics

| Topic | Type | Direction | Description |
|-------|------|-----------|-------------|
| `/mycobot/cmd_coords` | Pose | Send | Move arm to [x,y,z,rx,ry,rz] |
| `/mycobot/cmd_angles` | JointState | Send | Move arm to joint angles |
| `/mycobot/cmd_gripper` | String | Send | "open", "close", or angle number |
| `/mycobot/cmd_home` | Bool | Send | true = go to safe position |
| `/mycobot/coords` | Pose | Receive | Current coordinates |
| `/mycobot/angles` | JointState | Receive | Current joint angles |
| `/mycobot/gripper` | String | Receive | Gripper position (0-100) |
| `/camera_publisher/depth0/image_raw` | Image | Receive | Depth 640×480 16-bit |
| `/camera_publisher/rgb0/image` | Image | Receive | RGB 640×480 |
