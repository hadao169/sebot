import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.conditions import IfCondition  # <-- thêm Import này

def generate_launch_description():

    use_static_tf = LaunchConfiguration('use_static_tf', default='true')
    params_file = LaunchConfiguration(
        'params_file',
        default=os.path.join(
            get_package_share_directory('uwb_tracking_ros2'),
            'config',
            'params_dwm1001.yaml'
        )
    )
    rviz_config_file = os.path.join(
        get_package_share_directory('uwb_tracking_ros2'),
        'rviz',
        'dwm1001_rviz_config.rviz'
    )

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_static_tf',
            default_value='true',
            description='Whether to use static TF'
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='uwb_static_tf',
            arguments=['2.5', '2.5', '0', '0', '0', '0', '1', 'map', 'uwb_map'],
            condition=IfCondition(use_static_tf)  #
        ),

        Node(
            package='uwb_tracking_ros2',
            executable='uwb_tracking_dwm1001',
            name='uwb_tracking_dwm1001',
            output='screen',
            parameters=[params_file]
        ),

        Node(
            package='uwb_tracking_ros2',
            executable='viz_dwm1001',
            name='visualize_dwm1001',
            output='screen'
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config_file]
        ),
    ])

generate_launch_description()