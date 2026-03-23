import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class TransformNode(Node):
    def __init__(self):
        super().__init__('transform_node')
        self.subscription = self.create_subscription(
            PoseStamped,
            '/dwm1001/id_DW878F/pose',
            self.uwb_callback,
            10)
        self.publisher = self.create_publisher(
            PoseStamped,
            'uwb/fix',
            10)
        self.xy_variance = 0.01

    def uwb_callback(self, msg: PoseStamped):
        out_msg = PoseStamped()
        out_msg.header.stamp = msg.header.stamp
        out_msg.header.frame_id = 'map'
        out_msg.pose = msg.pose
        self.publisher.publish(out_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TransformNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()