import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf_transformations import quaternion_from_euler
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from motordriver_msgs.msg import MotordriverMessage
import math
import numpy as np
import matplotlib.pyplot as plt
import time
import csv
import os

try:
    from .encoder import Encoder
except:
    from encoder import Encoder


class OdomNode(Node):
  def __init__(self):
    super().__init__('odom_node')

    self.declare_parameter('wheel_radius', 0.0335)
    self.declare_parameter('wheel_base', 0.215)
    self.declare_parameter('ticks_per_revolution_l', 2006)
    self.declare_parameter('ticks_per_revolution_r', 1992)
    
    # Hae parametrien arvot
    self.wheel_radius = self.get_parameter('wheel_radius').value
    self.wheel_base = self.get_parameter('wheel_base').value
    self.ticks_per_revolution_l = self.get_parameter('ticks_per_revolution_l').value
    self.ticks_per_revolution_r = self.get_parameter('ticks_per_revolution_r').value

    self.get_logger().info(f'Wheel radius: {self.wheel_radius}')
    self.get_logger().info(f'Wheel distance: {self.wheel_base}')
    # self.get_logger().info(f'Sensor revolution: {self.ticks_per_revolution}')

    self.left_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution_l)
    self.right_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution_r)

    self.odom_theta = 0.0
    self.odom_x = 0.0
    self.odom_y = 0.0

    self.motor_subscriber = self.create_subscription(
        MotordriverMessage,
        'motor_data',
        self.update_encoders_callback,
        10
    )

    self.odom_publisher = self.create_publisher(
        Odometry,
        'wheel/odom',
        10
    )

    self.tf_broadcaster = TransformBroadcaster(self)

    self.prev_time = self.get_clock().now().nanoseconds

    timer_period = 0.1
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.update = True
    
    # === THÊM LOGIC GHI FILE ===
    self.log_filename = None
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        self.log_filename = f'odom_log_{timestamp}.csv'
        with open(self.log_filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'odom_x', 'odom_y', 'odom_theta', 'ticks_L', 'ticks_R', 'delta_d', 'cumulative_d'])
        self.get_logger().info(f"Logging odometry data to {self.log_filename}")
    except Exception as e:
        self.get_logger().error(f"Failed to initialize CSV file: {e}")
        self.log_filename = None

  def update_encoders_callback(self, message):
    self.left_encoder.update(message.encoder1)
    self.right_encoder.update(-message.encoder2)
    self.update = True

  def get_encoder(self):
    encoder1 = self.left_encoder.encoder
    encoder2 = self.right_encoder.encoder
    d_left= self.left_encoder.deltam()
    d_right = self.right_encoder.deltam()
    delta_distance = (d_left + d_right) / 2.0
    return encoder1, encoder2, delta_distance, d_left, d_right


  def timer_callback(self):

    if not self.update: return
    self.update = False
    current_time = self.get_clock().now().nanoseconds
    elapsed = (current_time - self.prev_time)/1000000000
    self.prev_time = current_time

    d_left= self.left_encoder.deltam()
    d_right = self.right_encoder.deltam()

    delta_distance = (d_left + d_right) / 2.0
    delta_theta = (d_right - d_left) / self.wheel_base

    if delta_distance != 0:
      robot_x = math.cos( delta_theta ) * delta_distance
      robot_y = -math.sin( delta_theta ) * delta_distance
      self.odom_x += ( math.cos( self.odom_theta ) * robot_x - math.sin( self.odom_theta ) * robot_y )
      self.odom_y += ( math.sin( self.odom_theta ) * robot_x + math.cos( self.odom_theta ) * robot_y )

    linear_y = delta_distance * math.cos(self.odom_theta) / elapsed
    linear_x = delta_distance * math.sin(self.odom_theta) / elapsed
    angular_z = delta_theta / elapsed

    self.odom_theta += delta_theta
    self.odom_theta = math.atan2(math.sin(self.odom_theta), math.cos(self.odom_theta)) # Giữ góc trong [-pi, pi]

    # === LOGIC GHI FILE ===
    if self.log_filename:
        current_time_sec = current_time / 1e9
        cumulative_d = math.sqrt(self.odom_x**2 + self.odom_y**2)
        try:
            with open(self.log_filename, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    current_time_sec,
                    self.odom_x,
                    self.odom_y,
                    self.odom_theta,
                    self.left_encoder.encoder,
                    self.right_encoder.encoder,
                    delta_distance,
                    cumulative_d
                ])
        except Exception as e:
            pass # Không thêm get_logger()
    # ======================

    odom_msg = Odometry()
    odom_msg.header.stamp = self.get_clock().now().to_msg()
    odom_msg.header.frame_id = 'odom'
    odom_msg.child_frame_id = 'base_footprint'

    odom_msg.pose.pose.position.x = self.odom_x
    odom_msg.pose.pose.position.y = self.odom_y
    odom_msg.pose.pose.position.z = 0.0

    quat = quaternion_from_euler(0.0, 0.0, self.odom_theta)
    odom_msg.pose.pose.orientation.x = quat[0]
    odom_msg.pose.pose.orientation.y = quat[1]
    odom_msg.pose.pose.orientation.z = quat[2]
    odom_msg.pose.pose.orientation.w = quat[3]

    odom_msg.twist.twist.linear.x = linear_x
    odom_msg.twist.twist.linear.y = linear_y
    odom_msg.twist.twist.angular.z = angular_z

    self.odom_publisher.publish(odom_msg)

    t = TransformStamped()
    t.header.stamp = self.get_clock().now().to_msg()
    t.header.frame_id = 'odom'
    t.child_frame_id = 'base_footprint'

    t.transform.translation.x = self.odom_x
    t.transform.translation.y = self.odom_y
    t.transform.translation.z = 0.0

    t.transform.rotation.z = quat[2]
    t.transform.rotation.w = quat[3]

    self.tf_broadcaster.sendTransform(t)
      

def main(args=None):
  rclpy.init(args=args)

  odom_node = OdomNode()

  try:
    rclpy.spin(odom_node)
  except KeyboardInterrupt:
    pass
  finally:
    odom_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()