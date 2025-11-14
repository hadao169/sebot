import rclpy
from rclpy.node import Node
from geometry_msgs.msg import QuaternionStamped
from geometry_msgs.msg import Vector3Stamped
from sensor_msgs.msg import Imu

class ImuIntegrationNode(Node):
  def __init__(self):
    super().__init__("imu_listener_node")
    self.quaternion = None
    self.angular_vel = None

    self.imu_quaternion_sub = self.create_subscription(
      QuaternionStamped,
      'filter/quaternion',
      self.quaternion_callback,
      10
    )

    self.imu_angularVelocity_sub = self.create_subscription(
      Vector3Stamped,
      "imu/angular_velocity",
      self.angular_vel_callback,
      10
    )

    self.imu_data_pub = self.create_publisher(
      Imu,
      "imu_data",
      10
    )

    timer_period = 0.01  # Sekuntia
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.get_logger().info("ImuIntegrationNode initialized.")

  def timer_callback(self):
    imu_data = Imu()
    imu_data.orientation = self.quaternion
    imu_data.angular_velocity = self.angular_vel
    self.imu_data_pub.publish(imu_data)

  def quaternion_callback(self, msg: QuaternionStamped):
    self.quaternion = msg.quaternion

  def angular_vel_callback(self, msg: Vector3Stamped):
    self.angular_vel = msg.vector


def main(args=None):
  rclpy.init(args=args)

  imu_integrator = ImuIntegrationNode()

  try:
    rclpy.spin(imu_integrator)
  except KeyboardInterrupt:
    pass
  finally:
    imu_integrator.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
  main()