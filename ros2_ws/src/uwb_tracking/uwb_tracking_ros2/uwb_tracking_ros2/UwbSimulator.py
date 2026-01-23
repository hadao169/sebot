import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Imu
import math
import time
import random

class RawSensorSim(Node):
    def __init__(self):
        super().__init__('raw_sensor_sim')
        
        # Publishers
        self.uwb_pub = self.create_publisher(PoseStamped, '/dwm1001/DW878F/pose', 10)
        self.odom_pub = self.create_publisher(Odometry, 'wheel/odom', 10)
        self.imu_pub = self.create_publisher(Imu, 'imu/data', 10)
        
        self.timer_period = 0.01 
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.uwb_ox = 1.5 
        self.uwb_oy = 2.0
        self.uwb_yaw_offset = math.radians(15.0)

        self.odom_x = 0.0
        self.odom_y = 0.0
        self.odom_theta = 0.0
        
        self.start_time = time.time()
        self.prev_time = self.get_clock().now().nanoseconds

    def timer_callback(self):
        current_time_ns = self.get_clock().now().nanoseconds
        elapsed = (current_time_ns - self.prev_time) / 1e9
        self.prev_time = current_time_ns
        total_time = time.time() - self.start_time

        # Điều khiển giả lập
        v = 0.4
        omega = 0.3 * math.sin(0.5 * total_time)
        
        delta_s = v * elapsed
        delta_theta = omega * elapsed

        # 1. Cập nhật trạng thái thực (Ground Truth) của Robot trong hệ tọa độ UWB
        # Giả sử Robot di chuyển trong hệ tọa độ của Anchor UWB ngay từ đầu
        self.uwb_ox += delta_s * math.cos(self.uwb_yaw_offset + delta_theta/2.0)
        self.uwb_oy += delta_s * math.sin(self.uwb_yaw_offset + delta_theta/2.0)
        self.uwb_yaw_offset += delta_theta

        # 2. Cập nhật Odom (Luôn bắt đầu từ 0, không quan tâm vị trí thực)
        self.odom_x += delta_s * math.cos(self.odom_theta + delta_theta/2.0)
        self.odom_y += delta_s * math.sin(self.odom_theta + delta_theta/2.0)
        self.odom_theta += delta_theta

        now = self.get_clock().now().to_msg()

        # Publish UWB (Vị trí thực trong hệ UWB + Nhiễu)
        uwb_msg = PoseStamped()
        uwb_msg.header.stamp = now
        uwb_msg.header.frame_id = "uwb_map"
        uwb_msg.pose.position.x = self.uwb_ox + random.gauss(0, 0.05)
        uwb_msg.pose.position.y = self.uwb_oy + random.gauss(0, 0.05)
        self.uwb_pub.publish(uwb_msg)

        # Publish Odom Raw
        odom_msg = Odometry()
        odom_msg.header.stamp = now
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'
        odom_msg.pose.pose.position.x = self.odom_x
        odom_msg.pose.pose.position.y = self.odom_y
        odom_msg.pose.pose.orientation.z = math.sin(self.odom_theta / 2.0)
        odom_msg.pose.pose.orientation.w = math.cos(self.odom_theta / 2.0)
        self.odom_pub.publish(odom_msg)

        # Publish IMU Raw (Heading thực tế của Robot)
        imu_msg = Imu()
        imu_msg.header.stamp = now
        imu_msg.header.frame_id = 'base_footprint'
        imu_msg.orientation.z = math.sin(self.uwb_yaw_offset / 2.0)
        imu_msg.orientation.w = math.cos(self.uwb_yaw_offset / 2.0)
        imu_msg.angular_velocity.z = omega
        self.imu_pub.publish(imu_msg)

def main(args=None):
    rclpy.init(args=args)
    node = RawSensorSim()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()