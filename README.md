# Nuwa-HP60C + MyCobot Pro 450 All-in-One Docker

## The Missing Piece: Eye-In-Hand Calibration

We have:
- ✅ Depth camera mounted on the gripper (eye-in-hand)
- ✅ 3D point cloud + RGB from the camera
- ✅ `send_coords` to move the arm precisely
- ✅ MyCobot ROS2 bridge

What's missing:
- ❌ The transform from camera frame → gripper frame

### The Pipeline We Need

```
1. Depth camera detects object at (u, v, depth)
2. Convert to 3D: (x_cam, y_cam, z_cam) in camera frame
3. Transform to gripper: T_cam_to_gripper * (x_cam, y_cam, z_cam)
4. Add gripper offset: (x_gripper, y_gripper, z_gripper) in arm base frame
5. send_coords(x_base, y_base, z_base, rx, ry, rz)
```

### How to Calibrate

This is a 6-DOF rigid transform problem. Options:

**A. Manual measurement (simplest)**
Measure the physical offset from the gripper mounting plate to the camera's optical center. Approximate rx, ry, rz from the camera's physical orientation.

**B. Geometric calibration (recommended)**
1. Place a known marker (e.g., ArUco/chessboard) at a fixed position
2. Move the arm to N different poses, record:
   - Arm base → gripper transform (from forward kinematics)
   - Camera → marker transform (from marker detection + depth)
3. Solve for camera → gripper transform using least squares

**C. ICP-based (Seline approach)**
Use the end effector's known geometry and point cloud registration.

### ROS2 TF Tree Concept

```
base_link → flange (from robot kinematics)
flange → camera_link (the calibration we need!)
camera_link → object (from depth camera)
```

## Current Capabilities

| Capability | Status |
|-----------|--------|
| Depth camera RGB stream (1280×1040 via UVC) | ✅ |
| Depth camera SDK (640×480 depth + RGB) | ✅ |
| MyCobot coordinate moves (send_coords) | ✅ |
| MyCobot angle moves | ✅ |
| Gripper control | ✅ |
| Camera → Arm coordinate transform | ❌ Needs calibration |

## Quick Start

### Build
```bash
docker build -t robot-all-in-one .
```

### Run
```bash
docker run --rm -it --privileged --network host --name robot robot-all-in-one
```

### Control Arm (2nd terminal)
```bash
# Move via coordinates
docker exec robot ros2 topic pub --once /mycobot/cmd_coords geometry_msgs/Pose \
  "{position: {x: 307, y: -85, z: 507}, orientation: {x: -151.7, y: -29.5, z: -47.6}}"

# Gripper
docker exec robot ros2 topic pub --once /mycobot/cmd_gripper std_msgs/String "data: 'open'"

# Check status
docker exec robot ros2 topic echo /mycobot/coords --once
```

### Check depth camera (3rd terminal)
```bash
docker exec robot ros2 topic hz /camera_publisher/depth0/image_raw
```
