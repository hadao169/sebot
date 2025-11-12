import rclpy
from rclpy.node import Node
import time
import lgpio

# Define GPIO pin
LED_PIN = 23

# Open GPIO chip (default for Raspberry Pi)
chip = lgpio.gpiochip_open(4)

# Set the LED pin as output
lgpio.gpio_claim_output(chip, LED_PIN)


class NodeChecker(Node):
    def __init__(self):
        super().__init__('node_checker')

    def get_running_nodes(self):
        # Get all available nodes
        node_names_and_namespaces = self.get_node_names_and_namespaces()
        nodes = [name for name, _ in node_names_and_namespaces]
        return nodes


def main():
    rclpy.init()
    node = NodeChecker()

    active = False

    lgpio.gpio_write(chip, LED_PIN, 0)

    try:
      while True:
  
#        while not active:
        
          nodes = node.get_running_nodes()
          check_nodes = ['robot_state_publisher', 'motordriver_node', 'odom_node', 'cmd_vel_node']
          active = set(check_nodes).issubset(set(nodes))
      
          if active:
              lgpio.gpio_write(chip, LED_PIN, 1)
  
          else:
              lgpio.gpio_write(chip, LED_PIN, 0)
  
          time.sleep(1)

    except KeyboardInterrupt:
      pass
    finally:
      lgpio.gpio_write(chip, LED_PIN, 0)

      node.destroy_node()
      if rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main()


