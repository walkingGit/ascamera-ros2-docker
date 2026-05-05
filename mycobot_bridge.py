#!/usr/bin/env python3
"""
MyCobot Pro 450 ROS2 bridge node.
Exposes arm control via ROS2 services and topics.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, Point
from std_msgs.msg import String, Float32
from sensor_msgs.msg import JointState
import time, threading

class MyCobotBridge(Node):
    def __init__(self):
        super().__init__('mycobot_bridge')
        
        self.mc = None
        self.connected = False
        
        # Publishers
        self.coord_pub = self.create_publisher(Pose, '/mycobot/coords', 10)
        self.angle_pub = self.create_publisher(JointState, '/mycobot/angles', 10)
        self.status_pub = self.create_publisher(String, '/mycobot/status', 10)
        
        # Subscribers
        self.create_subscription(Pose, '/mycobot/cmd_coords', self.cmd_coords_cb, 10)
        self.create_subscription(String, '/mycobot/cmd_gripper', self.cmd_gripper_cb, 10)
        self.create_subscription(JointState, '/mycobot/cmd_angles', self.cmd_angles_cb, 10)
        
        # Connect to arm
        self.connect()
        
        # Status timer
        self.create_timer(1.0, self.publish_status)
        
    def connect(self):
        try:
            from pymycobot import Pro450Client
            self.mc = Pro450Client('192.168.0.232', 4500)
            if self.mc.is_power_on() != 1:
                self.mc.power_on()
            self.connected = True
            self.get_logger().info('MyCobot connected!')
        except Exception as e:
            self.get_logger().error(f'Connect failed: {e}')
    
    def cmd_coords_cb(self, msg):
        if not self.connected: return
        try:
            coords = [msg.position.x, msg.position.y, msg.position.z,
                      msg.orientation.x, msg.orientation.y, msg.orientation.z]
            self.mc.send_coords(coords, 30)
            self.get_logger().info(f'Move to coords: {coords}')
        except Exception as e:
            self.get_logger().error(f'Coord move failed: {e}')
    
    def cmd_angles_cb(self, msg):
        if not self.connected: return
        try:
            self.mc.send_angles(list(msg.position), 30)
            self.get_logger().info(f'Move to angles: {msg.position}')
        except Exception as e:
            self.get_logger().error(f'Angle move failed: {e}')
    
    def cmd_gripper_cb(self, msg):
        if not self.connected: return
        cmd = msg.data.lower()
        try:
            if cmd == 'open':
                self.mc.set_pro_gripper_open()
            elif cmd == 'close':
                self.mc.set_pro_gripper_close()
            elif cmd.startswith('angle'):
                angle = float(cmd.split()[1])
                self.mc.set_pro_gripper_angle(angle)
            self.get_logger().info(f'Gripper: {cmd}')
        except Exception as e:
            self.get_logger().error(f'Gripper failed: {e}')
    
    def publish_status(self):
        if not self.connected:
            self.status_pub.publish(String(data='disconnected'))
            return
        try:
            angles = self.mc.get_angles()
            coords = self.mc.get_coords()
            gripper = self.mc.get_pro_gripper_angle()
            
            js = JointState()
            js.position = [float(a) for a in angles]
            self.angle_pub.publish(js)
            
            pose = Pose()
            pose.position.x = coords[0]
            pose.position.y = coords[1]
            pose.position.z = coords[2]
            pose.orientation.x = coords[3]
            pose.orientation.y = coords[4]
            pose.orientation.z = coords[5]
            self.coord_pub.publish(pose)
            
            msg = String()
            msg.data = f'angles={angles} gripper={gripper}'
            self.status_pub.publish(msg)
        except Exception as e:
            self.get_logger().error(f'Status failed: {e}')

def main():
    rclpy.init()
    node = MyCobotBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
