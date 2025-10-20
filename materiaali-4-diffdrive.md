### Differential Drive

Differential Drive is a two-wheeled robotic locomotion mechanism where the robot is controlled by adjusting the rotational speeds of the wheels. One wheel can rotate faster, slower, or even in the opposite direction than the other, which allows the robot to change direction and turn in place.

Differential Drive is a simple and effective mechanism that controls the robot's movement using the speed and direction differences of two wheels. It is a popular solution especially in the ROS system, where the `cmd_vel` topic is used to define the robot's linear and angular velocity using the message type `geometry_msgs/msg/Twist`. This message type is standardized for mobile robots, especially for differential drive systems.

The `geometry_msgs/msg/Twist` message type contains two vector fields:

- linear: Describes linear velocity (m/s) on all three axes (x, y, z).
- angular: Describes angular velocity (rad/s) on all three axes (x, y, z).

For Differential Drive robots, the significant components are:

- linear.x: Linear velocity forward (positive) or backward (negative).
- angular.z: Angular velocity around the robot's vertical axis.

Other components (linear.y, linear.z, angular.x, and angular.y) are generally not used in a 2D environment.

While the `cmd_vel` topic controls the robot's speeds, the `odom` topic provides information about the robot's actual position and orientation. Odometry calculation publishes this information on the `odom` topic, which allows real-time tracking of the robot's position.

### Odometry

`/odom`-topic: This publishes information about the robot's position and orientation relative to the original starting point.

Odometry calculation in this case is based solely on the information produced by the motor encoders. It is important to note that this method is not completely accurate, as the interaction between the wheels and the ground, such as slippage and friction, inevitably causes errors in estimating position and movement. Although this calculation method does not guarantee perfect accuracy, it still provides a reliable basis for tracking the robot's position and movement. Since no other sensors are used in this example, encoder-based odometry is the robot's only available navigation method.

#### How Odometry Calculation Works in Brief

Odometry calculation is based on measuring the movements of the robot's wheels and utilizing this information to determine the robot's position and orientation (x, y, θ) over time.

- The distance traveled by a wheel is obtained by knowing the wheel's diameter and the encoder reading for one revolution.
- Difference in movement between the left and right wheels: The distance traveled by the left and right wheels is calculated.
  The difference between the wheels determines the robot's turning and change of direction.

**Wheels**

The wheel radius and the distance between the wheels have a significant impact on the movement and control of a differential drive robot. They directly affect the calculation of the robot's trajectory, speed, and angular velocity.

The image below illustrates how the size of the wheels and the distance between them affect the robot's movement when one wheel moves at a certain speed and the other remains stationary. For example, the motor is driven for 3 seconds at a speed of 0.1 m/s.

![turning radius](kuvat/turnradius.png)

- Wheel size:
  - A smaller wheel travels a shorter distance in one revolution.
  - A larger wheel travels a longer distance in the same number of revolutions.
- Distance between wheels:
  - Short distance: Produces a sharper turn, as the radius of the arc decreases.
  - Long distance: Makes the turn shallower, as a greater distance requires a longer arc to form.
- When calculating the distance traveled:
  - The distance traveled depends on the wheel size and turning radius:
    - Smaller wheel + short distance → short travel and tight curve.
    - Larger wheel + long distance → long travel and shallow curve.

**Encoder Class**

We create an auxiliary class `Encoder` in Python, which is responsible for managing and calculating encoder readings. In most encoders, the reading resets after the maximum reading, at which point the revolutions start over. This class accurately keeps track of the wheel's revolutions so that the wheel's absolute position can be calculated correctly even when the encoder reading overflows or resets.

**~/ros2_ws/src/diffdrive/diffdrive/encoder.py**

```python
import math

class Encoder():
  encoder_min =  -32768
  encoder_max =  32768
  encoder_range = encoder_max - encoder_min

  encoder_low_wrap = (encoder_range * 0.3) + encoder_min
  encoder_high_wrap = (encoder_range * 0.7) + encoder_min


  def __init__(self, wheel_radius, ticks_per_revolution):

    self.wheel_radius = wheel_radius
    self.ticks_per_revolution = ticks_per_revolution

    # wheel radius R = 0.1m
    # encoder resolution E = 1000 ticks / revolution

    # wheel circumference: 2 * pi * R
    # revolutions per meter = 1m / wheel circumference
    # ticks per meter = E * (1m / (2 * pi * R)) = E / (2 * pi * R)

    self.ticks_per_meter = self.ticks_per_revolution / (2 * math.pi * self.wheel_radius)

    self.offset = None
    self.encoder = None
    self.prev_encoder = None

    self.position = 0
    self.prev_position = None

    self.multiplier = 0


  def update(self, encoder):
    if self.encoder == None:
      self.offset = encoder
      self.prev_encoder = encoder

    self.encoder = encoder

    # In encoders that measure rotation, there is often a limited range of values (e.g., 0–4095 for a 12-bit encoder).
    # When the encoder value "wraps around" (e.g., 4095 -> 0 or vice versa), this logic ensures that the correct
    # position is maintained by tracking full revolutions.
    #
    # self.encoder: Current encoder reading.
    # self.prev_encoder: Previous encoder reading.
    # self.encoder_low_wrap: Threshold value near the lower limit (0 + margin)
    # self.encoder_high_wrap: Threshold value near the upper limit (4095 − margin)
    # self.multiplier: Counter that tracks full revolutions
    #
    # i.e., when the previous value is in the upper range (e.g., 4090-4095) and the current value is in the lower range
    # (e.g., 0-5), then the absolute position increases, and in the other direction, the absolute position decreases.
    # In all other cases, we are on the same revolution.

    if (self.encoder < self.encoder_low_wrap) and (self.prev_encoder > self.encoder_high_wrap):
      self.multiplier += 1
    if (self.encoder > self.encoder_high_wrap) and (self.prev_encoder < self.encoder_low_wrap):
      self.multiplier -= 1

    self.position = self.encoder + self.multiplier * self.encoder_range - self.offset

    self.prev_encoder = self.encoder


  def deltam(self):
    if self.prev_position == None:
      self.prev_position = self.position
      return 0
    else:
      d = (self.prev_position - self.position) / self.ticks_per_meter
      self.prev_position = self.position
      return d
```

**Transformation**

Transformations are used to calculate the robot's position and orientation relative to different coordinate systems. When we want to visualize the robot's movement in the RViz environment, it is important that the transformation between the `odom` and `base_footprint` frames is correctly defined. This transformation connects the robot's physical location (`base_footprint`) to its relative position at the odometry starting point (`odom`).

**RViz Global Options and Fixed Frame**

Fixed Frame determines which coordinate system (frame) all other frames are displayed in RViz.

If we set the Fixed Frame value to `base_footprint`:

- The robot's position is displayed relative to itself, meaning no movement is visualized, even if the robot is moving.
- This is because the base_footprint always stays on the robot's body and follows it.

If we set the Fixed Frame value to `odom`:

- The robot's movement is visualized relative to the `odom` frame, which serves as the odometry starting point.
- This allows tracking the robot's actual movement on the screen.

**How does transformation affect it?**

When the robot moves, the `odom` frame stays in place, and the `base_footprint` moves relative to it. The `odom` -> `base_footprint` transformation is continuously updated, and RViz uses this information to draw the robot's position and orientation.

The location of transformation calculation and publishing depends on the robot's system architecture, as well as the required positioning accuracy and possible integration with other sensors, such as IMU or LiDAR.

Transformations can be implemented directly in the `odom` node if odometry is the system's only source of location. This approach is particularly suitable for simple systems that do not use other sensors.

If, however, multiple sensors are used, it is recommended to use the EKF (Extended Kalman Filter) node of the `robot_localization` package, which is part of commonly used ROS2 packages. EKF combines all available information, such as encoders, IMU, LiDAR, and GPS, and produces a more accurate estimate of the robot's position and orientation. This improves positioning accuracy and compensates for possible errors of individual sensors.

**Situation with IMU (Inertial Measurement Unit):**

IMU provides more precise data about the robot's actual movement, which helps compensate for errors caused by wheel slip.

Angular Velocity (Yaw-Rate):
IMU's gyroscope measures angular velocities (e.g., rotation around the z-axis).
If one wheel slips and the wheel encoders provide incorrect angular velocity information, the IMU can identify the actual angular velocity and correct the direction and position information.
This prevents distortion from accumulating in the robot's orientation (yaw).

Acceleration (Linear Acceleration)
IMU's accelerometers measure the robot's movement acceleration in the x and y directions.
During wheel slip, the linear movement estimated by the encoders may be incorrect, but the IMU can identify the actual acceleration and help estimate the true speed.
This reduces errors in the robot's positioning.

**Situation with LiDAR (Light Detection and Ranging):**

LiDAR complements the limitations of wheel encoders by providing accurate information about the robot's environment.

Distance Measurement: LiDAR maps the environment by measuring distances to obstacles and structures around the robot.

Static References: LiDAR can identify permanent environmental features, such as walls and furniture, which are used to determine the robot's position relative to the environment.

**Correcting Drift**

By utilizing absolute positioning methods (such as camera- or LiDAR-based SLAM, GNSS positioning, UWB positioning), the robot's actual movement relative to the environment can be detected and the accumulated error of the wheel encoders can be corrected.

For example, if the wheel encoders indicate that the robot has moved to a certain point, but the LiDAR's observation of the environment indicates otherwise, the positioning can be corrected by combining the information. In the case of ROS2, a common way to do such a correction is to feed the data streams of different positioning methods to the EKF filter of the `robot_localization` package.

Now that encoders are our only source of location, we will implement the publishing of transformations directly in the `odom` node, which is a simple and effective solution.

**~/ros2_ws/src/diffdrive/diffdrive/odom.py**

```python
import rclpy
from rclpy.node import Node

from nav_msgs.msg import Odometry
from tf_transformations import quaternion_from_euler

from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

from motordriver_msgs.msg import MotordriverMessage

import math

try:
    from .encoder import Encoder
except:
    from encoder import Encoder


class OdomNode(Node):
  def __init__(self):
    super().__init__('odom_node')

    # Read parameters
    self.declare_parameter('wheel_radius', 0.1)
    self.declare_parameter('wheel_base', 0.5)
    self.declare_parameter('ticks_per_revolution', 1075)

    # Get parameter values
    self.wheel_radius = self.get_parameter('wheel_radius').value
    self.wheel_base = self.get_parameter('wheel_base').value
    self.ticks_per_revolution = self.get_parameter('ticks_per_revolution').value

    self.get_logger().info(f'Wheel radius: {self.wheel_radius}')
    self.get_logger().info(f'Distance between wheels: {self.wheel_base}')
    self.get_logger().info(f'Sensor revolution: {self.ticks_per_revolution}')

    ## Let's take a prefix for the frame as a parameter, or if no parameter is provided, take it from the namespace information.
    #self.declare_parameter('frame_prefix', '')
    #frame_prefix_param = self.get_parameter('frame_prefix').get_parameter_value().string_value
    #if frame_prefix_param:
    #    self.frame_prefix = frame_prefix_param + '_'
    #else:
    #    ns = self.get_namespace().strip('/')
    #    self.frame_prefix = f'{ns}_' if ns and ns != '' else ''

    #if self.frame_prefix:
    #        self.get_logger().info(f'Using frame prefix: "{self.frame_prefix}"')


    self.left_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution)
    self.right_encoder = Encoder(self.wheel_radius, self.ticks_per_revolution)

    self.odom_theta = 0.0
    self.odom_x = 0.0
    self.odom_y = 0.0

    self.motor_subscriber = self.create_subscription(
        MotordriverMessage,
        'motor_data',
        self.update_encoders_callback,
        10
    )

    self.odom_publisher = self.create_publisher(
        Odometry,
        'odom',
        10
    )

    # TransformBroadcaster needs a reference to the main class to get the necessary context
    # (node settings or other shared data). This happens by passing self as a parameter.
    self.tf_broadcaster = TransformBroadcaster(self)

    self.prev_time = self.get_clock().now().nanoseconds

    timer_period = 0.1 # Seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
    self.update = True

  def update_encoders_callback(self, message):
    # Store the information in the message so it can be processed in timer_callback
    self.left_encoder.update(message.encoder1)
    self.right_encoder.update(-message.encoder2)
    self.update = True

  def timer_callback(self):
    if not self.update: return
    self.update = False
    current_time = self.get_clock().now().nanoseconds
    elapsed = (current_time - self.prev_time)/1000000000
    self.prev_time = current_time

    d_left= self.left_encoder.deltam()
    d_right = self.right_encoder.deltam()

    # The distance traveled (delta_distance) is calculated by taking the distance traveled by the left and right wheels
    # divided by two. The distance the robot moves straight along the centerline (the axis dividing the robot in the middle).
    # The change in angle (delta_theta) is calculated by taking the difference between the distance traveled by the left and right wheels and
    # dividing it by the distance between the wheels
    # If the wheels move equally in the same direction (d_left=d_right -> delta_theta=0), the robot moves
    # straight forward or backward.
    # If the wheels move equally in opposite directions (d_left=-d_right -> delta_distance=0), the robot spins
    # in place.
    delta_distance = (d_left + d_right) / 2.0
    delta_theta = (d_left - d_right) / self.wheel_base

    if delta_distance != 0:
      robot_x = math.cos( delta_theta ) * delta_distance
      robot_y = -math.sin( delta_theta ) * delta_distance
      self.odom_x = self.odom_x + ( math.cos( self.odom_theta ) * robot_x - math.sin( self.odom_theta ) * robot_y )
      self.odom_y = self.odom_y + ( math.sin( self.odom_theta ) * robot_x + math.cos( self.odom_theta ) * robot_y )

    linear_y = delta_distance * math.cos(self.odom_theta) / elapsed
    linear_x = delta_distance * math.sin(self.odom_theta) / elapsed
    angular_z = delta_theta / elapsed

    self.odom_theta = delta_theta + self.odom_theta

    odom_msg = Odometry()
    odom_msg.header.stamp = self.get_clock().now().to_msg()
    #odom_msg.header.frame_id = self.frame_prefix + 'odom' # Add a prefix to the frame name according to the namespace (or parameter).
    #odom_msg.child_frame_id = self.frame_prefix + 'base_footprint'
    odom_msg.header.frame_id = 'odom'
    odom_msg.child_frame_id = 'base_footprint'

    # pose contains two parts:
    # position (geometry_msgs/Point)
    #  x, y, z: Robot's position in the coordinate system.
    # orientation (geometry_msgs/Quaternion)
    #  x, y, z, w: Robot's orientation in quaternion format (3D rotation).
    odom_msg.pose.pose.position.x = self.odom_x ##
    odom_msg.pose.pose.position.y = self.odom_y ##
    odom_msg.pose.pose.position.z = 0.0

    quat = quaternion_from_euler(0.0, 0.0, self.odom_theta)
    odom_msg.pose.pose.orientation.x = quat[0] ##
    odom_msg.pose.pose.orientation.y = quat[1] ##
    odom_msg.pose.pose.orientation.z = quat[2] ##
    odom_msg.pose.pose.orientation.w = quat[3] ##

    # Speeds (optional, not used in this application)
    odom_msg.twist.twist.linear.x = linear_x
    odom_msg.twist.twist.linear.y = linear_y
    odom_msg.twist.twist.angular.z = angular_z

    # Publish odometry message
    self.odom_publisher.publish(odom_msg) ##

    t = TransformStamped()
    t.header.stamp = self.get_clock().now().to_msg()
    #t.header.frame_id = self.frame_prefix + 'odom'
    #t.child_frame_id = self.frame_prefix + 'base_footprint'
    t.header.frame_id = 'odom'
    t.child_frame_id = 'base_footprint'

    t.transform.translation.x = self.odom_x ##
    t.transform.translation.y = self.odom_y ##
    t.transform.translation.z = 0.0

    # z: Part of the quaternion related to rotation around the z-axis. This alone is not an angle,
    # but part of the combined representation of the axis and angle of rotation.
    # w: The scalar component of the quaternion, which determines how much of the rotation comes from around the axis.
    # In relation to other quaternion components, this determines the angle.

    t.transform.rotation.z = math.sin(self.odom_theta / 2.0) ##
    t.transform.rotation.w = math.cos(self.odom_theta / 2.0) ##

    # Publish transformation
    self.tf_broadcaster.sendTransform(t) ##


def main(args=None):
  rclpy.init(args=args)

  odom_node = OdomNode()

  try:
    rclpy.spin(odom_node)
  except KeyboardInterrupt:
    pass
  finally:
    odom_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()
```

Now we can test the program's functionality. Run the following commands in different terminals and ensure that all necessary nodes are running. If you follow your robot in RViz and set the Fixed Frame to `[SeBot_namespace]` `/odom`, the robot should move in the visualization view as expected.

```bash
# Start motordriver node (remember to source)
ros2 run motordriver motordriver
#ros2 run motordriver motordriver [--ros-args -r __ns:=/[SeBot_namespace]]

# Test odom node
python3 odom.py
#python3 odom.py --ros-args -r __ns:=/[SeBot_namespace]

# Print what /odom topic shows
ros2 topic echo /odom
#ros2 topic echo /[SeBot_namespace]/odom

# Move forward
ros2 topic pub /motor_command std_msgs/String "{data: 'SPD;100;-100;'}"
#ros2 topic pub /[SeBot_namespace]/motor_command std_msgs/String "{data: 'SPD;100;-100;'}"

# Move backward
ros2 topic pub /motor_command std_msgs/String "{data: 'SPD;-100;100;'}"

# Spin in place
ros2 topic pub /motor_command std_msgs/String "{data: 'SPD;100;100;'}"

# Drive in a circle
ros2 topic pub /motor_command std_msgs/String "{data: 'SPD;150;-100;'}"
```

When both `odom` and `transformation` are working correctly, you can visualize these in RViz, where the red Odometry arrow and the robot model point in the same direction and are aligned.
![](kuvat/rviz/ok.png)

In the code, there are lines followed by `##`. By commenting out these lines differently and restarting the program, you can see how they affect the operation of odometry and transformation.

Publish only the /odom topic, the transformation is in the last place it was published
![](kuvat/rviz/odom.png)

Only rotation in /odom topic
![](kuvat/rviz/odomz.png)

Only position in /odom topic
![](kuvat/rviz/tf.png)

Only position from transformation
![](kuvat/rviz/tfxy.png)

Only rotation from transformation
![](kuvat/rviz/tfz.png)

When you publish the transformation chain `odom` -> `base_footprint`, it appears in the TF-tree structure, which describes the relationships between all TF frames. This is an essential part of tracking the robot's position relative to the local odom frame.

![turning radius](kuvat/frames2.png)

When moving towards autonomous driving, a `map` frame is also added to the TF-tree. This forms a transformation chain `map` -> `odom` -> `base_footprint`, allowing the robot's position to be accurately tracked both on the map and in the local coordinate system. This enables viewing the robot's progress both locally and globally. If this exercise is done with many SeBots in the same `ROS_DOMAIN_ID`, it is necessary to create a somewhat artificial `map` frame. A model of this will be presented later in connection with the `launch` file.

### Twist

Next, we will move on to handling the `cmd_vel` topic. It allows us to control the robot more simply by directly defining linear velocity and angular velocity. This approach removes the need to control motors separately and makes motion control more intuitive.

The use of the `cmd_vel` topic together with the Nav2 system enables autonomous driving of the robot. Nav2 controls the robot by sending linear and angular velocity commands to the `cmd_vel` topic, allowing the robot to navigate independently based on a defined map and path.

In practice, the `cmd_vel` node converts the linear velocity `linear.x` and angular velocity `angular.z` into wheel-specific speed commands that the `motor_command` topic understands: `SPD;vel_l;vel_r;`

**~/ros2_ws/src/diffdrive/diffdrive/cmd_vel.py**

```python
import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import String

import math

class CmdVelNode(Node):
  def __init__(self):
    super().__init__('cmd_vel_node')

    # Read parameters
    self.declare_parameter('wheel_radius', 0.1)
    self.declare_parameter('wheel_base', 0.5)
    self.declare_parameter('ticks_per_revolution', 1075)

    # Get parameter values
    self.wheel_radius = self.get_parameter('wheel_radius').value
    self.wheel_base = self.get_parameter('wheel_base').value
    self.ticks_per_revolution = self.get_parameter('ticks_per_revolution').value

    self.get_logger().info(f'Wheel radius: {self.wheel_radius}')
    self.get_logger().info(f'Distance between wheels: {self.wheel_base}')
    self.get_logger().info(f'Sensor revolution: {self.ticks_per_revolution}')

    self.cmd_vel_subscriber = self.create_subscription(
        Twist,
        'cmd_vel',
        self.cmd_vel_callback,
        10
    )

    self.mc_publisher = self.create_publisher(
        String,
        'motor_command',
        10
    )

  def mps_to_spd(self,mps):
    # convert m/s to motor controller spd value
    pid_freq = 10 # Motor controller updates at 10Hz

    # angular velocity (rad/s)
    radps = mps / self.wheel_radius

    # RPM
    rpm = radps * ( 60 / ( 2 * math.pi ) )

    spd = rpm * (self.ticks_per_revolution / 60 / pid_freq)
    return spd

  def cmd_vel_callback(self, msg):
    # mps_l = left wheel m/s
    # mps_r = right wheel m/s
    mps_l = +(msg.linear.x + (msg.angular.z * self.wheel_base / 2.0))
    mps_r = -(msg.linear.x - (msg.angular.z * self.wheel_base / 2.0))

    string_msg = String()
    string_msg.data = "SPD;%i;%i;"%(self.mps_to_spd(mps_l), self.mps_to_spd(mps_r))

    self.mc_publisher.publish(string_msg)

def main(args=None):
  rclpy.init(args=args)

  cmdvel_node = CmdVelNode()

  try:
    rclpy.spin(cmdvel_node)
  except KeyboardInterrupt:
    pass
  finally:
    cmdvel_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()


if __name__ == '__main__':
  main()
```

Now it's time to try the program. Keep the `motordriver` and `odom` nodes and RViz running. This time, send messages to the `cmd_vel` topic instead of directly using `motor_command` topics. This way you can test the robot's control using linear and angular velocity.

```bash
# Start cmd_vel node
python3 cmd_vel.py

# Robot moves forward at 0.5 m/s:
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0},	angular: {x: 0.0, y: 0.0, z: 0.0}}"
# Same considering namespace:
ros2 topic pub /[SeBot_namespace]/cmd_vel geometry_msgs/Twist "{linear: {x: 0.5, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 0.0}}"


# Robot turns counter-clockwise in place (angular velocity 1 rad/s):
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.0, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: 1.0}}"

# Robot moves in a clockwise arc (forward + turn):
ros2 topic pub /cmd_vel geometry_msgs/Twist "{linear: {x: 0.3, y: 0.0, z: 0.0}, angular: {x: 0.0, y: 0.0, z: -0.5}}"
```

### Additional task: Teleop_twist_keyboard

Driving the robot with individual command line prompts is laborious. The actual idea is, of course, that the robot's control system gives these commands more or less autonomously (\"autonomous driving\"), but within the scope of this exercise, a good intermediate step is to introduce a ROS2 package that enables manual remote control. The easiest way is to try controlling with the keyboard, which is made possible by [teleop_twist_keyboard](https://index.ros.org/r/teleop_twist_keyboard/).

```bash
sudo apt install ros-jazzy-teleop-twist-keyboard
ros2 run teleop_twist_keyboard teleop_twist_keyboard

#ros2 run teleop_twist_keyboard teleop_twist_keyboard.py --ros-args -r /cmd_vel:=/[SeBot_namespace]/cmd_vel # If namespace is in use

```

`teleop_twist_keyboard` can also be configured to publish twist messages to another topic using the parameter `--ros-args --remap cmd_vel:=[some_other_topic]`. If only one SeBot is involved in the exercise or each operates in its own `ROS_DOMAIN_ID`, we use the `/cmd_vel` topic by default, and there should be no need to adjust the topic, as `/cmd_vel` is a commonly used standard in ROS 2.

If you want to control the robot with a game controller, you should check out the `[teleop_twist_joy](https://index.ros.org/r/teleop_twist_joy/#jazzy)` package. This is installed and run with the commands

```bash
apt install ros-jazzy-teleop-twist-joy
ros2 launch teleop_twist_joy teleop-launch.py joy_config:='[select controller configuration, for example \'xbox\']'
```

> Note that teleop_twist_joy is launched with the `launch`, not `run` command. In addition, you must ensure that the configuration matches the connected controller. Options can be found at [https://github.com/ros2/teleop_twist_joy/tree/rolling/config](https://github.com/ros2/teleop_twist_joy/tree/rolling/config).

### Comparison of PWM and PID control

If we want to compare the robot's operation between PWM control and PID-controlled speed, we can simply change one line of code that determines the control type.

```python
string_msg.data = "SPD;%i;%i;"%(vel_l,vel_r)
```

to

```python
string_msg.data = "PWM;%i;%i;"%(vel_l,vel_r)
#(vel_l and vel_r may require small coefficients,
#if the motors do not rotate at all with small values
#or alternatively only larger numbers for x and z values of the topic)
```

All good, update `setup.py` and compile the package as part of the system:

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
            'odom = diffdrive.odom:main',
            'cmd_vel = diffdrive.cmd_vel:main',
        ],
    },
)
```

```bash
cd ~/ros2_ws
colcon build --packages-select diffdrive

# Test operation
ros2 run diffdrive odom
ros2 run diffdrive cmd_vel
#ros2 run diffdrive odom --ros-args -r __ns:=/[SeBot_namespace]
#ros2 run diffdrive cmd_vel --ros-args -r __ns:=/[SeBot_namespace]

# odom.py and cmd_vel.py files contain sections where script variables get values as startup parameters. These parameters can also be input from an external file during startup.

# Here is an example where parameters are retrieved from the ~/ros2_ws/config/params.yaml file. The necessary content for this file is created below.
ros2 run diffdrive odom --ros-args --params-file ~/ros2_ws/config/params.yaml
```

### Launch files

In ROS 2, launch files enable launching one or more nodes simultaneously. We will update the launch file we created earlier, which launched the URDF node, by adding our `odom` and `cmd_vel` nodes to it as well, so that all necessary functions can be launched with a single command.

**~/ros2_ws/src/diffdrive/launch/diffdrive.launch.py**

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    # NAMESPACE = 'SeBotxx' # replace xx with your SeBot's identifier, e.g., the last byte of the IP address.
    # FRAME_PREFIX = NAMESPACE+"_" # create the value for the frame_prefix parameter supported by robot_state_publisher

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
            #namespace = NAMESPACE,
            #parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc, 'frame_prefix': FRAME_PREFIX}],
            parameters=[{'use_sim_time': use_sim_time, 'robot_description': robot_desc}],
            #arguments=[urdf] # 26.5.2025 this line is unnecessary, as robot_state_publisher does not parse command line arguments.
            ),

        Node(
            package='tf2_web_republisher_py',
            executable='tf2_web_republisher',
            name='tf2_web_republisher',
            #namespace = NAMESPACE,
            output='screen',
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

`odom.py` and `cmd_vel.py` files contained lines such as:

```python
    self.wheel_radius = self.get_parameter('wheel_radius').value
```

In the launch file, we now defined `parameters=["~ros2_ws/config/params.yaml"]` which means we can set parameters there that we can update without having to compile the system; only restarting the node is sufficient.

**~/ros2_ws/config/params.yaml**

```yaml
motordriver_node:
  ros__parameters:
    simulation: False
odom_node:
  ros__parameters:
    wheel_radius: 0.2
    wheel_base: 0.6
    ticks_per_revolution: 1000
cmd_vel_node:
  ros__parameters:
    wheel_radius: 0.3
    wheel_base: 0.7
```

##### Compile (build environment)

```bash
cd ~/ros2_ws
colcon build --packages-select diffdrive
```

##### Source

```bash
source ~/ros2_ws/install/setup.bash
```

##### Launch

```bash
ros2 launch diffdrive diffdrive.launch.py
```

##### Test (in another terminal)

```bash
ros2 topic pub /motor_command std_msgs/String "{data: 'SPD;100;100;'}"
```

### Automatic startup when robot starts

To automatically launch a ROS2 package when the system starts, you can use a systemd service in Linux systems. ROS2 packages require environment loading, which means that the setup commands for the ROS2 distribution (`/opt/ros/jazzy/setup.bash`) and the workspace (`install/setup.bash`) must be executed automatically before launching the node or launch file.

Create a bash script that the systemd service will launch:

**/home/ros2/ros2_ws/autostart.sh**

```bash
#!/bin/bash

# Load ROS2 environment
source /opt/ros/jazzy/setup.bash

# Load workspace environment
source /home/ros2/ros2_ws/install/setup.bash

# Execute launch file
ros2 launch diffdrive diffdrive.launch.py
```

Create a .service file that is controlled by the systemctl command. Note, editing must be done as sudo.

```bash
sudo nano /etc/systemd/system/ros2_motordriver.service
```

**/etc/systemd/system/ros2_motordriver.service**

```bash
[Unit]
Description="ROS2 Motor Driver Autostart"
After=network.target

[Service]
Type=simple
User=ros2
ExecStart=/home/ros2/ros2_ws/autostart.sh
Restart=always

Environment="PYTHONUNBUFFERED=1"
# means that Python is executed without output buffering (unbuffered mode).
# This particularly affects stdout and stderr streams (i.e., outputs and error messages),
# which might otherwise be delayed due to the buffer.

[Install]
WantedBy=multi-user.target
```

```bash
# start script
sudo systemctl start ros2_motordriver.service

# set script to start when system boots
sudo systemctl enable ros2_motordriver.service

# restart (e.g., if you change parameters)
sudo systemctl restart ros2_motordriver.service

# check status
systemctl status ros2_motordriver.service

# log
journalctl -u ros2_motordriver.service -f
```

### Additional Task: All Ready LED

Examine the code below and figure out its operation. An LED and a resistor are needed, connected to Raspberry Pi's GPIO interface pins 16 (GPIO-23) and 14 (GND).

```python
import rclpy
from rclpy.node import Node
import time
import lgpio

# GPIO-23
LED_PIN = 23

# Open GPIO chip (default for Raspberry Pi)
chip = lgpio.gpiochip_open(4)

# Set LED pin as output
lgpio.gpio_claim_output(chip, LED_PIN)

class NodeChecker(Node):
    def __init__(self):
        super().__init__('node_checker')

    def get_running_nodes(self):
        # Get all nodes
        node_names_and_namespaces = self.get_node_names_and_namespaces()
        nodes = [name for name, _ in node_names_and_namespaces]
        return nodes

def main():
    rclpy.init()
    node = NodeChecker()

    active = False

    lgpio.gpio_write(chip, LED_PIN, 0)

    try:
      while True:
          nodes = node.get_running_nodes()
          check_nodes = ['robot_state_publisher', 'motordriver_node', 'odom_node', 'cmd_vel_node']
          active = set(check_nodes).issubset(set(nodes))

          if active:
              lgpio.gpio_write(chip, LED_PIN, 1)

          else:
              lgpio.gpio_write(chip, LED_PIN, 0)

          time.sleep(1)

    except KeyboardInterrupt:
      pass
    finally:
      lgpio.gpio_write(chip, LED_PIN, 0)

      node.destroy_node()
      if rclpy.ok():
        rclpy.shutdown()

if __name__ == '__main__':
    main()
```

![piled](kuvat/pi_led.jpeg)

- Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control2025
