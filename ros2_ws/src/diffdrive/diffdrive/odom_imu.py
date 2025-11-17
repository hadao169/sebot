import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from tf_transformations import euler_from_quaternion, quaternion_from_euler 
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster
from sensor_msgs.msg import Imu
from motordriver_msgs.msg import MotordriverMessage
import math

try:
    from .encoder import Encoder
except ImportError:
    from encoder import Encoder


class OdomNode(Node):
  def __init__(self):
    super().__init__('odom_node')

    self.declare_parameter('wheel_radius', 0.1)
    self.declare_parameter('wheel_base', 0.5)
    self.declare_parameter('ticks_per_revolution', 1075)

    self.wheel_radius = self.get_parameter('wheel_radius').value
    self.wheel_base = self.get_parameter('wheel_base').value
    self.ticks_per_revolution = self.get_parameter('ticks_per_revolution').value

    self.get_logger().info(f'Wheel radius: {self.wheel_radius}')
    self.get_logger().info(f'Wheel distance: {self.wheel_base}')
    self.get_logger().info(f'Sensor revolution: {self.ticks_per_revolution}')

    self.left_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution)
    self.right_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution)

    self.odom_theta = 0.0
    self.odom_x = 0.0
    self.odom_y = 0.0
    
    self.imu_data = Imu()
    self.imu_data.orientation.w = 1.0 

    self.motor_subscriber = self.create_subscription(
        MotordriverMessage,
        'moto_data',
        self.update_encoders_callback,
        10
    )

    self.imu_subscriber = self.create_subscription(
        Imu,
        'imu/data', 
        self.imu_callback,
        10
    )

    self.odom_publisher = self.create_publisher(
        Odometry,
        'odom', 
        10
    )

    self.tf_broadcaster = TransformBroadcaster(self)

    self.prev_time = self.get_clock().now().nanoseconds

    timer_period = 0.02 
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.update = True

  def update_encoders_callback(self, message):
    self.left_encoder.update(message.encoder1)
    self.right_encoder.update(-message.encoder2)
    self.update = True

  def imu_callback(self, msg: Imu):
    self.imu_data = msg

  def timer_callback(self):
    if not self.update: return
    self.update = False
    
    current_time = self.get_clock().now().nanoseconds
    elapsed = (current_time - self.prev_time) / 1000000000
    self.prev_time = current_time

    d_left= self.left_encoder.deltam()
    d_right = self.right_encoder.deltam()

    delta_distance = (d_left + d_right) / 2.0

    q = self.imu_data.orientation
    
    (roll, pitch, imu_yaw) = euler_from_quaternion([q.x, q.y, q.z, q.w])

    delta_theta = imu_yaw - self.odom_theta 
    
    self.odom_theta = imu_yaw 
    
    if delta_distance != 0:
      robot_x = math.cos( self.odom_theta ) * delta_distance
      robot_y = math.sin( self.odom_theta ) * delta_distance 
      
      self.odom_x += robot_x
      self.odom_y += robot_y

    linear_x = delta_distance / elapsed 
    linear_y = 0.0 
    
    angular_z = self.imu_data.angular_velocity.z

    odom_msg = Odometry()
    odom_msg.header.stamp = self.get_clock().now().to_msg()
    odom_msg.header.frame_id = 'odom'
    odom_msg.child_frame_id = 'base_footprint'

    odom_msg.pose.pose.position.x = self.odom_x 
    odom_msg.pose.pose.position.y = self.odom_y 
    odom_msg.pose.pose.position.z = 0.0

    odom_msg.pose.pose.orientation = self.imu_data.orientation

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

    t.transform.rotation = self.imu_data.orientation 

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