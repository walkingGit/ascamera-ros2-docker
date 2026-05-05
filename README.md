# Nuwa-HP60C + MyCobot Pro 450 All-in-One Docker

## How to Control the Arm

### Option 1: Inside Docker (same container)

Run the container with both nodes:

```bash
docker run --rm -it --privileged --network host robot-all-in-one \
  bash -c "source /opt/ros/jazzy/setup.bash && source /workspace/ascam_ws/install/setup.bash && python3 /workspace/mycobot_bridge.py & ros2 run ascamera ascamera_node --ros-args -p confiPath:=/workspace/ascam_ws/src/ascamera/configurationfiles -p rgb_width:=640 -p rgb_height:=480 -p depth_width:=640 -p depth_height:=480 -p fps:=15 -p color_pcl:=false"
```

Then in **another terminal** (also inside Docker):
```bash
# Move arm to coordinates (preferred)
ros2 topic pub --once /mycobot/cmd_coords geometry_msgs/Pose \
  "{position: {x: 307, y: -85, z: 507}, orientation: {x: -151.7, y: -29.5, z: -47.6}}"

# Move arm with angles
ros2 topic pub --once /mycobot/cmd_angles sensor_msgs/JointState \
  "{position: [0, -20, -30, 0, 0, -50]}"

# Gripper
ros2 topic pub --once /mycobot/cmd_gripper std_msgs/String "data: 'open'"
ros2 topic pub --once /mycobot/cmd_gripper std_msgs/String "data: 'close'"

# Go home
ros2 topic pub --once /mycobot/cmd_home std_msgs/Bool "data: true"
```

### Option 2: From outside Docker (host machine)

Run the container with ROS2 networking exposed:

```bash
docker run --rm -d --privileged --network host \
  --name robot_container robot-all-in-one \
  bash -c "source /opt/ros/jazzy/setup.bash && source /workspace/ascam_ws/install/setup.bash && python3 /workspace/mycobot_bridge.py"
```

Then from the **host machine** (or any machine on the network), install ROS2 and:
```bash
# Source the same ROS2 distro
source /opt/ros/jazzy/setup.bash

# Set ROS domain to match container
export ROS_DOMAIN_ID=0

# Now you can control the arm from the host!
ros2 topic pub --once /mycobot/cmd_coords geometry_msgs/Pose \
  "{position: {x: 307, y: -85, z: 507}, orientation: {x: -151.7, y: -29.5, z: -47.6}}"

# Read arm status
ros2 topic echo /mycobot/coords
```

### Option 3: Python script on host (no ROS2 needed on host)

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose

class ArmController(Node):
    def __init__(self):
        super().__init__('arm_controller')
        self.pub = self.create_publisher(Pose, '/mycobot/cmd_coords', 10)
    
    def move_to(self, x, y, z, rx, ry, rz):
        msg = Pose()
        msg.position.x = x; msg.position.y = y; msg.position.z = z
        msg.orientation.x = rx; msg.orientation.y = ry; msg.orientation.z = rz
        self.pub.publish(msg)

rclpy.init()
node = ArmController()
node.move_to(307, -85, 507, -151.7, -29.5, -47.6)
```

## Topics Reference

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
| `/camera_publisher/depth0/points` | PointCloud2 | Receive | Point cloud |
