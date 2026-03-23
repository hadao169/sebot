import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
import matplotlib.pyplot as plt
from collections import deque

class TrajectoryPlotter(Node):
    def __init__(self):
        super().__init__('trajectory_plotter')

        # Buffer size for the trajectory lines (last 500 points)
        self.max_points = 500
        self.data = {
            'wheel': {'x': deque(maxlen=self.max_points), 'y': deque(maxlen=self.max_points)},
            'uwb': {'x': deque(maxlen=self.max_points), 'y': deque(maxlen=self.max_points)},
            'local': {'x': deque(maxlen=self.max_points), 'y': deque(maxlen=self.max_points)},
            'global': {'x': deque(maxlen=self.max_points), 'y': deque(maxlen=self.max_points)}
        }

        # Subscriptions
        self.create_subscription(Odometry, 'wheel/odom', lambda msg: self.odom_cb(msg, 'wheel'), 10)
        self.create_subscription(Odometry, 'odometry/uwb_data', lambda msg: self.odom_cb(msg, 'uwb'), 10)
        self.create_subscription(Odometry, 'odometry/filtered/local', lambda msg: self.odom_cb(msg, 'local'), 10)
        self.create_subscription(Odometry, 'odometry/filtered/global', lambda msg: self.odom_cb(msg, 'global'), 10)

        # Plot Setup
        plt.ion()
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.ax.set_title("Robot Trajectory Comparison")
        self.ax.set_xlabel("X (meters)")
        self.ax.set_ylabel("Y (meters)")
        self.ax.grid(True)

        # Timers
        self.timer = self.create_timer(0.1, self.update_plot) # 5Hz Refresh

    def odom_cb(self, msg, key):
        self.data[key]['x'].append(msg.pose.pose.position.x)
        self.data[key]['y'].append(msg.pose.pose.position.y)

    def update_plot(self):
        self.ax.clear()
        self.ax.set_title("Real-time Trajectory: Wheel vs UWB vs EKF")
        self.ax.set_xlabel("X Coordinate")
        self.ax.set_ylabel("Y Coordinate")
        self.ax.grid(True)

        # Plot each source with different colors and styles
        self.ax.plot(list(self.data['wheel']['x']), list(self.data['wheel']['y']), 'r-', label='Wheel Odom (Drifting)')
        self.ax.plot(list(self.data['uwb']['x']), list(self.data['uwb']['y']), 'g-', label='Raw UWB (Noisy)')
        self.ax.plot(list(self.data['local']['x']), list(self.data['local']['y']), 'b-', label='EKF Local (Smooth)')
        self.ax.plot(list(self.data['global']['x']), list(self.data['global']['y']), 'k-', linewidth=2, label='EKF Global (Fused)')

        self.ax.legend(loc='upper right')
        plt.draw()
        plt.pause(0.01)

def main(args=None):
    rclpy.init(args=args)
    node = TrajectoryPlotter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        plt.ioff()
        plt.show()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()