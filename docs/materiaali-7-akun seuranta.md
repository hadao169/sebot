## Extra: Battery voltage monitoring and alert light

LiPo battery condition deteriorates rapidly if the cell-specific voltage drops too low. If the limit value is set to 3.3V/cell, the voltage of the three-cell battery used in SeBot should not drop below approximately 10V (unless more advanced cell-specific voltage monitoring is used). Let's develop SeBot's functionalities so that if the voltage drops below the set level, an alert light will turn on:

1. Create a voltage divider circuit that allows the Arduino to read the battery voltage in addition to the motor data.
2. Feed this information as part of the string reporting the motor status to the Raspberry Pi, where the motordriver-node parses the information as part of the /motor_data topic.
3. Relay the information with a separate node to its own /battery_level topic and
4. monitor the voltage level with a node that delivers information about the alert status to the /battery_alert topic and turns on the alert light.

### Voltage divider circuit

The Arduino's analog input pin must not be supplied with more than 5V voltage. The nominal voltage of the battery is 12V, so it must be scaled so that a 12V voltage appears as slightly less than 5V on the Arduino's A0 pin. This is most conveniently done with a simple [voltage divider circuit](https://en.wikipedia.org/wiki/Voltage_divider).

![Voltage Divider](./kuvat/jannitteenjako.png)

Image: Voltage divider circuit and necessary calculation formulas.

The resistors R1 and R2 must be chosen so that their mutual ratio gives a voltage U2 that is always less than 5V at Arduino pin A0. Secondly, the total resistance should be quite large so that this "unnecessary" power consumption remains as small as possible.

If 10 k $\Omega$ is chosen for resistor R1 and the maximum battery voltage is U = 12.6V, then computationally, resistor R2 should be 6.6 k $\Omega$. However, we want some safety margin, so a good choice is R2 = 4.7 k $\Omega$. In this case, U2_max = U_max \* R2/(R1+R2) = 4.0 V.

### Arduino

Add to the Arduino's `motorcontroller.ino` file information about using the A0 pin as an analog input, reading the value from it and scaling it to a voltage value with the `ReadBatteryVoltage()` function, and sending this voltage value as part of the other string delivered to the Raspberry Pi.

If you wish, you can measure the resistance of the resistors you are using with a multimeter to refine the voltage measurement result.

**/opt/nomga/arduino/motorcontroller/motorcontroller.ino**

```c
#include "Motor.h"

const int voltagePin = A0;         // Analog input on pin A0
const float R1 = 9820.0;          // nominal resistance 10k ohms
const float R2 = 4720.0;           // nominal resistance 4.7k ohms
const float voltageScale = (R1 + R2) / R2; // ~3.13
...
```

```c
...
void sendData() {
  Serial.print(motor1.getEncoder());
  Serial.print(";");
  Serial.print(motor2.getEncoder());
  Serial.print(";");
  Serial.print(motor1.getSpeed());
  Serial.print(";");
  Serial.print(motor2.getSpeed());
  Serial.print(";");
  Serial.print(motor1.getMotorSpeed());
  Serial.print(";");
  Serial.print(motor2.getMotorSpeed());
  Serial.print(";");
  Serial.print(readBatteryVoltage(), 2); // Battery voltage with two decimal places
  Serial.print("\n");
}

float readBatteryVoltage() {
  int raw = analogRead(voltagePin);            // 0–1023
  float voltage = (raw / 1023.0) * 5.0;         // Convert to voltage
  return voltage * voltageScale;               // Scale to actual voltage.
}
```

Save the file and compile and upload it to the Arduino's memory by running the commands

```bash
/opt/nomga/arduino/compile.sh
/opt/nomga/arduino/upload.sh
```

### Reading voltage in ROS2 environment

Arduino now provides voltage information as the last field of its string. In SeBot's architecture, reading this should be done in the same context as reading motor data, i.e., in the `motordriver` node. This information can be published at the same time as other `/motor_data` topic information if we update its data type with one additional field. (Another, ultimately more straightforward option would be to publish the battery voltage information directly in its own node. However, in this exercise, we want to illustrate republishing topics in a separate node. As your own exercise, you can consider how to skip this intermediate step.)

#### MotordriverMessage update

First, update the data type by adding one `float32` type field to the end of the file.
**~/ros2_ws/src/motordriver_msgs/msg/MotordriverMessage.msg**

```
int32 encoder1
int32 encoder2
int32 speed1
int32 speed2
int32 pwm1
int32 pwm2
float32 battery
```

#### motordrive node update

After this, modify the `motordriver` node so that it also takes this added field into account
**~/ros2_ws/src/motordriver/motordriver/motordriver.py**

```python
...
    # The constructor of the MotordriverNode class is updated to include voltage simulation, if running in simulation.
    # if the simulation parameter is not found, it defaults to False
    self.declare_parameter('simulation', False)
    self.simulation = self.get_parameter('simulation').value
    self.get_logger().info(f'Starting motor_controller in simulation: {self.simulation}')
    if self.simulation:
      self.arduino = SimSerial()
      self.voltageDifference = 0
      self.startingVoltage = 12.6
    else:
      self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
      if not self.arduino.isOpen():
        raise Exception("No connection to motor controller")
...
  def timer_callback(self):
    # Create a message
    if self.msg != "x\n":
        self.arduino.write(self.msg.encode())


    if self.timercount == 11:
        if self.msg == "x\n":
            self.arduino.write(self.msg.encode())
        self.msg = "x\n"

        self.timercount = 0
        if self.arduino.inWaiting()>0:
          while self.arduino.inWaiting()>0:
            answer=self.arduino.readline().decode("utf8").split(";")
            if(self.simulation):
              self.voltageDifference -= 0.001
              answer.append(float(self.startingVoltage+self.voltageDifference))
          msg = MotordriverMessageBattery()

          try:
            msg.encoder1 = int(answer[0])
            msg.encoder2 = int(answer[1])
            msg.speed1 = int(answer[2])
            msg.speed2 = int(answer[3])
            msg.pwm1 = int(answer[4])
            msg.pwm2 = int(answer[5])
            msg.battery = float(answer[6])
            # Publish the message
            self.publisher.publish(msg)
          except Exception as err:
            self.get_logger().info(f'Error: {err}')
            pass

    self.timercount += 1
...
```

#### New `battery` package

For the purpose of this exercise, we will create a new ROS2 package in which we will create two separate nodes:

1. `battery_republish` which extracts battery voltage information and publishes it to its own topic `/battery_voltage` and
2. `battery_alert` which reads this topic and, upon detecting that the voltage has dropped below a set alert threshold, publishes an alert message on the `/battery_alert` topic. In addition, the node turns on an alert light.

Create a new package `battery`

```bash
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python battery
cd ~/ros2_ws/src/battery/battery
```

Create two files in the said directory:
**~/ros2_ws/src/battery/battery/battery_republish.py**

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import time

from motordriver_msgs.msg import MotordriverMessage

from std_msgs.msg import Float32

class BatteryRedirector(Node):
    def __init__(self):
        super().__init__('battery_redirector')
        self.declare_parameter('battery_check_interval', 10.0) # Parameter for voltage reading interval, seconds.
        self.publish_interval = self.get_parameter('battery_check_interval').value

        self.sub = self.create_subscription(MotordriverMessage, '/motor_data', self.callback, 10)
        self.pub = self.create_publisher(Float32, '/battery_voltage', 10)
        self.previous_time = time.time()
        self.get_logger().info(f"Battery voltage reading time set to {self.publish_interval:.2f} s")

    def callback(self, msg):
        time_now = time.time()
        time_interval = time_now - self.previous_time
        if time_interval > self.publish_interval:
            battery_msg = Float32()
            battery_msg.data = msg.battery
            self.pub.publish(battery_msg)
            self.previous_time = time_now

def main(args=None):
  rclpy.init(args=args)
  batteryredirector_node = BatteryRedirector()
  try:
    rclpy.spin(batteryredirector_node)
  except KeyboardInterrupt:
    pass
  finally:
    batteryredirector_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()

```

**~/ros2_ws/src/battery/battery/battery_alert.py**

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import time
from std_msgs.msg import Bool, Float32

import lgpio

class BatteryAlert(Node):
    def __init__(self):
        super().__init__('battery_alert_node')

        self.declare_parameter('threshold', 12.0) # Default value 12.0 V, this is quickly met even with a full battery when starting.
        self.threshold = self.get_parameter('threshold').get_parameter_value().double_value
        self.get_logger().info(f"Battery voltage lower limit set to {self.threshold:.2f} V")

        self.sub = self.create_subscription(Float32, '/battery_voltage', self.voltage_callback, 10)
        self.sub_alert = self.create_subscription(Bool, '/battery_alert', self.alert_callback, 10)
        self.pub = self.create_publisher(Bool, '/battery_alert', 10)
        self.previous_alert_state = False

        # Publish False once by default in /battery_alert, so that something is definitely visible there.
        battery_alert_msg = Bool()
        battery_alert_msg.data = self.previous_alert_state
        self.pub.publish(battery_alert_msg)

        # Define GPIO pin for alert LED
        self.LED_PIN = 18
        # Select GPIO chip (standard for Raspberry Pi)
        self.chip = lgpio.gpiochip_open(4)
        # Set LED_PIN as output
        lgpio.gpio_claim_output(self.chip, self.LED_PIN)
        # Initialize LED_PIN to low (zero)
        lgpio.gpio_write(self.chip, self.LED_PIN, 0)

    # This callback is called when messages arrive on the /battery_alert topic.
    def alert_callback(self, msg):
        if msg.data == True:
            pass
            lgpio.gpio_write(self.chip, self.LED_PIN, 1)
        else:
            pass
            lgpio.gpio_write(self.chip, self.LED_PIN, 0)

    def voltage_callback(self, msg):
        if msg.data < self.threshold:
            alert_state = True
        else:
            alert_state = False

        if self.previous_alert_state != alert_state: # Publish /battery_alert information only if it has changed from previous.
            battery_alert_msg = Bool()
            battery_alert_msg.data = alert_state
            self.pub.publish(battery_alert_msg)
            self.previous_alert_state = alert_state

def main(args=None):
  rclpy.init(args=args)
  batteryalert_node = BatteryAlert()

  try:
    rclpy.spin(batteryalert_node)
  except KeyboardInterrupt:
    pass

  finally:
      batteryalert_node.destroy_node()
      lgpio.gpio_write(batteryalert_node.chip, batteryalert_node.LED_PIN, 0)
      lgpio.gpiochip_close(batteryalert_node.chip)
      if rclpy.ok():
          rclpy.shutdown()

if __name__ == '__main__':
  main()


```

Update `setup.py` so that we can launch the nodes with the `ros2 run` command.

**~/ros2_ws/src/battery/setup.py**

```python
from setuptools import find_packages, setup

package_name = 'battery'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='sebot',
    maintainer_email='sebot@todo.todo',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'battery_republish = battery.battery_republish:main',
            'battery_alert = battery.battery_alert:main',
        ],
    },
)
```

Connect the LED and its current-limiting resistor to GPIO pin 18. This can be conveniently combined with the "all ready LED" mentioned in the `materiaali-4-diffdrive` section by using the same ground pin 14, which is between GPIO18 and GPIO23, see image below.
![Raspberry Pi 5 GPIO pin order](https://pinout-ai.s3.eu-west-2.amazonaws.com/raspberry-pi-5-gpio-pinout-diagram.webp)

#### Compiling and testing the Battery package

Now you can compile the modified and added packages and include them in the ROS2 environment:

```bash
cd ~/ros2_ws
colcon build
source ./install/setup.bash
```

Test the nodes' functionality by running the commands in separate terminals (here it is assumed that no node is already running):
**Terminal 1**

```bash
ros2 launch diffdrive diffdrive.launch.py # launch all other nodes so that SeBot is ready to drive
```

**Terminal 2**

```bash
ros2 run battery battery_republish
```

**Terminal 3**

```bash
ros2 run battery battery_alert
```

**Terminal 4**

```bash
ros2 topic list
ros2 topic echo /battery_voltage
ros2 topic echo /battery_alert
```

At least one "False" should appear in the `/battery_alert` topic, even if the battery voltage is initially below the set threshold. The threshold is set high by default to 12 V, so that its effect can be seen quickly even if the battery is full at the beginning.

If everything works, the `/battery_voltage` topic should show the up-to-date voltage and the LED connected to GPIO pin 18 should light up when the battery voltage drops below the threshold. This should also be visible in the `/battery_alert` topic as a message indicating the change of state.

**Note** that in larger ROS2 systems, this type of functionality is more likely implemented as a `service` such that when the voltage drops too low, for example, a `set_battery_alert` service is called with a value of True, which then handles the necessary actions, such as turning on an LED or shutting down the system. However, in this exercise, services are not covered, so the functionality is handled with topics.

#### Launch file

Finally, modify the `diffdrive` package's launch file so that the entire system starts up at once:

> Note that the launch file below does not enable `namespace` functionality. If you want to use multiple SeBots in the same ROS2 network, refer to the `materiaali-2-motordriver` and `materiaali-4-diffdrive` materials.

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
```

Finally, update `params.yaml` with new parameters:

```yaml

---
battery_republish_node:
  ros__parameters:
    threshold: 10.5
battery_alert_node:
  ros__parameters:
    battery_check_interval: 10.0
```

Now you can compile the modified and added packages and include them in the ROS2 environment:

```bash
cd ~/ros2_ws
colcon build
source ./install/setup.bash
```

-

Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
