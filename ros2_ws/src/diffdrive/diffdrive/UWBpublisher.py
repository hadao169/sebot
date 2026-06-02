import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import re
import numpy as np
from nav_msgs.msg import Odometry

class Kalman1D:
    def __init__(self, q=0.002, r=0.05):
        self.q = q  # Process noise (tăng nhẹ cho 10Hz)
        self.r = r  # Measurement noise
        self.x = None
        self.p = 1.0

    def filter(self, z):
        if self.x is None:
            self.x = z
            return self.x
        # Predict
        self.p = self.p + self.q
        # Update
        k_gain = self.p / (self.p + self.r)
        self.x = self.x + k_gain * (z - self.x)
        self.p = (1 - k_gain) * self.p
        return self.x

# ==========================================
# 2. NODE GIẢ LẬP XỬ LÝ UWB (10HZ)
# ==========================================
class UWBPublisher(Node):
    def __init__(self, file_path):
        super().__init__('uwb_fix_publisher_node')
        self.publisher_ = self.create_publisher(Odometry, 'uwb/fix', 10)
        
        # Mở file và chuẩn bị dữ liệu
        try:
            self.file = open(file_path, 'r', encoding='utf-8')
        except FileNotFoundError:
            self.get_logger().error(f'Không tìm thấy file: {file_path}')
            return

        self.kf_dict = {}
        self.last_pos = None
        self.anchor_pattern = re.compile(r"([0-9A-F]{4})\[([-0-9\.]+),([-0-9\.]+),([-0-9\.]+)\]=([0-9\.]+)")
        
        # Tạo Timer chạy ở tần số 10Hz (0.1 giây)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info('Node giả lập UWB 10Hz đã bắt đầu...')

    def taylor_ls_positioning(self, anchors, distances):
        anchors = np.array(anchors)
        distances = np.array(distances)
        
        # Điểm khởi đầu thông minh
        if self.last_pos is None:
            xv = np.mean(anchors, axis=0)
        else:
            xv = self.last_pos

        for _ in range(15):
            diff = anchors - xv
            r_v = np.linalg.norm(diff, axis=1)
            r_v[r_v == 0] = 1e-6
            
            b = distances - r_v
            H = (xv - anchors) / r_v[:, np.newaxis]
            
            try:
                HTH = H.T @ H + np.eye(3) * 1e-6
                delta = np.linalg.inv(HTH) @ H.T @ b
                xv = xv + delta
                if np.linalg.norm(delta) < 1e-4:
                    break
            except np.linalg.LinAlgError:
                return None
        return xv

    def timer_callback(self):
        line = self.file.readline()
        if not line:
            self.get_logger().info('Đã đọc hết file dữ liệu. Dừng Timer.')
            self.timer.cancel()
            return

        m_anchors = self.anchor_pattern.findall(line)
        
        # Chỉ xử lý nếu có đủ 4 phép đo từ 4 anchors
        if len(m_anchors) == 4:
            curr_anchors_pos = []
            curr_filtered_dists = []

            for a_id, ax, ay, az, d_raw in m_anchors:
                dist = float(d_raw)
                # Mỗi Anchor ID có một bộ lọc Kalman 1D riêng
                if a_id not in self.kf_dict:
                    self.kf_dict[a_id] = Kalman1D(q=0.002, r=0.05)
                
                # Bước 1: Lọc khoảng cách (Range Filtering)
                f_dist = self.kf_dict[a_id].filter(dist)
                
                curr_anchors_pos.append([float(ax), float(ay), float(az)])
                curr_filtered_dists.append(f_dist)

            # Bước 2: Giải thuật Taylor LS (Trilateration)
            new_pos = self.taylor_ls_positioning(curr_anchors_pos, curr_filtered_dists)

            if new_pos is not None:
                self.last_pos = new_pos
                
                # Bước 3: Publish PoseStamped
                msg = Odometry()
                msg.header.stamp = self.get_clock().now().to_msg()
                msg.header.frame_id = 'map'
                
                msg.pose.pose.position.x = new_pos[0]
                msg.pose.pose.position.y = new_pos[1]
                msg.pose.pose.position.z = new_pos[2]
                msg.pose.pose.orientation.w = 1.0
                
                self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    # Đường dẫn file CSV của bạn
    file_path = '/home/hadao169/sebot/data_ekf/uwb_raw_data/test_5.2.2026/uwb_raw_05_1122.csv'
    uwb_node = UWBPublisher(file_path)
    
    try:
        rclpy.spin(uwb_node)
    except KeyboardInterrupt:
        pass
    finally:
        uwb_node.file.close()
        uwb_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()