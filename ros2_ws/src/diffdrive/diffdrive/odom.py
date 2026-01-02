import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf_transformations import quaternion_from_euler
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from motordriver_msgs.msg import MotordriverMessage
import math
import time
import csv

try:
    from .encoder import Encoder
except ImportError:
    from encoder import Encoder

class OdomNode(Node):
    def __init__(self):
        super().__init__('odom_node')

        self.declare_parameter('wheel_radius', 0.0335)
        self.declare_parameter('wheel_base', 0.215)
        self.declare_parameter('ticks_per_revolution_l', 2006)
        self.declare_parameter('ticks_per_revolution_r', 1992)
        
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_base = self.get_parameter('wheel_base').value
        self.ticks_per_revolution_l = self.get_parameter('ticks_per_revolution_l').value
        self.ticks_per_revolution_r = self.get_parameter('ticks_per_revolution_r').value

        self.left_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution_l)
        self.right_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution_r)

        self.odom_x = 0.0
        self.odom_y = 0.0
        self.odom_theta = 0.0

        self.motor_subscriber = self.create_subscription(
            MotordriverMessage, 'motor_data', self.update_encoders_callback, 10)
        self.odom_publisher = self.create_publisher(Odometry, 'wheel/odom', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.prev_time = self.get_clock().now().nanoseconds
        self.update = False
        self.create_timer(0.05, self.timer_callback)

    def update_encoders_callback(self, message):
        self.left_encoder.update(message.encoder1)
        self.right_encoder.update(-message.encoder2)
        self.update = True

    def timer_callback(self):
        if not self.update:
            return
        
        current_time_ns = self.get_clock().now().nanoseconds
        dt = (current_time_ns - self.prev_time) / 1e9
        if dt < 0.0001:
            return
        self.prev_time = current_time_ns

        d_left = self.left_encoder.deltam()
        d_right = self.right_encoder.deltam()

        delta_distance = (d_left + d_right) / 2.0
        delta_theta = (d_right - d_left) / self.wheel_base

        avg_theta = self.odom_theta + (delta_theta / 2.0)
        self.odom_x += delta_distance * math.cos(avg_theta)
        self.odom_y += delta_distance * math.sin(avg_theta)
        self.odom_theta += delta_theta

        linear_v = delta_distance / dt
        angular_v = delta_theta / dt

        self.publish_odom(linear_v, angular_v)
        self.update = False

    def publish_odom(self, vx, vth):
        now = self.get_clock().now().to_msg()
        q = quaternion_from_euler(0.0, 0.0, self.odom_theta)

        odom = Odometry()
        odom.header.stamp = now
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_footprint'
        odom.pose.pose.position.x = self.odom_x
        odom.pose.pose.position.y = self.odom_y
        odom.pose.pose.orientation.x = q[0]
        odom.pose.pose.orientation.y = q[1]
        odom.pose.pose.orientation.z = q[2]
        odom.pose.pose.orientation.w = q[3]
        odom.twist.twist.linear.x = vx
        odom.twist.twist.angular.z = vth
        self.odom_publisher.publish(odom)

        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.odom_x
        t.transform.translation.y = self.odom_y
        t.transform.rotation.x = q[0]
        t.transform.rotation.y = q[1]
        t.transform.rotation.z = q[2]
        t.transform.rotation.w = q[3]
        #self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = OdomNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()