#!/usr/bin/env python3
"""
MyCobot Pro 450 ROS2 bridge node.
Controls the arm via send_coords (preferred) and send_angles.
Exposes topics + services for integration with depth camera.
"""
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose, PoseStamped
from std_msgs.msg import String, Bool
from sensor_msgs.msg import JointState
import time

class MyCobotBridge(Node):
    def __init__(self):
        super().__init__('mycobot_bridge')
        self.mc = None
        self.connected = False

        # --- Publishers (arm state) ---
        self.coord_pub = self.create_publisher(Pose, '/mycobot/coords', 10)
        self.angle_pub = self.create_publisher(JointState, '/mycobot/angles', 10)
        self.gripper_pub = self.create_publisher(String, '/mycobot/gripper', 10)

        # --- Subscribers (arm commands) ---
        # Preferred: send_coords [x,y,z,rx,ry,rz]
        self.create_subscription(Pose, '/mycobot/cmd_coords', self.cmd_coords_cb, 10)
        # Alternative: send_angles [j1..j6]
        self.create_subscription(JointState, '/mycobot/cmd_angles', self.cmd_angles_cb, 10)
        # Gripper: "open", "close", or "50" (angle value)
        self.create_subscription(String, '/mycobot/cmd_gripper', self.cmd_gripper_cb, 10)
        # Go home / safe position
        self.create_subscription(Bool, '/mycobot/cmd_home', self.cmd_home_cb, 10)

        self.connect()
        self.create_timer(0.5, self.publish_status)
        self.get_logger().info('MyCobot bridge ready — send commands to /mycobot/cmd_*')

    def connect(self):
        try:
            from pymycobot import Pro450Client
            self.mc = Pro450Client('192.168.0.232', 4500)
            if self.mc.is_power_on() != 1:
                self.mc.power_on()
            self.connected = True
            self.get_logger().info('MyCobot connected at 192.168.0.232')
        except Exception as e:
            self.get_logger().error(f'MyCobot connect failed: {e}')

    def cmd_coords_cb(self, msg):
        if not self.connected: return
        try:
            coords = [msg.position.x, msg.position.y, msg.position.z,
                      msg.orientation.x, msg.orientation.y, msg.orientation.z]
            self.mc.send_coords(coords, 30)
            self.get_logger().info(f'send_coords: {coords}')
        except Exception as e:
            self.get_logger().error(f'coord move: {e}')

    def cmd_angles_cb(self, msg):
        if not self.connected: return
        try:
            angles = list(msg.position)
            self.mc.send_angles(angles, 30)
            self.get_logger().info(f'send_angles: {angles}')
        except Exception as e:
            self.get_logger().error(f'angle move: {e}')

    def cmd_gripper_cb(self, msg):
        if not self.connected: return
        cmd = msg.data.strip().lower()
        try:
            if cmd == 'open':
                self.mc.set_pro_gripper_open()
            elif cmd == 'close':
                self.mc.set_pro_gripper_close()
            else:
                angle = int(float(cmd))
                self.mc.set_pro_gripper_angle(angle)
            self.get_logger().info(f'gripper: {cmd}')
        except Exception as e:
            self.get_logger().error(f'gripper: {e}')

    def cmd_home_cb(self, msg):
        if not self.connected or not msg.data: return
        try:
            self.mc.send_angles([0, 0, 0, 0, 0, -50], 30)
            self.get_logger().info('going home')
        except Exception as e:
            self.get_logger().error(f'home: {e}')

    def publish_status(self):
        if not self.connected:
            return
        try:
            angles = self.mc.get_angles()
            coords = self.mc.get_coords()
            gripper = self.mc.get_pro_gripper_angle()

            js = JointState()
            js.position = [float(a) for a in angles]
            js.name = ['j1','j2','j3','j4','j5','j6']
            self.angle_pub.publish(js)

            pose = Pose()
            pose.position.x = float(coords[0])
            pose.position.y = float(coords[1])
            pose.position.z = float(coords[2])
            pose.orientation.x = float(coords[3])
            pose.orientation.y = float(coords[4])
            pose.orientation.z = float(coords[5])
            self.coord_pub.publish(pose)

            self.gripper_pub.publish(String(data=str(gripper)))
        except Exception as e:
            pass

def main():
    rclpy.init()
    node = MyCobotBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
