import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    colcon_prefix_path = os.getenv('COLCON_PREFIX_PATH').split("/install")[0]

    urdf_file_name = 'robot.urdf'
    urdf = os.path.join(
        colcon_prefix_path,
        'config',
        urdf_file_name)
    with open(urdf, 'r') as infp:
        robot_desc = infp.read()
    print(urdf)
    if not robot_desc.strip():
        raise RuntimeError("robot_description is empty! Check your URDF file.")

    xsens_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('xsens_mti_ros2_driver'),
                'launch',
                'xsens_mti_node.launch.py'
            )
        )
    )

    lidar_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('rplidar_ros'),
                'launch',
                'view_rplidar_a1_launch.py'
            )
        )
    )
    
    uwb_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('uwb_tracking_ros2'),
                'launch',
                'uwb_tracking_dwm1001.launch.py'
            )
        )
    )
    
    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('sebot_localization'),
                'launch',
                'ekf_dual.launch.py'
            )
        )
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Use simulation (Gazebo) clock if true'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{'use_sim_time': use_sim_time,
                         'robot_description': robot_desc}],
        ),

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=[
                '-d',
                os.path.join(
                    get_package_share_directory('diffdrive'),
                    'rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
        ),

        Node(
            package='motordriver',
            executable='motordriver',
            name='motordriver_node',
            output='screen',
            parameters=[os.path.join(
                colcon_prefix_path,
                'config',
                'params.yaml')]
        ),

        Node(
            package='diffdrive',
            executable='odom',
            name='odom_node',
            output='screen',
            parameters=[os.path.join(
                colcon_prefix_path,
                'config',
                'params.yaml')]
        ),

        Node(
            package='diffdrive',
            executable='cmd_vel',
            name='cmd_vel_node',
            output='screen',
            parameters=[os.path.join(
                colcon_prefix_path,
                'config',
                'params.yaml')]
        ),
        xsens_launch,
        lidar_launch,
        uwb_launch,
        ekf_launch,
    ])
