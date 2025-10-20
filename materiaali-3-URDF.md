### URDF

A URDF (Unified Robot Description Format) file is an XML-based file format that contains a structural and kinematic description of a robot. It defines, for example, the robot's bodies, joints, materials, and dimensions.

![turning radius](kuvat/kinematic.png)

The model consists of joints and links. Joints can be either fixed or movable (fixed links such as sensors and movable links such as an arm or wheels). When a LIDAR and a 3D camera are added to the robot, for example, point clouds and other sensor data are brought into a common coordinate system, so they describe the same environment.

URDF models can be used to visualize and simulate robot structure and movement in tools like RViz and Gazebo.

Before the next step in motor control, a model of the robot is created. This allows better tracking of the robot's movements using the RViz tool, which helps to visualize and understand the operation better.

Create a `diffdrive` package

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python diffdrive
```

Create directories for configurations and launch files.

```bash
cd ~/ros2_ws
mkdir config
cd ~/ros2_ws/src/diffdrive
mkdir launch
```

> In future calculations, the robot's geometric properties defined here will not be taken into account. Therefore, for the movement to correspond to reality, it must be ensured that the wheel diameter and the distance between them are consistent in the calculations with both the values defined here and the actual hardware values.

**~/ros2_ws/config/robot.urdf**

```xml
<?xml version="1.0"?>

<robot name="robot model">

  <link name="base_footprint"/>

   <link name="base_link">
     <visual>
      <geometry>
        <box size="0.5 0.3 0.1"/>
      </geometry>
      <material name="blue">
        <color rgba="0 0 1 1"/>
      </material>
      <origin xyz="0 0 0" rpy="0 0 0" />
    </visual>
  </link>

  <joint name="base_footprint_to_base_link" type="fixed">
    <parent link="base_footprint"/>
    <child link="base_link"/>
    <origin xyz="0 0 0.0" rpy="0 0 0"/>
  </joint>

  <link name="left_wheel">
    <visual>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
      <material name="black">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>

  <link name="right_wheel">
    <visual>
      <geometry>
        <cylinder length="0.05" radius="0.1"/>
      </geometry>
      <material name="black">
        <color rgba="0 1 0 1"/>
      </material>
    </visual>
  </link>

  <joint name="base_to_left_wheel" type="fixed">
    <parent link="base_link"/>
    <child link="left_wheel"/>
    <origin xyz="0 0.15 0" rpy="-1.57 0 0"/>
  </joint>

  <joint name="base_to_right_wheel" type="fixed">
    <parent link="base_link"/>
    <child link="right_wheel"/>
    <origin xyz="0 -0.15 0" rpy="-1.57 0 0"/>
  </joint>

</robot>
```

Create a launch script that publishes the URDF file on the `robot_description` topic using the `robot_state_publisher` node. This allows the model to be shared with RViz and other nodes.

A ROS2 launch file is essentially a script that launches one or more ROS2 applications, such as nodes, parameters, or other processes. A launch file allows managing system components from one place and makes launching complex systems easier and more flexible.

**~/ros2_ws/src/diffdrive/launch/diffdrive.launch.py**

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    use_sim_time = LaunchConfiguration('use_sim_time', default='false')
    #NAMESPACE = 'SeBotxx' # replace xx with your SeBot's identifier, e.g., the last byte of the IP address.
    #FRAME_PREFIX = NAMESPACE+"_"
    # Working directory
    colcon_prefix_path = os.getenv('COLCON_PREFIX_PATH').split("/install")[0]

    # Read URDF file into robot_desc variable
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

        # Node to launch
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            #parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc, 'frame_prefix': FRAME_PREFIX}],# uncomment this line if you want to use a multi-robot namespace arrangement. Comment out the next line accordingly.
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
            #arguments=[urdf], # 26.5.2025 This line is redundant, robot_state_publisher does not parse command line arguments separately. The URDF file is passed to it as parameters.
            #namespace=NAMESPACE, # uncomment this line if you want to use a multi-robot namespace arrangement.
            ),

        ## Add conversion map->[namespace]_odom so that all robots are included in the same TF tree.
        #Node(
        #    package='tf2_ros',
        #    executable='static_transform_publisher',
        #    name='map_to_robot_odom',
        #    namespace=NAMESPACE,
        #    arguments=['0', '0', '0', '0', '0', '0',  # x y z yaw pitch roll
        #               'map', f'{FRAME_PREFIX}odom'],
        #    output='screen'
        #),
    ])
```

> Note that the namespace setting can be conveniently written as part of the launch file's node class parameter list, so that it is always automatically taken into account. We can run the launch file in its own directory without compiling and check its functionality

Let's try launching `diffdrive.launch.py` before compiling it into the package:

```
cd ~/ros2_ws/src/diffdrive/launch
ros2 launch diffdrive.launch.py
```

Modify the `setup.py` file so that the files in the config and launch directories are also included in the package compilation. This ensures that all necessary resources, such as configuration and launch files, are available after installation.

**~/ros2_ws/src/diffdrive/setup.py**

```python
from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'diffdrive'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name), glob('config/*')),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ros2',
    maintainer_email='ros2@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
        ],
    },
)
```

Compile the project, and since we have added a new package, it is important to re-run the source command. After this, we can launch the robot's URDF model and ensure its functionality.

```bash
cd ~/ros2_ws
colcon build --packages-select diffdrive
source ~/ros2_ws/install/setup.bash

ros2 launch diffdrive diffdrive.launch.py
```

Using the `view_frames` application from `tf2_tools`, which comes with ROS2 standard packages, you can get an understanding of the hierarchy and relationships of the TF frames in your system. Since you have published your robot's URDF model, you can examine these frames, which the URDF defines, related to the robot's body and wheels.

```bash
ros2 run tf2_tools view_frames -o robotframes

# Use evince -pdf reader
evince robotframes.pdf
```

![turning radius](kuvat/frames1.png)

The more parts a robot has, the more complex the TF tree becomes.
![turning radius](kuvat/complexurdf.jpg)

And what that model looks like in practice, we can examine in more detail in RViz.

Start RViz

```bash
rviz2
```

In RViz, the robot model should now be visible when you add the RobotModel visualization tool and set it to listen to the correct `robot_description` topic. It is important to ensure that the structures and parameters of the URDF file are defined correctly so that the model's visualization meets expectations and looks like the image below.

![turning radius](kuvat/rviz_urdf.png)

- Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
