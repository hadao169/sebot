# dual_ekf_standard.launch.py
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from ament_index_python.packages import get_package_share_directory
import os

def generate_launch_description():
    pkg_name = 'sebot_localization'
    
    robot_localization_dir = get_package_share_directory(pkg_name)
    parameters_file_dir = os.path.join(robot_localization_dir, 'config')
    parameters_file_path = os.path.join(parameters_file_dir, 'ekf_dual.yaml')
    print(parameters_file_path)
    os.environ['FILE_PATH'] = str(parameters_file_dir)
    

    use_sim_time = LaunchConfiguration('use_sim_time')

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation clock'),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_to_uwb',
            arguments=['0', '-0.05', '0', '0', '0', '0', 'base_link', 'uwb_link']
        ),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_local',
            output='screen',
            parameters=[parameters_file_path, {'use_sim_time': use_sim_time}],
            remappings=[('odometry/filtered', 'odometry/filtered/local')]
        ),

        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node_global',
            output='screen',
            parameters=[parameters_file_path, {'use_sim_time': use_sim_time}],
            remappings=[('odometry/filtered', 'odometry/filtered/global')]
        ),

        # Node(
        #     package='sebot_localization',
        #     executable='uwb_transform_dual_ekf_node',
        #     name='uwb_transform_dual_ekf_node',
        #     output='screen',
        #     parameters=[{'use_sim_time': use_sim_time}],
        #     remappings=[
        #         ('odometry/uwb_data', 'odometry/uwb_data')
        #     ]
        # ),
        
        # Node(
        #     package="uwb_tracking_ros2",
        #     executable="uwb_simulator",
        #     name="uwb_simulator",
        #     output="screen",
        #     parameters=[{'use_sim_time': use_sim_time}]
        # )
    ])
    
