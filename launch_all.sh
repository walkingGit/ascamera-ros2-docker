#!/bin/bash
# Launch all nodes
source /opt/ros/jazzy/setup.bash
source /workspace/ascam_ws/install/setup.bash

# Start depth camera node
ros2 run ascamera ascamera_node --ros-args \
  -p confiPath:=/workspace/ascam_ws/src/ascamera/configurationfiles \
  -p rgb_width:=640 -p rgb_height:=480 \
  -p depth_width:=640 -p depth_height:=480 \
  -p fps:=15 -p color_pcl:=false &
CAM_PID=$!

# Start arm bridge
python3 /workspace/mycobot_bridge.py &
ARM_PID=$!

echo "=== Both nodes started ==="
echo "Depth camera PID: $CAM_PID"
echo "Arm bridge PID: $ARM_PID"
echo ""
echo "Topics available:"
sleep 2
ros2 topic list 2>/dev/null

# Wait for any to exit
wait
