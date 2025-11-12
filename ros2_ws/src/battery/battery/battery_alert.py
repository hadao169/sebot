import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
from std_msgs.msg import Bool, Float32

import lgpio

class BatteryAlert(Node):
    def __init__(self):
        super().__init__('battery_alert_node')

        self.declare_parameter('threshold', 12.0) # Oletusarvo 12.0 V, tämä tulee nopeasti vastaan täydelläkin akulla aloitettaessa.
        self.threshold = self.get_parameter('threshold').get_parameter_value().double_value
        self.get_logger().info(f"Akun jännitteen alaraja asetettu arvoon {self.threshold:.2f} V")
        
        self.sub = self.create_subscription(Float32, '/battery_voltage', self.voltage_callback, 10)
        self.sub_alert = self.create_subscription(Bool, '/battery_alert', self.alert_callback, 10)
        self.pub = self.create_publisher(Bool, '/battery_alert', 10)
        self.previous_alert_state = False

        # Julkaistaan yhden kerran oletuksena /battery_alertissa False, jotta siellä näkyy varmasti jotain.
        battery_alert_msg = Bool()
        battery_alert_msg.data = self.previous_alert_state
        self.pub.publish(battery_alert_msg)
    
        # Määritellään GPIO nasta hälytys-LEDille
        self.LED_PIN = 18
        # Valitaan GPIO-siru (vakio Raspberry Pille)
        self.chip = lgpio.gpiochip_open(4)
        # Asetetaan LED_PIN ulostuloksi
        lgpio.gpio_claim_output(self.chip, self.LED_PIN)
        # Alustetaan LED_PIN alas (nollaksi)
        lgpio.gpio_write(self.chip, self.LED_PIN, 0)
    # Tämä callback kutsutaan kun /battery_alert topiciin tulee viestejä.
    def alert_callback(self, msg):
        if msg.data == True:
            pass
            lgpio.gpio_write(self.chip, self.LED_PIN, 1)  
        else:
            pass
            lgpio.gpio_write(self.chip, self.LED_PIN, 0)  

    def voltage_callback(self, msg):
        if msg.data < self.threshold:
            alert_state = True
        else:
            alert_state = False
        
        if self.previous_alert_state != alert_state: # Julkaistaan /battery_alert tieto vain jos se on muuttunut edellisestä.
            battery_alert_msg = Bool()
            battery_alert_msg.data = alert_state
            self.pub.publish(battery_alert_msg)
            self.previous_alert_state = alert_state

def main(args=None):
  rclpy.init(args=args)
  batteryalert_node = BatteryAlert()
  
  try:
    rclpy.spin(batteryalert_node)
  except KeyboardInterrupt:
    pass

  finally:
      batteryalert_node.destroy_node()
      lgpio.gpio_write(batteryalert_node.chip, batteryalert_node.LED_PIN, 0)
      lgpio.gpiochip_close(batteryalert_node.chip)
      if rclpy.ok():
          rclpy.shutdown()

if __name__ == '__main__':
  main()
