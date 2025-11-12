### Arduino

The Arduino code can be found in the directory `/opt/nomga/arduino/`

```bash
# Compile code
compile.sh

# Upload to Arduino
upload.sh
```

### ROS2

ROS2 code can be found in the directory `/opt/nomga/ros2/`

Functionality can be tested by

```bash
source /opt/nomga/ros2_ws/install/setup.bash
```

In the directory `/opt/nomga/ros2_ws/src/diffdrive/diffdrive/`, there is also the `pi_led.py` file, which lights up an LED connected to Raspberry PI GPIO23 when `ros2 launch diffdrive diffrive.launch.py` is run and everything is ready. Note that this is not an actual ROS2 package, meaning it is not run with the ros2 run ... command.

These .md files can be shared on a closed local network using the python script `serve_md_files.py`, found in the `code` folder, in whose `markdown_files` subdirectory these md-files have been copied.

### Foxglove Studio graphical user interface

This material has referred to the use of a visualization tool called RVIZ2. However, this is not possible if you do not have an Ubuntu machine with a graphical desktop, operating in the same ROS2 network. If you want to visualize a moving robot on screen, you can use a user interface software called [Foxglove](https://foxglove.dev/robotics/ros), which can also be run directly as a web service (i.e., without installing a Foxglove server on your own machine).

For this, you need a program called [Foxglove Bridge](https://docs.foxglove.dev/docs/connecting-to-data/ros-foxglove-bridge), which sends ROS2 environment messages in WebSocket format to the [Foxglove Studio](https://studio.foxglove.dev) service. To use the service, you need to create a user account or log in with, for example, your Microsoft account.

After installing Foxglove Bridge on your computer (which is in the same ROS2 network as SeBot's Raspberry Pi), you can launch it with default settings using the command

```bash
ros2 launch foxglove_bridge foxglove_bridge_launch.xml
```

Once you are logged into the Foxglove Studio service, you can now create a connection to your robot's ROS2 environment by enabling the [websocket channel](https://docs.foxglove.dev/docs/connecting-to-data/frameworks/ros2#foxglove-websocket)

![Foxglove Studio](kuvat/foxglove.png)

> Select 'Open data source' -> Foxglove WebSocket -> enter your Foxglove bridge server's URL (i.e., practically localhost:8765).

Now you can access your ROS2 environment.

If you want to see a visualization according to the URDF file, launch `robot_state_publisher` (the launch file according to materiaali-3-URDF or materiaali-4-diffdrive) and enter the following command in the terminal:

```bash
ros2 param set /robot_state_publisher robot_description "$(cat ~/ros2_ws/src/my_package/urdf/my_robot.urdf) # ensure that robot_state_publisher has the desired URDF file as its parameter
```

Now the robot's description is available in Foxglove Studio.

---

Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
