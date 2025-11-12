import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import serial
import time

from motordriver_msgs.msg import MotordriverMessage

try:
  from .simserial import SimSerial
except:
  from simserial import SimSerial

class MotordriverNode(Node):
  def __init__(self):
    super().__init__('motordriver_node')

    self.msg = "x\n"
    self.timercount = 0

    # jos simulation parametria ei löydy niin oletuksena se on True
    self.declare_parameter('simulation', True)
    self.simulation = self.get_parameter('simulation').value
    self.get_logger().info(f'Käynnistetään motor_controller simulaatiossa: {self.simulation}. Voit muuttaa tämän parametriä ajamalla: ros2 run motordriver motordriver --ros-args -p simulation:=[False/True]')
    if self.simulation:
      self.arduino = SimSerial()
    else:
      self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
      if not self.arduino.isOpen():
        raise Exception("Ei yhteyttä moottoriohjaimeen")

    self.subscriber = self.create_subscription(
        String,
        'motor_command',
        self.motor_command_callback,
        10
    )

    self.publisher = self.create_publisher(
        MotordriverMessage,
        'motor_data',
        10
    )

    timer_period = 0.01  # Sekuntia
    self.timer = self.create_timer(timer_period, self.timer_callback)

  def timer_callback(self):
    # Luodaan viesti
    if self.msg != "x\n":
        self.arduino.write(self.msg.encode())
    

    if self.timercount == 11:
        if self.msg == "x\n":
            self.arduino.write(self.msg.encode())
        self.msg = "x\n"

        self.timercount = 0
        if self.arduino.inWaiting()>0:
          while self.arduino.inWaiting()>0: 
            answer=self.arduino.readline().decode("utf8").split(";")
          msg = MotordriverMessage()

          try:
            msg.encoder1 = int(answer[0])
            msg.encoder2 = int(answer[1])
            msg.speed1 = int(answer[2])
            msg.speed2 = int(answer[3])
            msg.pwm1 = int(answer[4])
            msg.pwm2 = int(answer[5])

            # Julkaistaan viesti
            self.publisher.publish(msg)
          except Exception as err:
            pass

    self.timercount += 1

  def motor_command_callback(self, message):
    self.msg = "%s\n"%(message.data)

def main(args=None):
  rclpy.init(args=args)
  motordriver_node = MotordriverNode()
  try:
    rclpy.spin(motordriver_node)
  except KeyboardInterrupt:
    pass
  finally:
    motordriver_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()

