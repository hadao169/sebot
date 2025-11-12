## 2. ROS 2 -based control

Material tested:

- Raspberry PI 5 (image: username: ros2 password: ros2)
- Ubuntu 24.04 (Noble Numbat)
- ROS2 Jazzy Jalisco (jazzy)
- motor x2
- motor controller
- arduino
- battery connection

For a ROS2 node, we now have a section ready that sends a speed instruction to the motor controller. For the node to be usable as part of a larger system, we need to add the following components:

1. **Subscriber**: This receives speed information, which is then directed to the motor controller. This way, the node can function as part of the ROS2 system and receive control commands from another node.
2. **Publisher**: This publishes information about the motor's operation, such as encoder values, actual motor speeds, and PWM settings. The published data can be utilized, for example:

   - In Odometry: Encoder values can be used to calculate the robot's position and orientation (x, y, θ) relative to the starting point.

   - In State Monitoring: Speed and PWM values allow monitoring the motor's status and ensuring they operate as expected and without disturbances.

3. **ROS_DOMAIN_ID and namespace**: The DDS (Data Distribution Service) middleware utilized by ROS2 handles all communication routing between ROS2 applications (nodes). Because in this exercise there can be multiple computers and robots on the same WLAN network, all messages "belong" to all nodes between all machines. In the case of this exercise, this is undesirable, as each student undoubtedly wants to control only their own SeBot. There are two solutions to this:

- change the `ROS_DOMAIN_ID` environment variable to a unique number (instead of the default value 0). Each ROS2 node communicates only "within" its own `ROS_DOMAIN_ID`.
- utilize the `_namespace_` function, which automatically adds the given namespace name in front of all _topics_, _services_, and _actions_ (i.e., _interfaces_) of the nodes to be launched. In this case, for example, the /odom topic created in the node's code is converted to /[namespace]/odom format.

> In this exercise, we will try the first option so that we do not get bogged down in too complex a whole. Therefore, it is advisable to skip all sections referring to the use of namespaces, which are marked in the material with square brackets, for example, `/[SeBot_namespace]`.

When you want to change the `ROS_DOMAIN_ID` value, type in the command prompt

```bash
#export ROS_DOMAIN_ID=[value], for example
export ROS_DOMAIN_ID=1
```

This is only valid in that particular command prompt. If you want the new `ROS_DOMAIN_ID` value to take effect every time the command prompt starts, add the line above to the end of the `.bashrc` file found in your home directory:

```bash
nano ~/.bashrc # Or other editor
```

**~/.bashrc**

```
...
export ROS_DOMAIN_ID=1

>>ctrl+o, ctrl+x # Save and exit nano program
```

```bash
source ~/.bashrc # Reload .bashrc file in this command prompt
```

### Final Operation

![https://i.pinimg.com/originals/6b/b7/9e/6bb79e8a76dcf47cfbf6a1a6f38ac640.png](kuvat/arch.png)

#### Motordriver Subscriber (motor_command)

We implement the subscriber component as simply as possible by using `std_msgs.msg.String` data type. This allows the higher level to directly send motor controller command strings without the need to convert information to different formats. This way we avoid unnecessary complexity and can test and use the node quickly.

Let's create a motordriver python package

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src/
ros2 pkg create --build-type ament_python motordriver
cd ~/ros2_ws/src/motordriver/motordriver
```

Create a `motordriver.py` file, which utilizes the code we have already made for motor controller management. This file acts as a modular component that can be used in ROS2 nodes or other projects.

**~/ros2_ws/src/motordriver/motordriver/motordriver.py**

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import serial
import time

class MotordriverNode(Node):
  def __init__(self):
    super().__init__('motordriver_node')

    self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    if not self.arduino.isOpen():
      raise Exception("No connection to motor controller")

    # motor stops if no new command is received within 1s
    self.arduino.write(("ALIVE;1;\n").encode())

    self.subscriber = self.create_subscription(
        String,
        'motor_command',
        self.motor_command_callback,
        10
    )

  def motor_command_callback(self, message):
    self.arduino.write(("%s\n"%message.data).encode())

def main(args=None):
  rclpy.init(args=args)
  motordriver_node = MotordriverNode()
  try:
    rclpy.spin(motordriver_node)
  except KeyboardInterrupt:
    pass
  finally:
    motordriver_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()

if __name__ == '__main__':
  main()
```

`create_subscription` is a method of the ROS2 Node class that allows a node to subscribe to messages from a specific topic. When a message is published to the topic, the node executes the specified callback function, which processes the incoming message.

```python
    self.subscriber = self.create_subscription(
        String,				# msg_type
        'motor_command',		# topic_name
        self.motor_command_callback,	# callback
        10				# quos
    )
```

##### create_subscription -function parameters:

1. msg_type

   Määrittelee viestityypin, jota topicilla käytetään.

2. topic_name

   Topicin nimi, jota node tilaa. Tämä tulee kirjoittaa ilman edeltävää kenoviivaa /, jotta topicin nimestä tulee suhteellinen (eikä absoluuttinen) ja siten namespace-asetus voi toimia.

3. callback

   Funktio, joka suoritetaan aina, kun topicilta saapuu viesti. Tämä funktio vastaanottaa parametrina topicilta tulevan viestin ja käsittelee sen, tässä tapauksessa kirjoitetaan sarjaporttiin.

   ```python
   def motor_command_callback(self, message):
   	self.arduino.write(("%s\n"%message.data).encode())
   ```

4. qos (Quality of Service)

   Määrittelee viestien välityksen luotettavuuden ja suorituskyvyn.
   10 on luotettava ja vakioarvo pienille viestimäärille.

#### Testing

We can test the program's functionality before actual compilation with the following steps (note: multiple terminals must be in use):

![https://i.pinimg.com/originals/6b/b7/9e/6bb79e8a76dcf47cfbf6a1a6f38ac640.png](kuvat/terminal.png)

1. ##### Start the motor controller code directly with Python

```
python3 motordriver.py
```

If no errors occur, `motordriver.py` should work correctly in terms of serial communication and command handling.

**Note that all SeBots in the same WLAN network and `ROS_DOMAIN_ID` will receive all messages from the same topics if they are defined as such in the codes above.** If several students are doing the exercise at the same time, it is advisable to use different `ROS_DOMAIN_ID` environment variable values (or provide a namespace setting to the script at startup).

```bash
python3 motordriver.py
#python3 motordriver.py --ros-args -r __ns:=/[SeBot_namespace]
```

> There must be a slash / before `namespace`. As a namespace in this exercise, you could use the latter byte of your SeBot's IP address, for example
>
> ```bash
> python3 motordriver.py --ros-args -r __ns:=/SeBot11
> ```

2. ##### Check if the topic appears in the list

```
ros2 topic list

/motor_command
```

> If there are several ROS2 applications with the same `ROS_DOMAIN_ID` in the same WLAN, each with its own namespace setting, several topics will appear in the list, for example
>
> ```bash
> ros2 topic list
>
> /SeBot11/motor_command
> /SeBot12/motor_command
> /SeBot13/motor_command
> ```

3. ##### Send a speed command using a ROS2 topic

```bash
# publishes repeatedly
ros2 topic pub [/[SeBot_namespace]]/motor_command std_msgs/String "{data: 'SPD;100;100;'}"

# publishes repeatedly 2 times per second
ros2 topic pub -r 2 [/[SeBot_namespace]]/motor_command std_msgs/String "{data: 'SPD;100;100;'}"

# publish only once
ros2 topic pub -t 1 [/[SeBot_namespace]]/motor_command std_msgs/String "{data: 'SPD;100;100;'}"
```

Note the use of namespace. If it has not been set, it does not need to be written in this call either.

The command publishes a message of type `String` to the `motor_command` topic, containing the text `SPD;100;100;`. If your created node is now running and working correctly, the motors should start spinning.

### Compiling as part of a ROS2 system

When compiling Python packages in ROS 2, it essentially means building and installing nodes and packages into the workspace (install directory). When programs are "wrapped" as ROS2 packages, they can be run in the ROS2 environment, shared more easily with other users (for example, considering dependencies on Python and C++ libraries), and launched collectively using _launch_ files.

Add node to `setup.py` file

**~/ros2_ws/src/motordriver/setup.py**

```python
from setuptools import find_packages, setup

package_name = 'motordriver'

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
    maintainer='ros2',
    maintainer_email='ros2@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motordriver = motordriver.motordriver:main',
        ],
    },
)
```

##### Compile (in Python's case, just install)

```bash
cd ~/ros2_ws
colcon build --packages-select motordriver
```

Enable the environment variables of the workspace `~/ros2_ws`.

```bash
source ~/ros2_ws/install/setup.bash
```

And add the same command to the `~/.bashrc` file, so that it is always automatically in use.

```bash
nano ~/.bashrc # Or other editor you prefer
source ~/ros2_ws/install/setup.bash
```

When the program has been compiled as part of the system, it can be launched with the command

```bash
ros2 run motordriver motordriver
#ros2 run motordriver motordriver --ros-arg -r __ns:=/[SeBot_namespace]
```

Note that --ros-arg -r \__ns:=/[SeBot_namespace] is an instance of ROS2 runtime \_remapping_. The -r flag refers to _remap_, i.e., remapping (interfaces). At this point, each student can choose, for example, the latter byte of their SeBot's IP address as their namespace. Or some other unique identifier. Later, we will also explore a separate _parameter_ input option -p.

And let's test again

```bash
ros2 topic pub /motor_command std_msgs/String "{data: 'SPD;100;100;'}"

#ros2 topic pub [/[SeBot_namespace]]/motor_command std_msgs/String "{data: 'SPD;100;100;'}"

# For example
ros2 topic pub /SeBot11/motor_command std_msgs/String "{data: 'SPD;100;100;'}"
```

#### Motordriver Publisher (motor_data)

Let's add a publisher to the ROS2 node's functionality that publishes the data read from the motor controller for use by other nodes. This allows other nodes to utilize motor speeds, encoder values, and PWM settings.

I.e., the data returned by the motor controller:
`motor1_encoder;motor2_encoder;motor1_speed;motor2_speed;motor1_pwm_set;motor2_pwm_set`

**custom message type**

Unlike the standard message type `std_msgs/String` we used in the subscriber node, we will now create our own message type so that the data published from the motor controller is clearer and more structured. This enables easy handling of different data fields and improves the readability and extensibility of the system.

```bash
cd ~/ros2_ws/src/
ros2 pkg create motordriver_msgs
cd ~/ros2_ws/src/motordriver_msgs/
rm -rf include/
rm -rf src/
mkdir msg
```

Create file `~/ros2_ws/src/motordriver_msgs/msg/MotordriverMessage.msg` where we define

**~/ros2_ws/src/motordriver_msgs/msg/MotordriverMessage.msg**

```yaml
int32 encoder1
int32 encoder2
int32 speed1
int32 speed2
```

When we executed the command `ros2 pkg create --build-type ament_python motordriver`, ROS 2 automatically created the package structure. Now we will deal with the files `package.xml`, which contains the package description definition, and `CMakeLists.txt`, which contains the compilation settings.

Modify the package.xml file to

**~/ros2_ws/src/motordriver_msgs/package.xml**

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>motordriver_msgs</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="ros2@todo.todo">ros2</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <buildtool_depend>rosidl_default_generators</buildtool_depend>
  <exec_depend>rosidl_default_runtime</exec_depend>
  <member_of_group>rosidl_interface_packages</member_of_group>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Modify the CMakeLists.txt file to

**~/ros2_ws/src/motordriver_msgs/CMakeLists.txt**

```python
cmake_minimum_required(VERSION 3.8)
project(motordriver_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

find_package(rosidl_default_generators REQUIRED)
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MotordriverMessage.msg"
 )
ament_export_dependencies(rosidl_default_runtime)

ament_package()
```

Compile the new message type as part of the system.

```
cd ~/ros2_ws
colcon build --packages-select motordriver_msgs
source ~/ros2_ws/install/setup.bash
```

Modify the `motordriver.py` file by adding a publisher for the motor_data topic. Schedule it to query data at a frequency of 10Hz.

![](kuvat/motordriver.png)

**~/ros2_ws/src/motordriver/motordriver/motordriver.py**

```python
import rclpy
from rclpy.node import Node

from std_msgs.msg import String

import serial
import time

from motordriver_msgs.msg import MotordriverMessage

class MotordriverNode(Node):
  def __init__(self):
    super().__init__('motordriver_node')

    self.msg = "x\n"
    self.timercount = 0

    self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    if not self.arduino.isOpen():
      raise Exception("No connection to motor controller")
    # motor stops if no new command is received within 1s

    self.arduino.write(("ALIVE;1;\n").encode())

    self.subscriber = self.create_subscription(
        String,
        'motor_command', # relative reference. If you write a slash in front, for example '/motor_command', it becomes absolute, and the namespace setting no longer affects it.
        self.motor_command_callback,
        10
    )

    self.publisher = self.create_publisher(
        MotordriverMessage,
        'motor_data',
        10
    )

    timer_period = 0.01  # Seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)

  def timer_callback(self):
    # Create message for Arduino
    if self.msg != "x\n":
        self.arduino.write(self.msg.encode())

    if self.timercount == 11:
        if self.msg == "x\n":
            self.arduino.write(self.msg.encode())

        self.timercount = 0
        if self.arduino.inWaiting()>0:
          while self.arduino.inWaiting()>0:
            answer=self.arduino.readline().decode("utf8").split(";")

          msg = MotordriverMessage()

          try:
            msg.encoder1 = int(answer[0])
            msg.encoder2 = int(answer[1])
            msg.speed1 = int(answer[2])
            msg.speed2 = int(answer[3])

            # Publish message on topic
            self.publisher.publish(msg)
          except Exception as err:
            pass

    self.msg = "x\n"
    self.timercount += 1

  def motor_command_callback(self, message):
    self.msg = "%s\n"%(message.data)

def main(args=None):
  rclpy.init(args=args)
  motordriver_node = MotordriverNode()
  try:
    rclpy.spin(motordriver_node)
  except KeyboardInterrupt:
    pass
  finally:
    motordriver_node.destroy_node()
    if rclpy.ok():
      rclpy.shutdown()


if __name__ == '__main__':
  main()
```

Using the new message type

```python
from motordriver_msgs.msg import MotordriverMessage
```

Message sent to the motor controller. "x\n" is just a short message to read the responses.

```python
    self.msg = "x\n"
```

`create_publisher` is a method of the ROS2 Node class that allows creating a publisher, i.e., a message sender, for a specific topic. The publisher enables the node to share information with other nodes in the ROS2 system.

```python
    self.publisher = self.create_publisher(
        MotordriverMessage,	# msg_type, i.e., ROS2 data type of the message.
        'motor_data',		# topic name, note that a slash / is not used in front here, so that the namespace setting can work. If a slash is written in front of the topic, it becomes an absolute reference instead of a relative reference.
        10					# qos
    )
```

##### Parameters:

1. msg_type

   Viestityyppi, jota topic käyttää.

2. topic_name

Topicin nimi, johon viesti julkaistaan.

3. qos (Quality of Service)

   Laadunhallintaprofiili, joka määrittää, kuinka viestejä käsitellään, jos lähettäjän ja vastaanottajan välinen yhteys ei ole täydellinen. Luku 10, riittää useimpiin tilanteisiin.

We create a timer that runs at 100Hz. The control command to the controller is not sent directly but is sent in the timer. New values are read from the motor controller at a frequency of 10Hz in the timer. This aims to prevent excessive irregular traffic that would hinder the operation of the PID controller.

```python
    timer_period = 0.01  # Seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)

  def timer_callback(self):
    # Create message
    if self.msg != "x\n":
        self.arduino.write(self.msg.encode())


    if self.timercount == 11:
        if self.msg == "x\n":
            self.arduino.write(self.msg.encode())
        self.msg = "x\n"

        self.timercount = 0
        if self.arduino.inWaiting()>0:
          answer=self.arduino.readline().decode("utf8").split(";")
          self.arduino.flushInput()

          msg = MotordriverMessage()

          try:
            msg.encoder1 = int(answer[0])
            msg.encoder2 = int(answer[1])
            msg.speed1 = int(answer[2])
            msg.speed2 = int(answer[3])

            # Publish message
            self.publisher.publish(msg)
          except Exception as err:
            pass

    self.timercount += 1

  def motor_command_callback(self, message):
    self.msg = "%s\n"%(message.data)
```

We can again launch the node simply (note: source... must be executed):

```bash
python3 motordriver.py
#python3 motordriver.py --ros-args -r __ns:=/[SeBot_namespace]
```

And check that both nodes are running (again, noting that at this stage all SeBot topics in the same `ROS_DOMAIN_ID` are the same if they are written that way in the codes).

```bash
ros2 topic list

[/SeBot_namespace]/motor_command
[/SeBot_namespace]/motor_data
```

Motor rotation should work the same way as before

```bash
ros2 topic pub /motor_command std_msgs/msg/String "{data: 'SPD;100;-100;'}"
#ros2 topic pub /[SeBot_namespace]/motor_command std_msgs/msg/String "{data: 'SPD;100;-100;'}"
```

And in addition we should get values (remember the source command if you are running in an old window)

```bash
ros2 topic echo /motor_data
#ros2 topic echo /[SeBot_namespace]/motor_data


	encoder1: 22663
	encoder2: 23018
	speed1: 102
	speed2: 99
	---
	encoder1: 22569
	encoder2: 22924
	speed1: 99
	speed2: 100
	---
	encoder1: 22474
	encoder2: 22829
	speed1: 99
	speed2: 100
	---
	encoder1: 22379
	encoder2: 22735
	speed1: 101
	speed2: 100
```

All good? Let's compile the package.

```bash
cd ~/ros2_ws
colcon build --packages-select motordriver
```

And now we can launch the node

```bash
ros2 run motordriver motordriver
```

Thus, we have created a node that relays commands published to the `motor_command` topic to the motor controller and publishes motor speed data and encoder values from the `/[SeBot_namespace]` `/motor_data` topic. If desired, we can add PWM control values to the `MotordriverMessage` message type we created, and thus, if desired, we can read what PWM values the SPD command gives to the motor.

Add to **~/ros2_ws/src/motordriver_msgs/msg/MotordriverMessage.msg** file:

```yaml
int32 pwm1
int32 pwm2
```

and to **~/ros2_ws/src/motordriver/motordriver/motordriver.py** file:

```python
msg.pwm1 = int(answer[4])
msg.pwm2 = int(answer[5])
```

We can compile both packages at once:

```bash
cd ~/ros2_ws
colcon build --packages-select motordriver motordriver_msgs
```

Simulation without a real motor controller. Let's make an emulator as an alternative to the serial port.

**~/ros2_ws/src/motordriver/motordriver/simserial.py**

```python
import time
import threading

class SimSerial():
  def __init__(self):
    self.answer = [0,0,0,0,0,0]
    self.response = 0
    self.encoder_min = -32768
    self.encoder_max = 32768
    self.sim_odo_left = SimuOdo(self.encoder_min, self.encoder_max)
    self.sim_odo_right = SimuOdo(self.encoder_min, self.encoder_max)

  def write(self,message):
    try:
      a = message.decode().split(";")
      self.sim_odo_left.set_speed(int(a[1]))
      self.sim_odo_right.set_speed(int(a[2]))

      self.answer[4] = self.sim_odo_left.speed
      self.answer[5] = self.sim_odo_right.speed

    except Exception as err:
      pass

    self.answer[0] = self.sim_odo_left.tell_ticks()
    self.answer[1] = self.sim_odo_right.tell_ticks()

    self.response = 1

  def inWaiting(self):
    return self.response

  def readline(self):
    retval = ";".join([str(x) for x in self.answer]).encode()
    self.response = 0
    return retval


class SimuOdo():
    """This class 'simulates' a physical encoder, allowing the ROS2 code package to be run without physical hardware."""
    def __init__(self, encoder_min, encoder_max):
        self.speed = 0
        self.ticks = 0
        self.encoder_min = encoder_min
        self.encoder_max = encoder_max
        thread = threading.Thread(target = self.run_periodically)
        thread.start()
    def run_periodically(self):
        while True:
            self.roll()
            time.sleep(0.1)

    def set_speed(self, speed):
        self.speed = speed

    def roll(self):
        self.ticks = self.ticks + self.speed
        if self.ticks > self.encoder_max:
          self.ticks -= self.encoder_max-self.encoder_min
        if self.ticks < self.encoder_min:
          self.ticks += self.encoder_max-self.encoder_min

    def tell_ticks(self):
        return self.ticks
```

Modify the motordriver.py file:

**~/ros2_ws/src/motordriver/motordriver/motordriver.py**

```python
.
.
.
try:
  from .simserial import SimSerial
except:
  from simserial import SimSerial

class MotordriverNode(Node):
  def __init__(self):
    super().__init__('motordriver_node')

    self.msg = "x\n"
    self.timercount = 0

	 # if simulation parameter is not found, it defaults to True
    self.declare_parameter('simulation', True)
    self.simulation = self.get_parameter('simulation').value
    self.get_logger().info(f'Starting motor_controller in simulation: {self.simulation}')
    if self.simulation:
      self.arduino = SimSerial()
    else:
      self.arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
      if not self.arduino.isOpen():
        raise Exception("No connection to motor controller")

    self.subscriber = self.create_subscription(
        String,
        'motor_command',
        self.motor_command_callback,
        10
    )

    self.publisher = self.create_publisher(
        MotordriverMessage,
        'motor_data',
        10
    )

    timer_period = 0.01  # seconds
    self.timer = self.create_timer(timer_period, self.timer_callback)
.
.
.
```

Now you can add the parameter on the command line. Compare to the `namespace` setting made in the previous section, which was done with the -r (which is the same as --remap) option.

```bash
python3 motordriver.py --ros-args -p simulation:=False #-r __ns:=/[SeBot_namespace]
```

Or after compilation:

```bash
ros2 run motordriver motordriver --ros-args -p simulation:=False #-r __ns:=/[SeBot_namespace]
```

Add the parameter to the configuration file (False = use real serial port). For the Launch file.

**~/ros2_ws/config/params.yaml**

```yaml
motordriver_node:
  ros__parameters:
    simulation: False
```

**Note that the namespace setting cannot be written to the node's parameter file. It is not an actual parameter, but a runtime remapping.**

- Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
