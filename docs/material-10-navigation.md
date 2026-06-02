# Navigation with Static Map and Nav2

## 1. Introduction to Navigation

Navigation in this system is the process of moving the robot autonomously from its current pose to a specified goal pose in the map frame. The navigation stack uses:

- a static occupancy-grid map of the environment,
- live localization estimates from the dual-EKF localization system,
- and LiDAR-based obstacle detection
to plan and execute safe motion while avoiding obstacles.

In addition to simple point-to-point navigation, this system also supports **waypoint following**, where the robot follows a predefined sequence of poses instead of just a single goal.

## 2. What is Nav2?

Nav2 is the standard ROS 2 navigation stack for mobile robots. It provides a modular, configurable framework for:

- global path planning,
- local path following and collision avoidance,
- recovery behaviors,
- and map-based localization (though in this project localization is handled externally).

Nav2 is designed to work with:

- the TF coordinate system (`map -> odom -> base_link (or base_footprint)`),
- an occupancy-grid map,
- LiDAR (or 2D range sensors),
- and odometry or pose estimates.

The stack is based on behavior trees and lifecycle nodes, which allows subsystems like the planner, controller, and map server to be started and stopped in a controlled way.

## 3. Main Components of Nav2

Nav2 is composed of several core components, each of which corresponds to a dedicated ROS 2 node or server:

- **Map Server**  
  Loads the static map (e.g., `map.yaml` and `map.pgm`) and publishes it as a global map used by the navigation stack.

- **AMCL** *(optional)*  
  A 2D particle‑filter localization node that estimates the robot’s pose on the map. In this project, AMCL can be disabled because the existing dual‑EKF localization already provides the robot’s pose in the `map` frame.

- **Global Planner**  
  Computes a **global path** from the robot’s current pose to the goal pose in the map frame. This node is responsible for finding a valid, collision‑free route through the static environment, based on the static map and costmaps.

- **Local Planner (Controller Server)**  
  Transforms the global path into **velocity commands** (`cmd_vel`) while **handling real‑time obstacle avoidance**. Together with the costmap, the local planner continuously checks the robot’s immediate surroundings and dynamically adjusts the trajectory so that the robot never collides with obstacles (static or dynamic). In many Nav2 setups, the DWB (DWBLocalPlanner) or similar controller plugins are used for this task.

- **Behavior Tree Navigator (BT Navigator)**  
  Orchestrates the entire navigation workflow using behavior trees, i.e., starting the global planner, calling the local planner, executing recovery behaviors on failure, and monitoring the current goal state.

- **Costmap2D Server**  
  Maintains two costmaps:
  - a **global costmap**, built from the static map and long‑range obstacles,
  - and a **local costmap**, built primarily from LiDAR (or 2D range sensors).
  The costmaps are the main components that detect and represent obstacles; the local planner then uses these costmaps to decide which velocities and trajectories are safe.

- **Lifecycle Manager**  
  Controls the startup order and state transitions of the Nav2 nodes (e.g., map‑server → amcl → planners and controller), ensuring that the stack is properly initialized before the robot starts to move.

In this project, the dual‑EKF localization system provides the `map -> odom -> base_link` TF tree, while Nav2 performs map‑based navigation and **obstacle avoidance using the Costmap2D Server and the Local Planner (Controller Server)**.

## 4. Required Packages

To use Nav2 together with SLAM Toolbox and the waypoint follower, install:

```bash
sudo apt update
sudo apt install ros-${ROS_DISTRO}-slam-toolbox ros-${ROS_DISTRO}-navigation2 ros-${ROS_DISTRO}-nav2-bringup ros-${ROS_DISTRO}-robot-localization
```

## 5. Create the Navigation Package and Build the Workspace

After installing the packages and setting up your navigation package:

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python sebot_navigation
```

Folder structure:

```bash
cd ~/ros2_ws/src/sebot_navigation/
mkdir -p config launch
touch config/nav2_params.yaml
touch config/slam_toolbox_params.yaml
touch sebot_navigation/waypoint_publisher.py
touch launch/nav2_bringup.launch.py
touch launch/sebot_navigation.launch.py
touch launch/slam_online_async.launch.py
```

Source code can be found in the path: `~/ros2_ws/src/sebot_navigation`

## 6. How to Use (with UWB–IMU Alignment)

This section describes how to create a static map, save it, and then use it for navigation, while also explaining the UWB–IMU coordinate alignment strategy.

### 6.1 UWB–IMU Coordinate Alignment Strategy

Because the UWB system defines its own 2D coordinate frame (with the first anchor at `0,0`) and the IMU often assumes a different heading reference (e.g., north‑based yaw), it is difficult to align the UWB frame directly with an external UTM‑like GPS frame.

To avoid this problem, the following strategy is used:

- The IMU is configured (using the manufacturer software) so that:
  - its yaw value is **0 at startup**,
  - and the orientation is aligned with the UWB frame axes.

- The robot is always started:
  - at the **first UWB anchor position** (`0,0` in the UWB frame),
  - with the robot’s front facing the **UWB frame x‑axis**,
  so that the UWB and IMU reference frames naturally align during operation.

This approach removes the need to convert UWB coordinates into a UTM‑like GPS frame and keeps the robot’s internal coordinate system consistent with the fixed UWB layout. Although the UWBTransformNode can perform the transformation from the UWB frame to the map frame even when the robot is not started at anchor 1, you should always place the robot at anchor 1 when creating the static map and when starting navigation. This avoids the situation where the goal pose you provide lies outside the UWB frame or becomes misaligned with the actual environment.

### 6.2 Mapping phase

Because the robot’s frame must always be aligned with the UWB layout, the static map should be created when the robot starts at the first UWB anchor and its orientation matches the UWB x‑axis.

```bash
# Remember to source the workspace before executing the following commands.
# Open the first terminal - initialize the system.
ros2 launch sebot_navigation sebot_navigation.launch.py

# Second terminal - run SLAM Toolbox to create the map.
ros2 launch sebot_navigation slam_online_async.launch.py

# Third terminal - teleoperate the robot while building the map.
ros2 run teleop_twist_keyboard teleop_twist_keyboard

# After the map is complete, save it.
ros2 run nav2_map_server map_saver_cli -f ~/ros2_ws/map
```

After the map is saved successfully, kill the first terminal and stop SLAM Toolbox in the second terminal. Then place the robot back to the origin position (anchor 1).

### 6.3 Navigation phase

Once the map is saved and the UWB–IMU frames are aligned, navigation can be started:

```bash
# Kill any previous instances and relaunch the robot system
ros2 launch sebot_navigation sebot_navigation.launch.py
# second terminal
ros2 launch sebot_navigation nav2_bringup.launch.py
```

RViz2 will be initialized together with this command, and then you can give the goal pose using the 2D Goal Pose tool in RViz2. You can also give the goal pose by executing this command:

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose "pose:
  header:
    frame_id: 'map'
    stamp:
      sec: 0
      nanosec: 0
  pose:
    position:
      x: 1.0
      y: 0.0
      z: 0.0
    orientation:
      x: 0.0
      y: 0.0
      z: 0.0
      w: 1.0"
```

Or you can use a very useful platform called **Foxglove** to not only give the goal pose, but also visualize and monitor the data from all sensors simultaneously, especially when your robot has a camera. Foxglove can show the robot’s 3D pose, LiDAR point clouds, IMU and UWB measurements, along with synchronized camera feeds, all in a single web‑based dashboard.

## 7. Waypoint Following

Define the waypoints in `~/ros2_ws/src/sebot_navigation/sebot_navigation/waypoint_publisher.py`.  
Each waypoint includes a pose in the map frame.

This allows the robot to automatically patrol a sequence of positions without manual intervention.

```bash
# Open one more terminal
ros2 run sebot_navigation waypoint_publisher
```

The saved map is loaded by Nav2, and the waypoint follower guides the robot through the predefined poses.

## 8. Practical Notes

- Remember to also change the code in `setup.py` file.
- Make sure ports used for Lidar, IMU, UWB connection are set correctly.
- Make sure the LiDAR scan topic name matches the one used in Nav2 parameters.
- Make sure the base frame name in Nav2 matches the TF frame used by the robot.
- Make sure the map file path in the launch file points to the correct `map.yaml`.
- The waypoint follower should use the same map frame (`map`) as the Nav2 planner.
- If the robot cannot reach a waypoint, first verify the map, TF, and LiDAR scan.
- **Nav2 parameters** should be adjusted according to your system. Those values are significantly different for diffrent robots with different sensor models. 
- The navigation accuracy of this system is limited by sensor noise and UWB measurement error. Under normal operating conditions, the error between the robot’s actual position and the pose in the `map` frame will typically be in the range of 10–15 cm.

## 9. Limitations Due to Raspberry Pi 5 Hardware

This system runs on a **Raspberry Pi 5**, which introduces hardware-related constraints that affect the entire stack:

- **Overheating under load**:  
  The Pi 5 can throttle its CPU when temperature rises, causing jitter and latency in sensor processing, localization, and control.

- **Limited processing power**:  
  The four-core CPU struggles with multiple concurrent ROS 2 nodes (SLAM Toolbox, Nav2, localization, and custom nodes) at high frequencies.

- **Reduced Nav2 node frequencies**:  
  To keep the system stable, the update frequency of the **controller server** and some other Nav2 nodes has been reduced (e.g., 5-10 Hz). This lowers CPU usage and throttling but slightly reduces responsiveness.

These limitations are documented here so that users understand that the chosen configuration (including reduced Nav2 node frequencies) is a **hardware-driven trade-off**, not a software design flaw.



 