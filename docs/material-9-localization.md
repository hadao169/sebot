# Multi-Sensor Fusion Localization

## System Integration: IMU, Wheel Encoder, UWB

This document provides a technical walkthrough for implementing a localization system. By fusing high-frequency relative motion data with absolute global references, we ensure stable and accurate navigation for autonomous systems.

## 1. How the Sensors Work

### **Inertial Measurement Unit (IMU)**

- **Mechanism:** Contains a 3-axis gyroscope to measure angular velocity ($\omega$) and a 3-axis accelerometer to measure linear acceleration ($a$).
- **Role:** Provides high-frequency data for rapid movement tracking and orientation. It is the "inner ear" of the robot.
- **Pros/Cons:** Very fast response but suffers from "drift" (accumulated error) over time.

### **Wheel Encoders (Odometry)**

- **Mechanism:** Sensors count the ticks of motor shafts to measure wheel rotation.
- **Role:** Calculates linear displacement and heading through dead reckoning based on the robot's kinematics (e.g., Differential Drive).
- **Pros/Cons:** Reliable over short distances; fails during wheel slippage or on carpet/uneven terrain.

### **Ultra-Wideband (UWB)**

- **Role:** Provides absolute $X, Y, Z$ coordinates
- **Pros:** Achieves 2–10 cm accuracy; high immunity to multipath interference (distinguishes direct vs. reflected pulses); low power spectral density prevents interference with other radio signals.
- **Cons:** Performance can degrade in environments with extreme metallic density.

### **LiDAR (Light Detection and Ranging)**

- **Mechanism:** Emits laser pulses to measure distances, creating a 360° point cloud of the environment.
- **Role:** Performs "Scan Matching" against a known map to determine precise location relative to structural geometry.
- **Pros/Cons:** Quite precise; can be confused by repetitive environments like long, featureless corridors.

## 2. Sensor Setup

### 2.1 IMU (Xsens MTi 630)

- Follow this repository https://github.com/xsenssupport/Xsens_MTi_ROS_Driver_and_Ntrip_Client/tree/ros2

### 2.2 UWB (Decawave DWM1001)

- This implementation is based on this repository https://github.com/cliansang/uwb-tracking-ros/tree/ros2
- To set up the UWB system, you can follow the instruction in this repository https://github.com/SeAMKedu/DecawaveUWBwithPython

### 2.3 2D Lidar

- Driver for the RPLidar https://github.com/Slamtec/rplidar_ros/tree/ros2

After install the drivers and required packages, you need to update the launch file in diffdrive package to run all sensors together with the robot.

```python
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

    ekf_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('sebot_localization'),
                'launch',
                'ekf_dual.launch.py'
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
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
        ),

        # Node(
        #     package='joint_state_publisher_gui',
        #     executable='joint_state_publisher_gui',
        #     name='joint_state_publisher_gui',
        #     output='screen',
        #     #namespace = NAMESPACE,
        #     parameters=[{'use_sim_time': use_sim_time}],
        # ),

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
        uwb_launch,
        ekf_launch,
    ])


```

After running the robot, the data from sensors will be published to their own topic

- IMU: topic imu/data (Message Type: nav_msgs/msg/Imu)
- UWB: topic dwm1001/id_DW878F/pose (Message Type: geometry_msgs/msg/PoseWithCovarianceStamped)

##### Compile and source workspace

```bash
cd ~/ros2_ws
colcon build --symlink-install
source ~/ros2_ws/install/setup.bash
```

## 3. Robot_localization package

robot_localization is a collection of state estimation nodes, each of which is an implementation of a nonlinear state estimator for robots moving in 3D space.

### 3.1 Installation

To install the package for ROS2, run the following command in your terminal:

```bash
sudo apt update
sudo apt install ros-${ROS_DISTRO}-robot-localization
```

And then, you should create a package for localization for more easily configuration by executing command

```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_cmake sebot_localization
```

### 3.2 Configuration (params file)

```bash
cd ~/ros2_ws/src/sebot_localization/config/
touch ekf_dual.yaml
```

And then add this to the yaml file:

```yaml
ekf_filter_node_local:
  ros__parameters:
    frequency: 30.0
    sensor_timeout: 0.1
    two_d_mode: true
    publish_tf: true
    map_frame: map
    odom_frame: odom
    base_link_frame: base_footprint
    world_frame: odom

    odom0: wheel/odom
    odom0_config: [false, false, false,
                  false, false, false,
                  true,  true,  false,
                  false, false, true,
                  false, false, false]

    imu0: imu/data
    imu0_config: [false, false, false,
                  false, false,  true,
                  false, false, false,
                  false, false,  true,
                  false, false, false]
    process_noise_covariance: []
    initial_estimate_covariance: []

ekf_filter_node_global:
  ros__parameters:
    frequency: 30.0
    sensor_timeout: 0.1
    two_d_mode: true
    publish_tf: true
    map_frame: map
    odom_frame: odom
    base_link_frame: base_footprint
    world_frame: map

    odom0: wheel/odom
    odom0_config: [false, false, false,
                  false, false, false,
                  true,  true,  false,
                  false, false, true,
                  false, false, false]

    odom1: odometry/uwb_data
    odom1_config: [true, true, false,
                  false, false, false,
                  false, false, false,
                  false, false, false,
                  false, false, false]
    odom1_pose_rejection_threshold: 3.0

    imu0: imu/data
    imu0_config: [false, false, false,
                  false, false, true,
                  false, false, false,
                  false, false, true,
                  false, false, false]
    process_noise_covariance: []
    initial_estimate_covariance: []
```

In this yaml file, you should adjust the value of each parameter according to your system, especially the process_noise_covariance and initial_estimate_covariance to get better localization result. The instructions and explaination about all parameters can be found in this repository https://github.com/cra-ros-pkg/robot_localization

#### Understanding Covariance Tuning

To achieve optimal results, you must tune the Process Noise Covariance. This matrix represents the uncertainty in your robot's motion model.

- Lower values in the diagonal (e.g., 1e-5) tell the EKF to trust the robot's predicted path more (resulting in smoother but slower-to-correct motion).
- Higher values (e.g., 1e-2) make the EKF more reactive to sensor measurements like UWB, which is good for quick corrections but can introduce jitter if the sensors are noisy.

Sensor Configuration Logic

- IMU: We set only Yaw, Angular Velocity Z to true. Using Roll and Pitch is unnecessary for 2D ground robots and often introduces noise.
- UWB: We set only X and Y to true. Since UWB doesn't provide reliable heading (orientation), we let the IMU handle the yaw while UWB fixes the global position.

### 3.3 Transformation between frames

In a multi-sensor system, each sensor operates in its own Local Frame. For the EKF to mathematically fuse data from UWB, every measurement must be translated into a unified Global Frame (the map frame).

#### How the Transformation is Implemented

- In this project, the transformation is handled by the uwb_transform_dual_ekf_node. You can read more about it in this LINK or you can find code in the path **ros2_ws/src/sebot_localization/uwb_transform_dual_ekf.cpp**

- The transformed data is re-published as a nav_msgs/msg/Odometry message on the topic odometry/uwb_data. This message is now "Map-aligned," allowing the ekf_filter_node_global to fuse it directly with other sources.

### 3.4 Last step

Now we will deal with the files `package.xml`, which contains the package description definition, and `CMakeLists.txt`, which contains the compilation settings.

**~/ros2_ws/src/sebot_localization/package.xml**

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>sebot_localization</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="ros2@todo.todo">ros2</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>
  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <depend>rclcpp</depend>
  <depend>std_msgs</depend>
  <depend>sensor_msgs</depend>
  <depend>nav_msgs</depend>
  <depend>geometry_msgs</depend>
  <depend>tf2</depend>
  <depend>tf2_ros</depend>
  <depend>tf2_geometry_msgs</depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>

</package>
```

**~/ros2_ws/src/sebot_localization/CMakeLists.txt**

```txt
cmake_minimum_required(VERSION 3.8)
project(sebot_localization)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

include_directories(include)

add_executable(ekf_node src/ekf_node.cpp)
target_include_directories(ekf_node PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${Eigen3_INCLUDE_DIRS}
)
ament_target_dependencies(ekf_node
  rclcpp sensor_msgs nav_msgs geometry_msgs std_msgs tf2 tf2_ros tf2_geometry_msgs
)
target_link_libraries(ekf_node Eigen3::Eigen)

add_executable(uwb_transform_node src/uwb_transform.cpp)
target_include_directories(uwb_transform_node PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${Eigen3_INCLUDE_DIRS}
)
ament_target_dependencies(uwb_transform_node
  rclcpp sensor_msgs nav_msgs geometry_msgs std_msgs tf2 tf2_ros tf2_geometry_msgs
)
target_link_libraries(uwb_transform_node Eigen3::Eigen)

add_executable(uwb_transform_dual_ekf_node src/uwb_transform_dual_ekf.cpp)
target_include_directories(uwb_transform_dual_ekf_node PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${Eigen3_INCLUDE_DIRS}
)
ament_target_dependencies(uwb_transform_dual_ekf_node
  rclcpp sensor_msgs nav_msgs geometry_msgs std_msgs tf2 tf2_ros tf2_geometry_msgs
)
target_link_libraries(uwb_transform_dual_ekf_node Eigen3::Eigen)


install(TARGETS
  ekf_node
  uwb_transform_node
  uwb_transform_dual_ekf_node
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
```

To run the ekf nodes, we need a launch file:

```bash
cd ~/ros2_ws/src/sebot_localization/
mkdir launch
touch ekf_dual.launch.py
```

```python
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

        ## Static transform to eliminate the offset of sensor to the center of the robot (UWB is placed 5cm to the right of the robot center)
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='static_transform_publisher_uwb_to_base_link',
            output='screen',
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

        Node(
            package='sebot_localization',
            executable='uwb_transform_dual_ekf_node',
            name='uwb_transform_dual_ekf_node',
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
    ])
```

![Dual EKF architecture](/images/ekf_architecture.png)
<p>
  <em>Figure 1. Integration of UWB computation in ROS 2 according to Moore’s (2016) model (Mäkelä 2024)</em>
</p>

The localization strategy uses a Dual-EKF architecture to separate smooth local motion from global positioning accuracy.

The Local EKF (Odom Frame) fuses high-frequency data from the IMU and Wheel Encoders. Its primary role is to produce a jitter-free, continuous stream of odometry (50Hz–100Hz) for immediate motion control. While this frame stays smooth for local maneuvers, it naturally drifts over time because it lacks an external reference.

The Global EKF (Map Frame) acts as the system's error corrector. It fuses the same data as local EKF together with absolute global references UWB. Its objective is to calculate the transform between the map -> odom frames to eliminate accumulated drift.

##### Compile and source workspace

```bash
cd ~/ros2_ws
colcon build --symlink-install
source ~/ros2_ws/install/setup.bash
ros2 launch diffdrive diffdrive.launch.py
```

There is a data file obtained by using this system, you can take a look at how the EKF helped to correct the drifts over time with only wheel encoders by executing commands:

```bash
# Open the first terminal
# Replay the bag data file with rosbag
ros2 bag play ~/ros2?ws/data_ekf/rosbag2_2026_03_02-02_11_23 --topic wheel/odom odometry/uwb_data odometry/filtered/local odometry/filtered/global

# Open the second terminal
source ~/ros2_ws/install/setup.bash
ros2 run diffdrive plot
```

