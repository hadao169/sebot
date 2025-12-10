#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import matplotlib.pyplot as plt
from collections import deque
import numpy as np
import matplotlib.patches as patches

class LSPosePlotter(Node):
    def __init__(self):
        super().__init__('ls_pose_plotter')

        target_topic = '/dwm1001/id_C4_22_04_B9_DE_53/pose_ls'
        self.get_logger().info(f"Dang ve do thi theo CM tu topic: {target_topic}")

        self.subscription = self.create_subscription(
            PoseStamped,
            target_topic,
            self.pose_callback,
            10
        )

        self.max_points = 500
        self.xs = deque(maxlen=self.max_points)
        self.ys = deque(maxlen=self.max_points)

        plt.ion() 
        self.fig, self.ax = plt.subplots()
        
        # Cấu hình Axes
        self.ax.set_title(f'Real-time LS Position & Error Bound')
        self.ax.set_xlabel('X [cm]') 
        self.ax.set_ylabel('Y [cm]')
        self.ax.grid(True)
        self.ax.set_aspect('equal', adjustable='box') 
        
        # 1. Vòng tròn Sai số (Radius = 10cm)
        self.error_radius = 10.0 
        self.error_circle = patches.Circle(
            (0, 0), # Center (x, y)
            self.error_radius,
            color='b', 
            alpha=0.2, 
            label='Error Bound (±10cm)', 
            zorder=1 
        )
        self.ax.add_patch(self.error_circle)

        # track Line
        self.track_line, = self.ax.plot([], [], 'k--', alpha=0.5, label='Path Track', zorder=2) 

        # Tag position
        self.sc = self.ax.scatter([], [], c='r', label='Current Position', s=50, zorder=3) 
        
        self.ax.legend(loc='upper right')
        
        self.create_timer(0.1, self.redraw)

    def pose_callback(self, msg: PoseStamped):
        # m -> cm
        x_cm = msg.pose.position.x * 100.0
        y_cm = msg.pose.position.y * 100.0
        
        self.xs.append(x_cm)
        self.ys.append(y_cm)

    def redraw(self):
        if not self.xs:
            self.fig.canvas.flush_events()
            return

        current_x = self.xs[-1]
        current_y = self.ys[-1]
        
        # Cập nhật quỹ đạo
        self.track_line.set_data(list(self.xs), list(self.ys))

        # Cập nhật vị trí tag
        self.sc.set_offsets(np.array([[current_x, current_y]]))
        
        # Cập nhật vòng tròn sai số 
        self.error_circle.center = (current_x, current_y)
        
        # Tự động co giãn trục
        self.ax.relim()
        self.ax.autoscale_view()
        
        self.fig.canvas.draw_idle()
        self.fig.canvas.flush_events()

def main(args=None):
    rclpy.init(args=args)
    node = LSPosePlotter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        plt.close('all')
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()