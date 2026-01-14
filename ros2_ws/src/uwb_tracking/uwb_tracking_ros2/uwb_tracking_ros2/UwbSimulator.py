# import rclpy
# from rclpy.node import Node
# from nav_msgs.msg import Odometry
# from geometry_msgs.msg import PoseStamped
# from sensor_msgs.msg import Imu
# import math
# import time
# import random

# class StraightLineKinematicSim(Node):
#     def __init__(self):
#         super().__init__('straight_line_kinematic_sim')
        
#         self.uwb_pub = self.create_publisher(PoseStamped, '/dwm1001/DW878F/pose', 10)
#         self.odom_pub = self.create_publisher(Odometry, 'wheel/odom', 10)
#         self.imu_pub = self.create_publisher(Imu, 'imu/data', 10)
        
#         self.wheel_base = 0.215
#         self.timer_period = 0.01 
#         self.timer = self.create_timer(self.timer_period, self.timer_callback)

#         self.x = 5.0
#         self.y = 2.0
#         self.theta = 0.0
        
#         self.x0 = 0.0
#         self.y0 = 0.0
        
#         self.prev_time = self.get_clock().now().nanoseconds

#     def timer_callback(self):
#         current_time_ns = self.get_clock().now().nanoseconds
#         elapsed = (current_time_ns - self.prev_time) / 1e9
#         self.prev_time = current_time_ns

#         v = 0.2
#         d_left = v * elapsed
#         d_right = v * elapsed
        
#         delta_distance = (d_left + d_right) / 2.0
#         delta_theta = (d_right - d_left) / self.wheel_base

#         if delta_distance != 0 or delta_theta != 0:
#             self.x += delta_distance * math.cos(self.theta + delta_theta / 2.0)
#             self.y += delta_distance * math.sin(self.theta + delta_theta / 2.0)
            
#             self.x0 += delta_distance * math.cos(self.theta + delta_theta / 2.0)
#             self.y0 += delta_distance * math.sin(self.theta + delta_theta / 2.0)
            
#             self.theta += delta_theta

#         now = self.get_clock().now().to_msg()

#         uwb_msg = PoseStamped()
#         uwb_msg.header.stamp = now
#         uwb_msg.header.frame_id = "uwb_map"
#         uwb_msg.pose.position.x = self.x + random.gauss(0, 0.05)
#         uwb_msg.pose.position.y = self.y + random.gauss(0, 0.05)
#         uwb_msg.pose.position.z = 0.0
#         self.uwb_pub.publish(uwb_msg)

#         odom_msg = Odometry()
#         odom_msg.header.stamp = now
#         odom_msg.header.frame_id = 'odom'
#         odom_msg.child_frame_id = 'base_footprint'
#         odom_msg.pose.pose.position.x = self.x0
#         odom_msg.pose.pose.position.y = self.y0
#         odom_msg.pose.pose.position.z = 0.0
        
#         odom_msg.pose.pose.orientation.w = math.cos(self.theta / 2.0)
#         odom_msg.pose.pose.orientation.x = 0.0
#         odom_msg.pose.pose.orientation.y = 0.0
#         odom_msg.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        
#         odom_msg.twist.twist.linear.x = v
#         odom_msg.twist.twist.angular.z = 0.0
#         self.odom_pub.publish(odom_msg)

#         imu_msg = Imu()
#         imu_msg.header.stamp = now
#         imu_msg.header.frame_id = 'base_footprint'
#         imu_msg.orientation.w = math.cos(self.theta / 2.0)
#         imu_msg.orientation.x = 0.0
#         imu_msg.orientation.y = 0.0
#         imu_msg.orientation.z = math.sin(self.theta / 2.0)
#         imu_msg.angular_velocity.z = 0.0
#         self.imu_pub.publish(imu_msg)

# def main(args=None):
#     rclpy.init(args=args)
#     node = StraightLineKinematicSim()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
from sensor_msgs.msg import Imu
import math
import time
import random

class StraightLineKinematicSim(Node):
    def __init__(self):
        super().__init__('straight_line_kinematic_sim')
        
        self.uwb_pub = self.create_publisher(PoseStamped, '/dwm1001/DW878F/pose', 10)
        self.odom_pub = self.create_publisher(Odometry, 'wheel/odom', 10)
        self.imu_pub = self.create_publisher(Imu, 'imu/data', 10)
        
        self.wheel_base = 0.215
        self.timer_period = 0.01 
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        self.x = 5.0
        self.y = 2.0
        self.theta = 0.0
        
        self.x0 = 0.0
        self.y0 = 0.0
        
        self.start_time = time.time()
        self.prev_time = self.get_clock().now().nanoseconds

    def timer_callback(self):
        current_time_ns = self.get_clock().now().nanoseconds
        elapsed = (current_time_ns - self.prev_time) / 1e9
        self.prev_time = current_time_ns
        
        total_time = time.time() - self.start_time

        v = 0.3
        omega = 0.5 * math.sin(0.5 * total_time)
        
        d_left = (v - (omega * self.wheel_base / 2.0)) * elapsed
        d_right = (v + (omega * self.wheel_base / 2.0)) * elapsed
        
        delta_distance = (d_left + d_right) / 2.0
        delta_theta = (d_right - d_left) / self.wheel_base

        if delta_distance != 0 or delta_theta != 0:
            self.x += delta_distance * math.cos(self.theta + delta_theta / 2.0)
            self.y += delta_distance * math.sin(self.theta + delta_theta / 2.0)
            
            self.x0 += delta_distance * math.cos(self.theta + delta_theta / 2.0)
            self.y0 += delta_distance * math.sin(self.theta + delta_theta / 2.0)
            
            self.theta += delta_theta

        now = self.get_clock().now().to_msg()

        uwb_msg = PoseStamped()
        uwb_msg.header.stamp = now
        uwb_msg.header.frame_id = "uwb_map"
        uwb_msg.pose.position.x = self.x + random.gauss(0, 0.05)
        uwb_msg.pose.position.y = self.y + random.gauss(0, 0.05)
        uwb_msg.pose.position.z = 0.0
        self.uwb_pub.publish(uwb_msg)

        odom_msg = Odometry()
        odom_msg.header.stamp = now
        odom_msg.header.frame_id = 'odom'
        odom_msg.child_frame_id = 'base_footprint'
        odom_msg.pose.pose.position.x = self.x0
        odom_msg.pose.pose.position.y = self.y0
        odom_msg.pose.pose.position.z = 0.0
        
        odom_msg.pose.pose.orientation.w = math.cos(self.theta / 2.0)
        odom_msg.pose.pose.orientation.x = 0.0
        odom_msg.pose.pose.orientation.y = 0.0
        odom_msg.pose.pose.orientation.z = math.sin(self.theta / 2.0)
        
        odom_msg.twist.twist.linear.x = v
        odom_msg.twist.twist.angular.z = omega
        self.odom_pub.publish(odom_msg)

        imu_msg = Imu()
        imu_msg.header.stamp = now
        imu_msg.header.frame_id = 'base_footprint'
        imu_msg.orientation.w = math.cos(self.theta / 2.0)
        imu_msg.orientation.x = 0.0
        imu_msg.orientation.y = 0.0
        imu_msg.orientation.z = math.sin(self.theta / 2.0)
        imu_msg.angular_velocity.z = omega
        self.imu_pub.publish(imu_msg)

def main(args=None):
    rclpy.init(args=args)
    node = StraightLineKinematicSim()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()