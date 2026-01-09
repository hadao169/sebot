import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import PoseStamped
import math
import csv
from datetime import datetime
import numpy as np

class DataLoggerNode(Node):
    def __init__(self):
        super().__init__('data_logger_node')

        self.encoder_sub = self.create_subscription(Odometry, "/wheel/odom", self.encoder_callback, 10)
        self.uwb_sub = self.create_subscription(PoseStamped, "/dwm1001/id_DW878F/pose_ls", self.uwb_callback, 10)

        self.enc_x, self.enc_y = 0.0, 0.0
        self.uwb_x, self.uwb_y = 0.0, 0.0
        
        self.theta = 0
        self.Tx = 1.36
        self.Ty = 2.0
               
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filename = f'pos_data_{time_str}.csv'
        self.init_csv()
        self.get_logger().info(f'Log to: {self.filename}')

    def init_csv(self):
        with open(self.filename, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Timestamp', 'Enc_X_Transformed', 'Enc_Y_Transformed', 'UWB_X', 'UWB_Y', 'Delta_Error'])

    def encoder_callback(self, msg):
        self.enc_x = msg.pose.pose.position.x
        self.enc_y = msg.pose.pose.position.y

    def uwb_callback(self, msg):
        self.uwb_x = msg.pose.position.x
        self.uwb_y = msg.pose.position.y
        self.log_to_file()

    def transform_encoder_to_uwb_frame(self, x, y):
        # Pos_transformed = R * Pos_encoder + T (R: rotation matrix, T: translation vector)
        rotation_matrix = np.array([
            [np.cos(self.theta), -np.sin(self.theta)],
            [np.sin(self.theta),  np.cos(self.theta)]
        ])
        enc_pos = np.array([x, y])
        translation = np.array([self.Tx, self.Ty]) 
        
        transformed = (rotation_matrix @ enc_pos) + translation
        return transformed[0], transformed[1]

    def log_to_file(self):
        tx, ty = self.transform_encoder_to_uwb_frame(self.enc_x, self.enc_y)
        dx = tx - self.uwb_x
        dy = ty - self.uwb_y
        delta = math.sqrt(dx**2 + dy**2)

        with open(self.filename, mode='a', newline='') as f:
            writer = csv.writer(f)
            timestamp = self.get_clock().now().to_msg().sec
            writer.writerow([timestamp, tx, ty, self.uwb_x, self.uwb_y, delta])

def main(args=None):
    rclpy.init(args=args)
    node = DataLoggerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Stop logging')
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()