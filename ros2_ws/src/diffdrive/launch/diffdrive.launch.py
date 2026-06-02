import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import IncludeLaunchDescription

def generate_launch_description():
    # NAMESPACE = 'SeBotxx' # korvaa xx oman Sebotin tunnisteella, esimerkiksi IP-osoitteen viimeisellä tavulla.
    # FRAME_PREFIX = NAMESPACE+"_" # luodaan robot_state_publisherin tukeman frame_prefix-parametrin arvo

    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    colcon_prefix_path = os.getenv('COLCON_PREFIX_PATH').split("/install")[0]

    urdf_file_name = 'robot.urdf'
    urdf = os.path.join(
        colcon_prefix_path,
        'ros2_ws/config',
        urdf_file_name)
    with open(urdf, 'r') as infp:
        robot_desc = infp.read()
    if not robot_desc.strip():
        raise RuntimeError("robot_description is empty! Check your URDF file.")
    print("robot_description loaded.", urdf)

    xsens_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('xsens_mti_ros2_driver'),
                'launch',
                'xsens_mti_node.launch.py'
            )
        )
    )

    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('sebot_localization'),
                'launch',
                'ekf.launch.py'
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
            #namespace = NAMESPACE,
            #parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc, 'frame_prefix': FRAME_PREFIX}],
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
            #arguments=[urdf] # 26.5.2025 tämä on tarpeeton rivi, sillä robot_state_publisher ei parsi komentokehotteen argumentteja.
        ),

        Node(
            package='joint_state_publisher_gui',
            executable='joint_state_publisher_gui',
            name='joint_state_publisher_gui',
            output='screen',
            #namespace = NAMESPACE,
            parameters=[{'use_sim_time': use_sim_time}],
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
                    'rviz',   # bạn có thể đổi tên nếu khác
                )
            ],
            parameters=[{'use_sim_time': use_sim_time}],
        ),

        Node(
            package='motordriver',
            executable='motordriver',
            name='motordriver_node',
            #namespace = NAMESPACE,
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
            #namespace = NAMESPACE,
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
            #namespace = NAMESPACE,
            output='screen',
            parameters=[os.path.join(
              colcon_prefix_path,
              'config',
              'params.yaml')]
        ),
        xsens_launch,
        ekf_launch,
        uwb_launch,

    ])

