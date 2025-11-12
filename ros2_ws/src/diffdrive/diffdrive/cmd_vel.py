import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import String

import math

class CmdVelNode(Node):
  def __init__(self):
    super().__init__('cmd_vel_node')

    # Lue parametrit
    self.declare_parameter('wheel_radius', 0.1)
    self.declare_parameter('wheel_base', 0.5)
    self.declare_parameter('ticks_per_revolution', 1075)

    # Hae parametrien arvot
    self.wheel_radius = self.get_parameter('wheel_radius').value
    self.wheel_base = self.get_parameter('wheel_base').value
    self.ticks_per_revolution = self.get_parameter('ticks_per_revolution').value

    self.get_logger().info(f'Pyörän säde: {self.wheel_radius}')
    self.get_logger().info(f'Pyörien etäisyys: {self.wheel_base}')
    self.get_logger().info(f'Anturin kierros: {self.ticks_per_revolution}')

    self.cmd_vel_subscriber = self.create_subscription(
        Twist,
        'cmd_vel',
        self.cmd_vel_callback,
        10
    )

    self.mc_publisher = self.create_publisher(
        String,
        'motor_command',
        10
    )

  def mps_to_spd(self,mps):
    # muunnetan m/s moottoriohjaimen spd arvoksi
    pid_freq = 10 # Moottoriohjain päivittyy 10Hz taajuudella

    # kulmanopeus (rad/s)
    radps = mps / self.wheel_radius

    # RPM
    rpm = radps * ( 60 / ( 2 * math.pi ) )
    
    spd = rpm * (self.ticks_per_revolution / 60 / pid_freq)
    return spd

  def cmd_vel_callback(self, msg):
    # mps_l = vasen rengas m/s
    # mps_r = oikea rengas m/s
    mps_l = +(msg.linear.x + (msg.angular.z * self.wheel_base / 2.0))
    mps_r = -(msg.linear.x - (msg.angular.z * self.wheel_base / 2.0))

    string_msg = String()
    string_msg.data = "SPD;%i;%i;"%(self.mps_to_spd(mps_l), self.mps_to_spd(mps_r))
    
    self.mc_publisher.publish(string_msg)

def main(args=None):
  rclpy.init(args=args)

  cmdvel_node = CmdVelNode()

  try:
    rclpy.spin(cmdvel_node)
  except KeyboardInterrupt:
    pass
  finally:
    cmdvel_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()
