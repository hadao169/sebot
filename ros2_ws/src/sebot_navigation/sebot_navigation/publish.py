import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class UWBGoalPublisher(Node):
    def __init__(self):
        super().__init__('uwb_goal_publisher')
        
        self.publisher_ = self.create_publisher(PoseStamped, '/goal_pose', 10)
        
        self.timer = self.create_timer(1.0, self.publish_callback)
        
        self.get_logger().info('UWB Goal Publisher đã khởi chạy!')
        self.get_logger().info('Đang gửi liên tục điểm đích: x=2.0, y=2.0')

    def publish_callback(self):
        msg = PoseStamped()
        
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'map'

        msg.pose.position.x = 2.0 
        msg.pose.position.y = 2.0
        msg.pose.position.z = 0.0

        msg.pose.orientation.w = 1.0

        self.publisher_.publish(msg)
        
        self.get_logger().info(f'Publishing Goal: x={msg.pose.position.x:.1f}, y={msg.pose.position.y:.1f}')

def main(args=None):
    rclpy.init(args=args)
    node = UWBGoalPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
    