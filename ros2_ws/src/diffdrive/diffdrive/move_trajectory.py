# import rclpy
# from rclpy.node import Node
# from geometry_msgs.msg import Twist, PoseStamped
# from nav_msgs.msg import Path
# import math

# class TrajectoryNode(Node):
#     def __init__(self):
#         super().__init__('trajectory_node')

#         self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
#         self.path_publisher_ = self.create_publisher(Path, '/desired_trajectory', 10)

#         self.timer_period = 0.05
#         self.timer = self.create_timer(self.timer_period, self.timer_callback)

#         self.declare_parameter('shape', 'custom')
#         self.shape = self.get_parameter('shape').get_parameter_value().string_value.lower()

#         self.time_elapsed = 0.0
#         self.is_finished = False
#         self.init_wait_time = 2.0
#         self.state = 'INIT'

#         self.ref_x = 0.0
#         self.ref_y = 0.0
#         self.ref_theta = 0.0
#         self.desired_path = Path()
#         self.desired_path.header.frame_id = 'odom'

#         # ==========================================
#         # 1. CẤU HÌNH HÌNH VUÔNG (SQUARE) - Quay về 2.5m
#         # ==========================================
#         self.square_side_length = 2.5
#         self.square_v = 0.2
#         self.square_w = 0.5
#         self.square_move_time = self.square_side_length / self.square_v
#         self.square_turn_time = (math.pi / 2.0) / self.square_w
#         self.square_side_count = 0

#         # ==========================================
#         # 2. CẤU HÌNH HÌNH TRÒN (CIRCLE) - Bán kính 1m
#         # ==========================================
#         self.circle_radius = 1.0
#         self.circle_v = 0.2
#         self.circle_w = self.circle_v / self.circle_radius
#         self.circle_time = (2 * math.pi * self.circle_radius) / self.circle_v

#         # ==========================================
#         # 3. CẤU HÌNH QUỸ ĐẠO TỰ DO (FREE PATH)
#         # ==========================================
#         self.free_v = 0.2
#         self.free_duration = 20.0

#         # ==========================================
#         # 4. CẤU HÌNH LỘ TRÌNH CUSTOM (QUAY VỀ GỐC 2.5m)
#         # ==========================================
#         self.custom_v = 0.15
#         self.custom_w = 0.5
#         self.custom_turn_time = (math.pi / 2.0) / self.custom_w
#         self.custom_commands = [
#             (2.5, 'LEFT'),   # 1. J(0,0) -> K(2.5, 0)
#             (2.5, 'LEFT'),   # 2. K(2.5, 0) -> E(2.5, 2.5)
#             (2.5, 'LEFT'),   # 3. E(2.5, 2.5) -> G(0, 2.5)
#             (1.5, 'LEFT'),   # 4. G(0, 2.5) -> L(0, 1.0)
#             (1.5, 'RIGHT'),  # 5. L(0, 1.0) -> M(1.5, 1.0)
#             (1.0, 'RIGHT'),  # 6. M(1.5, 1.0) -> N(1.5, 0)
#             (1.5, 'NONE')    # 7. N(1.5, 0) -> J(0, 0)
#         ]
#         self.custom_step = 0
#         self.custom_target_move_time = 0.0
#         self.custom_current_turn_dir = 'NONE'

#     def update_and_publish_desired_path(self, v, w):
#         delta_d = v * self.timer_period
#         delta_th = w * self.timer_period
#         avg_theta = self.ref_theta + (delta_th / 2.0)
        
#         self.ref_x += delta_d * math.cos(avg_theta)
#         self.ref_y += delta_d * math.sin(avg_theta)
#         self.ref_theta += delta_th

#         pose = PoseStamped()
#         pose.header.stamp = self.get_clock().now().to_msg()
#         pose.header.frame_id = 'odom'
#         pose.pose.position.x = self.ref_x
#         pose.pose.position.y = self.ref_y
#         pose.pose.orientation.z = math.sin(self.ref_theta / 2.0)
#         pose.pose.orientation.w = math.cos(self.ref_theta / 2.0)

#         self.desired_path.poses.append(pose)
#         self.desired_path.header.stamp = self.get_clock().now().to_msg()
#         self.path_publisher_.publish(self.desired_path)

#     def load_next_custom_step(self):
#         if self.custom_step < len(self.custom_commands):
#             distance, turn_dir = self.custom_commands[self.custom_step]
#             self.custom_target_move_time = distance / self.custom_v
#             self.custom_current_turn_dir = turn_dir
#             self.state = 'MOVE'
#             self.time_elapsed = 0.0
#             self.get_logger().info(f'Đoạn {self.custom_step + 1}: Đi thẳng {distance}m...')
#         else:
#             self.is_finished = True
#             self.get_logger().info('Đã hoàn thành toàn bộ lộ trình Custom!')

#     def timer_callback(self):
#         if self.is_finished:
#             return

#         msg = Twist()
#         v_cmd, w_cmd = 0.0, 0.0
#         is_moving = False

#         if self.state == 'INIT':
#             if self.time_elapsed < self.init_wait_time:
#                 self.time_elapsed += self.timer_period
#             else:
#                 if self.shape == 'custom':
#                     self.load_next_custom_step()
#                 else:
#                     self.state = 'MOVE'
#                     self.time_elapsed = 0.0
#                     self.get_logger().info('Bắt đầu di chuyển...')
#             self.publisher_.publish(msg)
#             return

#         if self.shape == 'square':
#             is_moving = True
#             if self.state == 'MOVE':
#                 if self.time_elapsed < self.square_move_time:
#                     v_cmd = self.square_v
#                     self.time_elapsed += self.timer_period
#                 else:
#                     self.state = 'TURN'
#                     self.time_elapsed = 0.0
#             elif self.state == 'TURN':
#                 if self.time_elapsed < self.square_turn_time:
#                     w_cmd = self.square_w
#                     self.time_elapsed += self.timer_period
#                 else:
#                     self.square_side_count += 1
#                     self.state = 'MOVE'
#                     self.time_elapsed = 0.0
#                     if self.square_side_count >= 4:
#                         self.is_finished = True
#                         self.get_logger().info('Hoàn thành Hình Vuông!')

#         elif self.shape == 'circle':
#             is_moving = True
#             if self.state == 'MOVE':
#                 if self.time_elapsed < self.circle_time:
#                     v_cmd = self.circle_v
#                     w_cmd = self.circle_w
#                     self.time_elapsed += self.timer_period
#                 else:
#                     self.is_finished = True
#                     self.get_logger().info('Hoàn thành Hình Tròn!')

#         elif self.shape == 'free':
#             is_moving = True
#             if self.state == 'MOVE':
#                 if self.time_elapsed < self.free_duration:
#                     v_cmd = self.free_v
#                     w_cmd = 0.5 * math.sin(0.5 * self.time_elapsed)
#                     self.time_elapsed += self.timer_period
#                 else:
#                     self.is_finished = True
#                     self.get_logger().info('Hoàn thành Quỹ đạo Tự do!')

#         elif self.shape == 'custom':
#             is_moving = True
#             if self.state == 'MOVE':
#                 if self.time_elapsed < self.custom_target_move_time:
#                     v_cmd = self.custom_v
#                     self.time_elapsed += self.timer_period
#                 else:
#                     if self.custom_current_turn_dir == 'NONE':
#                         self.custom_step += 1
#                         self.load_next_custom_step()
#                     else:
#                         self.state = 'TURN'
#                         self.time_elapsed = 0.0
#                         self.get_logger().info(f'Đang rẽ {self.custom_current_turn_dir}...')
#             elif self.state == 'TURN':
#                 if self.time_elapsed < self.custom_turn_time:
#                     if self.custom_current_turn_dir == 'LEFT':
#                         w_cmd = self.custom_w
#                     elif self.custom_current_turn_dir == 'RIGHT':
#                         w_cmd = -self.custom_w
#                     self.time_elapsed += self.timer_period
#                 else:
#                     self.custom_step += 1
#                     self.load_next_custom_step()

#         if self.is_finished:
#             v_cmd, w_cmd = 0.0, 0.0
#             is_moving = False

#         msg.linear.x = v_cmd
#         msg.angular.z = w_cmd
#         self.publisher_.publish(msg)

#         if is_moving:
#             self.update_and_publish_desired_path(v_cmd, w_cmd)

# def main(args=None):
#     rclpy.init(args=args)
#     node = TrajectoryNode()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     finally:
#         node.publisher_.publish(Twist())
#         node.destroy_node()
#         rclpy.shutdown()

# if __name__ == '__main__':
#     main()


import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import math

class TrajectoryNode(Node):
    def __init__(self):
        super().__init__('trajectory_node')

        # Khai báo tham số chọn quỹ đạo (1, 2 hoặc 3)
        self.declare_parameter('trajectory', 1)
        self.trajectory_type = self.get_parameter('trajectory').value

        # Publisher cmd_vel
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer_period = 0.05
        self.timer = self.create_timer(self.timer_period, self.timer_callback)

        # Cấu hình vận tốc chung
        self.v_speed = 0.15          # m/s
        self.w_speed = 0.5           # rad/s (dùng cho quay tại chỗ 90°)

        # Thời gian quay 90 độ
        self.turn_time = (math.pi / 2.0) / self.w_speed

        # -------------------------------------------------
        # Khởi tạo dữ liệu cho từng loại quỹ đạo
        # -------------------------------------------------
        self.commands = []           # danh sách (distance, turn_dir) cho quỹ đạo 1 & 2
        self.is_circle = False       # flag cho quỹ đạo 3
        self.circle_duration = 0.0   # thời gian chạy hết vòng tròn

        if self.trajectory_type == 1:
            # Quỹ đạo 1: như code gốc
            self.commands = [
                (1.5, 'LEFT'),   # 1
                (1.5, 'LEFT'),   # 2
                (1.5, 'LEFT'),   # 3
                (0.9, 'LEFT'),   # 4
                (0.9, 'RIGHT'),  # 5
                (0.6, 'RIGHT'),  # 6
                (0.9, 'NONE')    # 7
            ]
            self.get_logger().info('Chọn quỹ đạo 1 (theo hình gốc)')

        elif self.trajectory_type == 2:
            # Quỹ đạo 2: hình vuông 2.5x2.5
            side = 2.5
            self.commands = [
                (side, 'LEFT'),
                (side, 'LEFT'),
                (side, 'LEFT'),
                (side, 'NONE')
            ]
            self.get_logger().info(f'Chọn quỹ đạo 2 (hình vuông cạnh {side}m)')

        elif self.trajectory_type == 3:
            # Quỹ đạo 3: đường tròn bán kính 1.5m
            self.is_circle = True
            radius = 1.5
            # Thời gian để đi hết 1 vòng tròn
            circumference = 2.0 * math.pi * radius
            self.circle_duration = circumference / self.v_speed
            # Vận tốc góc cần thiết: w = v / R
            self.circle_angular = self.v_speed / radius   # = 0.1 rad/s
            self.get_logger().info(f'Chọn quỹ đạo 3 (vòng tròn R={radius}m, t={self.circle_duration:.1f}s)')
        else:
            self.get_logger().error('Tham số trajectory chỉ nhận 1, 2 hoặc 3. Dừng node.')
            raise ValueError('Invalid trajectory type')

        # Trạng thái máy trạng thái
        self.state = 'INIT'
        self.time_elapsed = 0.0
        self.init_wait_time = 2.0
        self.is_finished = False

        self.target_move_time = 0.0
        self.current_turn_dir = 'NONE'
        self.step = 0

        if not self.is_circle:
            self.get_logger().info('Khởi động kịch bản quỹ đạo (đi thẳng + rẽ).')
        else:
            self.get_logger().info('Khởi động kịch bản quỹ đạo tròn.')

    def load_next_step(self):
        if self.step < len(self.commands):
            distance, turn_dir = self.commands[self.step]
            self.target_move_time = distance / self.v_speed
            self.current_turn_dir = turn_dir
            self.state = 'MOVE'
            self.time_elapsed = 0.0
            self.get_logger().info(f'Đoạn {self.step+1}: đi thẳng {distance}m...')
        else:
            self.is_finished = True
            self.get_logger().info('Đã hoàn thành toàn bộ lộ trình!')

    def timer_callback(self):
        if self.is_finished:
            return

        msg = Twist()

        # Xử lý quỹ đạo tròn (đặc biệt)
        if self.is_circle:
            if self.state == 'INIT':
                if self.time_elapsed < self.init_wait_time:
                    self.time_elapsed += self.timer_period
                else:
                    self.state = 'CIRCLE'
                    self.time_elapsed = 0.0
                    self.get_logger().info('Bắt đầu chạy vòng tròn...')
            elif self.state == 'CIRCLE':
                if self.time_elapsed < self.circle_duration:
                    msg.linear.x = self.v_speed
                    msg.angular.z = self.circle_angular   # dương: rẽ trái liên tục
                    self.time_elapsed += self.timer_period
                else:
                    self.is_finished = True
                    self.get_logger().info('Đã hoàn thành vòng tròn.')
            # Publish và kết thúc
            self.publisher_.publish(msg)
            return

        # Xử lý quỹ đạo 1 và 2 (đi thẳng + rẽ tại chỗ)
        if self.state == 'INIT':
            if self.time_elapsed < self.init_wait_time:
                self.time_elapsed += self.timer_period
            else:
                self.load_next_step()

        elif self.state == 'MOVE':
            if self.time_elapsed < self.target_move_time:
                msg.linear.x = self.v_speed
                msg.angular.z = 0.0
                self.time_elapsed += self.timer_period
            else:
                if self.current_turn_dir == 'NONE':
                    self.step += 1
                    self.load_next_step()
                else:
                    self.state = 'TURN'
                    self.time_elapsed = 0.0
                    self.get_logger().info(f'Rẽ {self.current_turn_dir}...')

        elif self.state == 'TURN':
            if self.time_elapsed < self.turn_time:
                msg.linear.x = 0.0
                if self.current_turn_dir == 'LEFT':
                    msg.angular.z = self.w_speed
                elif self.current_turn_dir == 'RIGHT':
                    msg.angular.z = -self.w_speed
                self.time_elapsed += self.timer_period
            else:
                self.step += 1
                self.load_next_step()

        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Dừng robot
        node.publisher_.publish(Twist())
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()