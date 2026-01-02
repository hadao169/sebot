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

class OdomImuNode(Node):
    def __init__(self):
        super().__init__('odom_node')

        # Khai báo tham số (Sửa lỗi dấu phẩy ở wheel_base: 0,215 -> 0.215)
        self.declare_parameter('wheel_radius', 0.0335)
        self.declare_parameter('wheel_base', 0.215)
        self.declare_parameter('ticks_per_revolution_l', 2006)
        self.declare_parameter('ticks_per_revolution_r', 1992)
        
        self.wheel_radius = self.get_parameter('wheel_radius').value
        self.wheel_base = self.get_parameter('wheel_base').value
        self.ticks_per_revolution_l = self.get_parameter('ticks_per_revolution_l').value
        self.ticks_per_revolution_r = self.get_parameter('ticks_per_revolution_r').value

        self.left_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution_l)
        self.right_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution_r)

        self.odom_x = 0.0
        self.odom_y = 0.0
        self.odom_theta = 0.0
        
        # Biến để xử lý mốc 0 ban đầu cho IMU
        self.initial_yaw = None
        self.current_corrected_yaw = 0.0
        
        self.imu_data = Imu()
        self.imu_data.orientation.w = 1.0 

        self.motor_subscriber = self.create_subscription(MotordriverMessage, 'motor_data', self.update_encoders_callback, 10)
        self.imu_subscriber = self.create_subscription(Imu, 'imu/data', self.imu_callback, 10)
        self.odom_publisher = self.create_publisher(Odometry, 'wheel/odom_imu', 10)
        self.tf_broadcaster = TransformBroadcaster(self)

        self.prev_time = self.get_clock().now()
        self.create_timer(0.02, self.timer_callback) # Tăng tần suất lên 50Hz để mượt hơn
        self.update = False

    def update_encoders_callback(self, message):
        self.left_encoder.update(message.encoder1)
        self.right_encoder.update(-message.encoder2)
        self.update = True

    def imu_callback(self, msg: Imu):
        quat = [msg.orientation.x, msg.orientation.y, msg.orientation.z, msg.orientation.w]
        _, _, raw_yaw = euler_from_quaternion(quat)
        
        if self.initial_yaw is None:
            self.initial_yaw = raw_yaw
            self.get_logger().info(f'Set Initial Yaw: {math.degrees(self.initial_yaw):.2f} deg')
        
        self.current_corrected_yaw = raw_yaw - self.initial_yaw
        self.imu_data = msg
        self.update = True

    def timer_callback(self):    
        if not self.update or self.initial_yaw is None: return
        self.update = False
        
        current_time = self.get_clock().now()
        dt = (current_time - self.prev_time).nanoseconds / 1e9
        self.prev_time = current_time

        d_left = self.left_encoder.deltam()
        d_right = self.right_encoder.deltam()
        delta_distance = (d_left + d_right) / 2.0

        new_theta = self.current_corrected_yaw

        # Tích phân Runge-Kutta 2 (Dùng trung bình góc cũ và mới)
        avg_theta = self.odom_theta + (new_theta - self.odom_theta) / 2.0
        
        if delta_distance != 0:
            self.odom_x += delta_distance * math.cos(avg_theta)
            self.odom_y += delta_distance * math.sin(avg_theta)
        
        self.odom_theta = new_theta

        linear_x = delta_distance / dt 
        linear_y = 0.0
        angular_z = self.imu_data.angular_velocity.z

        self.publish_data(current_time, linear_x, linear_y, angular_z)

    def publish_data(self, time, vx, vy, vth):
        now = time.to_msg()
        q = quaternion_from_euler(0.0, 0.0, self.odom_theta)

        # Odometry
        odom_msg = Odometry()
        odom_msg.header.stamp = now
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'
        odom_msg.pose.pose.position.x = self.odom_x
        odom_msg.pose.pose.position.y = self.odom_y
        odom_msg.pose.pose.orientation = q
        
        odom_msg.twist.twist.linear.x = vx
        odom_msg.twist.twist.linear.y = vy
        odom_msg.twist.twist.angular.z = vth
        self.odom_publisher.publish(odom_msg)

        # TF
        t = TransformStamped()
        t.header.stamp = now
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_footprint'
        t.transform.translation.x = self.odom_x
        t.transform.translation.y = self.odom_y
        t.transform.rotation.x, t.transform.rotation.y, \
        t.transform.rotation.z, t.transform.rotation.w = q
        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = OdomImuNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()