import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

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
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
            arguments=[urdf]),

        #Node(
        #    package='tf2_web_republisher_py',
        #    executable='tf2_web_republisher',
        #    name='tf2_web_republisher',
        #    output='screen',
        #  ),

        Node(
            package='motordriver',
            executable='motordriver_battery',
            name='motordriver_node',
            output='screen',
            parameters=[os.path.join(
              colcon_prefix_path,
              'config',
              'params.yaml')] 
          ),

        Node(
            package='diffdrive',
            executable='odom_battery',
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

        Node(
            package='diffdrive',
            executable='pi_led',
            name='pi_led_node',
            output='screen',
          ), 

        Node(
            package='battery',
            executable='battery_republish',
            name='battery_republish_node',
            parameters=[os.path.join(
              colcon_prefix_path,
              'config',
              'params.yaml')],       
            output='screen',
          ),

        Node(
            package='battery',
            executable='battery_alert',
            name='battery_alert_node',
            parameters=[os.path.join(
              colcon_prefix_path,
              'config',
              'params.yaml')],
            output='screen',
          ),            

    ])
