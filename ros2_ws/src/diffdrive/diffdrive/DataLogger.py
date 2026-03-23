import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import message_filters
import csv
import math
from datetime import datetime

class OptimalTrajectoryLogger(Node):
    def __init__(self):
        super().__init__('optimal_trajectory_logger')

        self.ekf_sub = message_filters.Subscriber(self, Odometry, '/odometry/filtered/global')
        self.uwb_sub = message_filters.Subscriber(self, Odometry, '/odometry/uwb')

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.ekf_sub, self.uwb_sub], 
            queue_size=10, 
            slop=0.05
        )
        self.sync.registerCallback(self.synchronized_callback)

        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'optimal_sync_log_{time_str}.csv'
        
        with open(self.filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'EKF_X', 'EKF_Y', 'UWB_X', 'UWB_Y', 'Error', 'Time_Diff'])

        self.get_logger().info(f'Logger started: {self.filename}')

    def synchronized_callback(self, ekf_msg, uwb_msg):
        ex = ekf_msg.pose.pose.position.x
        ey = ekf_msg.pose.pose.position.y
        ux = uwb_msg.pose.pose.position.x
        uy = uwb_msg.pose.pose.position.y
        
        error = math.sqrt((ex - ux)**2 + (ey - uy)**2)
        
        t_ekf = ekf_msg.header.stamp.sec + ekf_msg.header.stamp.nanosec * 1e-9
        t_uwb = uwb_msg.header.stamp.sec + uwb_msg.header.stamp.nanosec * 1e-9
        time_diff = abs(t_ekf - t_uwb)

        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([t_uwb, ex, ey, ux, uy, error, time_diff])

def main():
    rclpy.init()
    node = OptimalTrajectoryLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()