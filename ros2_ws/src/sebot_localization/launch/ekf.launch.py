from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch_ros.substitutions import FindPackageShare
from launch.substitutions import LaunchConfiguration
import os

def generate_launch_description():
    pkg_name = 'sebot_localization'
    
    ekf_config_path = os.path.join(
        FindPackageShare(package=pkg_name).find(pkg_name),
        'config',
        'ekf.yaml'
    )

    ekf_config_file_lc = LaunchConfiguration('ekf_config_file')
    use_sim_time_lc = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'ekf_config_file',
            default_value=ekf_config_path,
            description='Full path to EKF config file'
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'
        ),
        
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                ekf_config_file_lc,
                {'use_sim_time': use_sim_time_lc}
            ]
        ),

        Node(
            package='sebot_localization',
            executable='ekf_node',
            name='ekf_node',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time_lc}]
        )
    ])