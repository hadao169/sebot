# Multi-Sensor Fusion Localization

## System Integration: IMU, Wheel Encoder, UWB

This document describes the implementation of a localization system for a differential‑drive robot equipped with an IMU, wheel encoders, and an Ultra‑Wideband (UWB) system that replaces traditional GPS. By fusing high‑frequency relative motion data with absolute global references, stable and accurate navigation can be ensured for autonomous systems.

---

## 1. How the Sensors Work

### Inertial Measurement Unit (IMU)

- **Mechanism:**  
  Contains a 3‑axis gyroscope to measure angular velocity ($\omega$) and a 3‑axis accelerometer to measure linear acceleration ($a$).

- **Role:**  
  Provides high‑frequency data for rapid movement tracking and orientation. It serves as the “inner ear” of the robot.

- **Pros/Cons:**  
  Very fast response but suffers from “drift” (accumulated error) over time.

### Wheel Encoders (Odometry)

- **Mechanism:**  
  Sensors count the ticks of motor shafts to measure wheel rotation.

- **Role:**  
  Calculates linear displacement and heading through dead reckoning based on the robot’s kinematics (e.g., differential drive).

- **Pros/Cons:**  
  Reliable over short distances; performance degrades during wheel slippage or on carpet/uneven terrain.

### Ultra-Wideband (UWB)

- **Role:**  
  Provides absolute $X, Y, Z$ coordinates in the local UWB coordinate frame.

- **Pros:**  
  Achieves 2–10 cm accuracy; high immunity to multipath interference (distinguishes direct vs. reflected pulses); low power spectral density prevents interference with other radio signals.

- **Cons:**  
  Performance can degrade in environments with high metallic density or severe non‑line‑of‑sight conditions.

### LiDAR (Light Detection and Ranging)

- **Mechanism:**  
  Emits laser pulses to measure distances, creating a 360° point cloud of the environment.

- **Role:**  
  Performs “scan matching” against a known map to determine precise location relative to structural geometry.

- **Pros/Cons:**  
  Quite precise; can be confused by repetitive environments such as long, feature‑less corridors.

---

## 2. Sensor Setup

### 2.1 IMU (Xsens MTi 630)

This implementation uses the ROS 2 driver provided in the repository:  
<https://github.com/xsenssupport/Xsens_MTi_ROS_Driver_and_Ntrip_Client/tree/ros2>

### 2.2 UWB (Decawave DWM1001)

This implementation builds on the repository:  
<https://github.com/cliansang/uwb-tracking-ros/tree/ros2>  

The UWB system setup is further configured using helper scripts from:  
<https://github.com/SeAMKedu/DecawaveUWBwithPython>

### 2.3 2D LiDAR

- Driver for the RPLidar:  
  <https://github.com/Slamtec/rplidar_ros/tree/ros2>

After installing the drivers and required packages, the launch file in the `diffdrive` package is updated to run all sensors together with the robot. The built‑in `odom` node is kept only for low‑level wheel‑tick reading; the higher‑level odometry estimate is instead provided by the `robot_localization` package, which follows the ROS standard for multi‑sensor state estimation.

Below is the updated `diffdrive.launch.py` file:

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')

    colcon_prefix_path = os.getenv('COLCON_PREFIX_PATH').split("/install")

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

        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=[
                '-d',
                os.path.join(
                    get_package_share_directory('diffdrive'),
                    'rviz'   # change if the file name is different
                )
            ],
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
        uwb_launch,
        ekf_launch,
    ])
```

After running the robot, the data from the sensors is published to their own topics:

- IMU: topic `/imu/data`  
  Message type: `sensor_msgs/msg/Imu`
- UWB: topic `/dwm1001/id_DW878F/pose`  
  Message type: `geometry_msgs/msg/PoseWithCovarianceStamped`

#### Compile and source workspace

```bash
cd ~/ros2_ws
colcon build --symlink-install
source ~/ros2_ws/install/setup.bash
```

---

## 3. Robot_localization Package

`robot_localization` is a collection of state estimation nodes, each of which implements a nonlinear state estimator for robots moving in 3D space. In this setup, it replaces the simple wheel‑based odometry with a dual‑EKF configuration that follows ROS best practices for multi‑sensor localization.

### 3.1 Installation

To install the package for ROS 2, run:

```bash
sudo apt update
sudo apt install ros-${ROS_DISTRO}-robot-localization
```

Next, a dedicated localization package is created for easier configuration:

```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_cmake sebot_localization
```

### 3.2 Configuration (params file)

```bash
cd ~/ros2_ws/src/sebot_localization/config/
touch ekf_dual.yaml
```

Add the following configuration to the YAML file:

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

Each parameter should be adjusted according to the specific robot and sensor configuration, especially `process_noise_covariance` and `initial_estimate_covariance`, to achieve better localization performance. The official documentation and parameter explanation for `robot_localization` can be found in the repository:  
<https://github.com/cra-ros-pkg/robot_localization>

#### Disable TF of wheel_odom node

The simple wheel‑based odometry node in the `diffdrive` package is kept only for reading raw wheel‑tick data and converting it into a basic `Odometry` message. The higher‑level state estimation and `map -> odom -> base_link` transforms are instead handled by the `robot_localization` package, which is the ROS standard solution for multi‑sensor fusion (e.g., wheel encoders, IMU, and UWB). Therefore, disable the `tf_broadcaster` in the odom node to avoid the TF conflict between it and robot_localization estimate node. This approach provides a more robust, consistent, and configurable localization pipeline that can properly integrate noisy or intermittent sensor data.

#### Understanding Covariance Tuning

To achieve optimal results, the process noise covariance must be tuned. This matrix represents the uncertainty in the robot’s motion model.

- Lower values on the diagonal (e.g., 1e‑5) indicate that the EKF trusts the predicted motion more, which results in smoother but slower‑to‑correct behavior.
- Higher values (e.g., 1e‑2) make the EKF more reactive to sensor measurements such as UWB, which is useful for quick corrections but can introduce jitter if the sensor data is noisy.

##### Sensor Configuration Logic

- **IMU:** Only yaw and angular velocity are fused in the EKF. Roll and pitch are disabled because they are generally unnecessary for 2D ground robots and can introduce noise.
- **UWB:** Only X and Y positions are used. Since UWB typically does not provide reliable orientation estimates, the IMU is responsible for yaw, while UWB corrects the global position.

### 3.3 Transformation Between Frames

In a multi‑sensor system, each sensor operates in its own local frame. For the EKF to mathematically fuse the UWB measurements, all data must be expressed in a unified global frame, typically the `map` frame.

#### How the Transformation is Implemented

The transformation from the UWB frame into the `map` frame is handled by a custom ROS 2 node called `UwbTransformNode`. The implementation is available in the file:

`~/ros2_ws/src/sebot_localization/src/uwb_transform_dual_ekf.cpp`

This node:

- subscribes to:
  - the UWB pose topic (`/dwm1001/id_DW878F/pose`),
  - and the IMU topic (`imu/data`);

- uses a short history of IMU messages to interpolate the robot’s yaw at the UWB timestamp;

- computes an initial datum using the first `sample_threshold_` UWB position and averaged IMU yaw;

- applies the static offset between the UWB tag and the robot’s base link (defined in TF as `uwb_link` → `base_link`) in the robot’s current orientation;  

- then rotates and translates the UWB position into the `map` frame using the stored `pos0_uwb_` and `yaw0_`;

- finally publishes the result as an `Odometry` message on the topic `odometry/uwb_data`, with realistic covariance values for x, y, z, and orientation.

Because the transformation logic and parameters are already encapsulated in the node, the YAML configuration for the global EKF only needs to enable x and y from `odometry/uwb_data` and let the node handle the frame‑alignment details.

### 3.4 Last Step: Packaging and Launching

The C++ implementation for the EKF and UWB transformation nodes is grouped into a single package `sebot_localization`. The package metadata and dependencies are defined in `package.xml` and `CMakeLists.txt`.

**`~/ros2_ws/src/sebot_localization/package.xml`**

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>sebot_localization</name>
  <version>0.0.0</version>
  <description>Localization package for dual EKF fusion with IMU, wheel odometry, UWB, and LiDAR.</description>
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

**`~/ros2_ws/src/sebot_localization/CMakeLists.txt`**

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

The EKF nodes are launched via the configuration defined in the shared YAML file and the launch script below:

```bash
cd ~/ros2_ws/src/sebot_localization/
mkdir launch
touch ekf_dual.launch.py
```

```python
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
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
            parameters=[parameters_file_path, {'use_sim_time': use_sim_time}]
        )

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
