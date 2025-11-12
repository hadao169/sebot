import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from motordriver_msgs.msg import MotordriverMessage

import time

class SimplePublisher(Node):
    def __init__(self):
        super().__init__('simple_publisher')  # Name the node 'simple_publisher'
        self.publisher_ = self.create_publisher(String, 'motor_command', 10)  # Create publisher on 'topic' with queue size of 10

        self.subscriber = self.create_subscription(
            MotordriverMessage,
            'motor_data',
            self.setspeed_callback,
            10
        )

        self.offset1 = ""
        self.offset2 = ""

        self.encoder1 = 0
        self.encoder2 = 0

        self.target1 = 1130*20
        self.target2 = 1020*20

        msg = String()
        msg.data = 'ZERO;'
        self.publisher_.publish(msg)
        time.sleep(2)
 
    def setspeed_callback(self, message):    
        if self.offset1 == "":
            self.offset1 = message.encoder1
            self.offset2 = message.encoder2

        self.encoder1 = message.encoder1-self.offset1
        self.encoder2 = message.encoder2-self.offset2

        error1 = (self.encoder1 - self.target1)*0.4
        error2 = (self.encoder2 - self.target2)*0.4

        if error1 >  259: error1 =  250
        if error1 < -250: error1 = -250

        if error2 >  259: error2 =  250
        if error2 < -250: error2 = -250

        msg = String()
        msg.data = 'SPD;%s;%s;'%(error1,error2)
        self.publisher_.publish(msg)
 

    def publish_message(self):
        msg = String()
        msg.data = 'SPD;144;130;'
        self.publisher_.publish(msg)
        self.get_logger().info(f'Publishing: "{msg.data}"')


def main(args=None):
    rclpy.init(args=args)

    simple_publisher = SimplePublisher()

    #simple_publisher.publish_message()
    rclpy.spin(simple_publisher)

    simple_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
