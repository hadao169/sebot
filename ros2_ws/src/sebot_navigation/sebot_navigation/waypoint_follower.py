#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from nav2_msgs.action import FollowWaypoints
from geometry_msgs.msg import PoseStamped
from rclpy.action import ActionClient
from geometry_msgs.msg import Quaternion
import math

def quaternion_from_yaw(yaw):
    """Tạo quaternion từ góc yaw (rad)"""
    q = Quaternion()
    q.x = 0.0
    q.y = 0.0
    q.z = math.sin(yaw / 2.0)
    q.w = math.cos(yaw / 2.0)
    return q

class WaypointPublisher(Node):
    def __init__(self):
        super().__init__('waypoint_publisher')
        self._action_client = ActionClient(self, FollowWaypoints, 'follow_waypoints')
        self.get_logger().info('Waypoint Publisher Node Started')

    def send_waypoints(self, waypoints):
        if not self._action_client.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('FollowWaypoints action server not available!')
            return
        goal_msg = FollowWaypoints.Goal()
        goal_msg.poses = waypoints
        self.get_logger().info(f'Sending {len(waypoints)} waypoints...')
        future = self._action_client.send_goal_async(goal_msg)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return
        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Navigation finished')
        self.get_logger().info(f'Waypoint results: {result.waypoint_results}')

def create_waypoints_from_list(waypoint_list, frame_id='map'):
    waypoints = []
    for wp in waypoint_list:
        pose = PoseStamped()
        pose.header.stamp = rclpy.time.Time().to_msg()
        pose.header.frame_id = frame_id
        pose.pose.position.x = wp[0]
        pose.pose.position.y = wp[1]
        pose.pose.position.z = 0.0
        yaw = wp[2] if len(wp) > 2 else 0.0
        pose.pose.orientation = quaternion_from_yaw(yaw)
        waypoints.append(pose)
    return waypoints

def main():
    rclpy.init()
    node = WaypointPublisher()

    waypoints_data = [
        (1.0, 1.0, 0.0),
        (1.0, 3.0, 0.0),
        (2.5, 2.0, 0.0),
        (2.5, 2.5, 0.0),
        (3.0, 0.5, 3.14),
    ]

    waypoints = create_waypoints_from_list(waypoints_data)

    node.get_logger().info('=' * 50)
    node.get_logger().info('Waypoints:')
    for i, wp in enumerate(waypoints_data):
        node.get_logger().info(f'  {i+1}: ({wp[0]}, {wp[1]}, yaw={wp[2] if len(wp)>2 else 0})')
    node.get_logger().info('=' * 50)

    node.send_waypoints(waypoints)
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()