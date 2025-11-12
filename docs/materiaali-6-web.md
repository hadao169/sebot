### UI and ROS 2: ROSbridge and roslib.js quick example

Finally, we will create a webpage that facilitates testing the ROS 2 system and sending commands. The page will clearly display encoder values and current speed on the top row. In addition, the user can input desired values into command fields and execute various commands easily with buttons.

![turning radius](kuvat/ui.png)

To transmit commands from the webpage to the ROS 2 system, we need an intermediary component. The ROSbridge server enables communication between ROS 2 and web applications via a WebSocket connection. To utilize this connection, we use the roslib.js library, which provides an easy-to-use interface to ROS 2 topics directly from webpages.

**RoslibJS** is a JavaScript library that simplifies robot-related programming and communication through webpages or web applications. It enables, for example, robot control, reading sensor data, and managing robot status easily with JavaScript. It is often used in web-based robot projects and IoT applications that require real-time connection and control of robot operations.

Start ROSbridge

```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

Create the webpage

**index.html**

```html
<html>
  <head>
    <script
      type="text/javascript"
      src="https://cdn.jsdelivr.net/npm/roslib@1/build/roslib.min.js"></script>
    <script type="text/javascript" src="ros.js"></script>
    <style type="text/css">
      div {
        width: 100px;
        display: inline-block;
        text-align: right;
      }
    </style>
  </head>
  <body>
    <button onClick="pwm(0,0);">stop</button>
    <div id="m1speed">0</div>
    <div id="m2speed">0</div>
    <div id="m1encoder">0</div>
    <div id="m2encoder">0</div>
    <table>
      <tr>
        <td></td>
        <td><input id="value1" placeholder="Motor1 PWM" /></td>
        <td><input id="value2" placeholder="Motor2 PWM" /></td>
        <td><button onClick="runPWM()">PWM</button></td>
      </tr>
      <tr>
        <td></td>
        <td><input id="value3" placeholder="Motor1 SPD" /></td>
        <td><input id="value4" placeholder="Motor2 SPD" /></td>
        <td><button onClick="runSPD()">SPD</button></td>
      </tr>
      <tr>
        <td><input id="value5" placeholder="P" /></td>
        <td><input id="value6" placeholder="I" /></td>
        <td><input id="value7" placeholder="D" /></td>
        <td><button onClick="runPID()">PID</button></td>
      </tr>
      <tr>
        <td></td>
        <td><input id="value8" placeholder="Linear Speed" /></td>
        <td><input id="value9" placeholder="Angular Speed" /></td>
        <td><button onClick="runCMD_VEL()">cmd_vel</button></td>
      </tr>
    </table>
  </body>
</html>
```

and the javascript file

**ros.js**

```javascript
const ROBOT_IP = "<robotin ip osoite>";

let cmd_raw = null;
let msg = null;

const ros = new ROSLIB.Ros({
  url: "ws://" + ROBOT_IP + ":9090",
  groovyCompatibility: false,
});

function cmd_vel(speed, rotate) {
  cmd_raw = new ROSLIB.Topic({
    ros: ros,
    name: "/cmd_vel",
    messageType: "geometry_msgs/msg/Twist",
  });

  msg = new ROSLIB.Message({
    linear: {
      x: parseFloat(speed),
      y: 0.0,
      z: 0.0,
    },
    angular: {
      x: 0.0,
      y: 0.0,
      z: parseFloat(rotate),
    },
  });
  cmd_raw.publish(msg);
}

function spd(a, b) {
  cmd_raw = new ROSLIB.Topic({
    ros: ros,
    name: "/motor_command",
    messageType: "std_msgs/msg/String",
  });

  msg = new ROSLIB.Message({
    data: "SPD;" + a + ";" + b + ";",
  });

  cmd_raw.publish(msg);
}

function pid(a, b, c) {
  const cmd_tmp = new ROSLIB.Topic({
    ros: ros,
    name: "/motor_command",
    messageType: "std_msgs/msg/String",
  });

  const msg_tmp = new ROSLIB.Message({
    data: "PID;" + a + ";" + b + ";" + c + ";",
  });

  cmd_tmp.publish(msg_tmp);
}

function pwm(a, b) {
  cmd_raw = new ROSLIB.Topic({
    ros: ros,
    name: "/motor_command",
    messageType: "std_msgs/msg/String",
  });

  msg = new ROSLIB.Message({
    data: "PWM;" + a + ";" + b + ";",
  });

  cmd_raw.publish(msg);
  cmd_raw = null;
  msg = null;
}

var listener = new ROSLIB.Topic({
  ros: ros,
  name: "/motor_data",
  messageType: "motordriver_msgs/msg/MotordriverMessage",
});

listener.subscribe((message) => {
  document.getElementById("m1speed").innerHTML = message.speed1;
  document.getElementById("m2speed").innerHTML = message.speed2;

  document.getElementById("m1encoder").innerHTML = message.encoder1;
  document.getElementById("m2encoder").innerHTML = message.encoder2;
});

setInterval(myTimer, 2000);
function myTimer() {
  if (cmd_raw !== null && msg !== null) {
    cmd_raw.publish(msg);
  }
}

function runPWM() {
  let value1 = document.getElementById("value1").value;
  let value2 = document.getElementById("value2").value;
  pwm(value1, value2);
}

function runSPD() {
  let value1 = document.getElementById("value3").value;
  let value2 = document.getElementById("value4").value;
  spd(value1, value2);
}

function runPID() {
  let value1 = document.getElementById("value5").value;
  let value2 = document.getElementById("value6").value;
  let value3 = document.getElementById("value7").value;
  pid(value1, value2, value3);
}

function runCMD_VEL() {
  let value1 = document.getElementById("value8").value;
  let value2 = document.getElementById("value9").value;
  cmd_vel(value1, value2);
}
```

Set ROSbridge to start automatically when the system boots

**/home/ros2/rosbridge_autostart.sh**

```bash
#!/bin/bash

# Load ROS2 environment
source /opt/ros/jazzy/setup.bash

# Load workspace environment
source /home/ros2/ros2_ws/install/setup.bash

# Execute launch file
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```

**/etc/systemd/system/ros2_rosbridge.service**

```
[Unit]
Description="ROS2 Rosbridge Autostart"
After=network.target

[Service]
Type=simple
User=ros2
ExecStart=/home/ros2/rosbridge_autostart.sh
Restart=always
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

```bash
# Start ROSbridge
sudo systemctl start ros2_rosbridge.service

# Set ROSbridge to start on boot
sudo systemctl enable ros2_rosbridge.service
```

- Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
