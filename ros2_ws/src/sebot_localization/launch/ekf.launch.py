# single_ekf_custom.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_uwb',
            arguments=['0.05', '0', '0', '0', '0', '0', 'base_link', 'uwb_link']
        ),

        Node(
            package='sebot_localization',
            executable='uwb_transform_node',
            name='uwb_transform_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),

        Node(
            package='sebot_localization',
            executable='ekf_node',
            name='ekf_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time}],
        ),
        Node(
            package="uwb_tracking_ros2",
            executable="uwb_simulator",
            name="uwb_simulator",
            output="screen",
            parameters=[{'use_sim_time': use_sim_time}]
        )
    ])