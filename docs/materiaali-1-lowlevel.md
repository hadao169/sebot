## Motor Control

### Overview

![controller and motors](kuvat/yleiskuva.png)

- Raspberry PI 5, [for example from Botland](https://botland.store/raspberry-pi-5-modules-and-kits/23905-raspberry-pi-5-8gb-5056561803326.html). Older Raspberry Pis are also well-suited.
- [Raspberry power supply](https://botland.store/raspberry-pi-5-power-supply/23906-raspberry-pi-27w-usb-c-power-supply-official-51v-5a-psu-for-raspberry-pi-5-white-5056561803401.html) It's good to keep the robot on mains power during the development phase.
- [32GB memory card](https://botland.store/raspberry-pi-memory-cards/25873-raspberry-microsd-32-gb-memory-card-5056561804200.html)
- [Arduino Micro](https://botland.store/arduino-basic-boards/1481-arduino-micro-module-a000053-7630049200159.html)
- [USB A - Micro USB](https://botland.store/usb-20-cables/17430-cable-microusb-b-usb-a-20-hi-speed-015m-black-4040849957369.html) for serial communication between Raspberry and Arduino
- [Motor driver L293D](https://botland.store/drivers-for-dc-motors/176-l293d-two-channel-36v-06a-motor-driver-5pcs-5904422350253.html)
- 2 x [DC motor with gearbox and encoder 12VDC](https://www.aliexpress.com/item/1005006217803283.html?spm=a2g0o.productlist.main.29.31698cddQydl2q&algo_pvid=af0cf6cd-9f25-4eb1-b422-3434cb6787d7&algo_exp_id=af0cf6cd-9f25-4eb1-b422-3434cb6787d7-14&pdp_ext_f=%7B%22order%22%3A%2232%22%2C%22eval%22%3A%221%22%7D&pdp_npi=4%40dis%21EUR%2110.51%218.41%21%21%2184.99%2167.99%21%4021038df617443630303392462edc8c%2112000042604759092%21sea%21FI%216207330698%21X&curPageLogUid=twZpCBgxq1fC&utparam-url=scene%3Asearch%7Cquery_from%3A)
- [Adjustable step-down converter 5A 25W](https://botland.store/converters-step-down/8103-step-down-voltage-regulator-xl4015-13v-36v-5a-5904422336202.html)
- [USB C cable](https://botland.store/usb-c-cables/18762-green-cell-powerstream-usb-type-c-usb-type-c-quick-charge-cable-12-m-black-5907813963599.html) as a power cable between the step-down converter and Raspberry
- [3s (12.6V) LiPo battery](https://botland.store/battery-li-half-3s-111-v/2394-li-pol-dualsky-800mah-25c-3s-111v-eco-s-package-6941047104662.html). A larger battery is beneficial if you want to use the robot on battery power for a long time. Note that the motors according to this guide do not tolerate more than 3S LiPo batteries, i.e., for example, 16.8V 4S batteries require different motors.

If you make the circuit board yourself, you may also need the following (or similar, according to your design) parts

- [Solder boards](https://www.aliexpress.com/item/1005007014530064.html?spm=a2g0o.productlist.main.45.6c8b272b52aYQS&algo_pvid=d0078849-9223-47ab-a4a2-498410346850&algo_exp_id=d0078849-9223-47ab-a4a2-498410346850-42&pdp_ext_f=%7B%22order%22%3A%229%22%2C%22eval%22%3A%221%22%7D&pdp_npi=4%40dis%21EUR%218.49%212.80%21%21%2167.57%2122.28%21%40211b876e17484499413794147e29d4%2112000039073325488%21sea%21FI%216207330698%21X&curPageLogUid=f3axRd5dcNw9&utparam-url=scene%3Asearch%7Cquery_from%3A)
- [Terminal blocks](https://www.tme.eu/fi/en/details/dg128-5.0-02p14/pcb-terminal-blocks/degson-electronics/dg128-5-0-02p-14/)
- [Headers](https://botland.store/connectors-goldpin/8505-socket-1x20pin-254mm-5904422311780.html)
- [M2.5 Spacers](https://www.tme.eu/fi/en/details/tfm-m2.5x10_dr222o/metal-spacers/dremec/222x10of/)
- [M2.5 screws](https://www.tme.eu/fi/en/details/b2.5x6_bn15857/bolts/bossard/3108702/)
  In addition, suitable wires, LEDs, etc.

![https://i.pinimg.com/originals/6b/b7/9e/6bb79e8a76dcf47cfbf6a1a6f38ac640.png](kuvat/simple.png)

The movement of a two-wheeled robot is based on the operation of the wheel motors, which receive instructions from a higher level. In the ROS environment, these instructions are usually given in cmd_vel messages, which define the robot's linear and angular velocity. Using this information, a ROS node connected to the robot calculates the necessary rotation directions and speeds for each wheel, which are then transmitted to the motor controller.

This calculation requires the following information:

- Wheel diameter: Affects the relationship between linear and angular velocity.
- Encoder pulse count per revolution: Needed for accurate movement measurement and speed control.
- Distance between wheels (track width): Affects the calculation of the robot's turning.

The motor controller uses an H-bridge, such as the L293D chip, to control the direction of rotation of the wheels, and a PWM signal to adjust the rotational speed of the wheels. By comparing the encoder signal to the set values, the motor controller achieves precise speed control using a PID controller, which enables accurate and controlled implementation of both straight and rotating movement.

**DC Motor Control and Arduino:**

The L293D H-bridge chip is used to control the robot's motors, allowing two motors to be controlled simultaneously. The chip is connected to an Arduino microcontroller, which has an example program for motor control. The program allows:

- Direct control of motors using PWM commands.
- Control of motors using a PID controller, which generates a PWM signal to adjust motor speed.

The program determines the motor's rotation direction based on the value produced by the PID controller or PWM command:

- A positive value causes the motor to rotate forward.
- A negative value reverses the motor's direction.

This system combines ROS environment commands and Arduino-based control, enabling precise and flexible robot motion control in terms of both speed and direction.

### Hardware

![controller and motors](kuvat/device2.png)

Arduino Micro, L293D, [DC6-24v Gear Motor with Encoder](https://www.elecrow.com/dc624v-gear-motor-with-encoder-p-1616.html)

### Wiring

The table below explains the connections between the Arduino Micro, L293D chip, and motors.

<table>
<tr>
<td valign="top">

**MOTOR WIRE CONNECTIONS**

| motor wire | function   | target  | pin             |
| ---------- | ---------- | ------- | --------------- |
| white      | motor -    | L293D   | M#1->3, M#2->11 |
| blue       | sensor +   | Arduino | +5V             |
| green      | A          | Arduino | M#1->3, M#2->2  |
| yellow     | B          | Arduino | M#1->4, M#2->9  |
| black      | sensor gnd | Arduino | gnd             |
| red        | motor +    | L293D   | M#1->6, M#2->14 |

![https://i.pinimg.com/originals/6b/b7/9e/6bb79e8a76dcf47cfbf6a1a6f38ac640.png](kuvat/arduinopins.png) Arduino Micro connections. Red circles indicate used pins.

</td><td>

**H-BRIDGE L293D CONNECTIONS**

| L293D pin | function | target   | pin / wire           |
| --------- | -------- | -------- | -------------------- |
| 1         | enable1  | Arduino  | 5                    |
| 2         | input1   | Arduino  | 6                    |
| 3         | output1  | Motor #1 | white                |
| 4         | gnd      | Arduino  | gnd                  |
| 5         | gnd      | Arduino  | gnd                  |
| 6         | output2  | Motor #1 | red                  |
| 7         | input2   | Arduino  | 8                    |
| 8         | Vs       | Battery  | +12V (drive voltage) |
| 9         | enable2  | Arduino  | 10                   |
| 10        | input3   | Arduino  | 11                   |
| 11        | output3  | Motor #2 | white                |
| 12        | gnd      | Arduino  | gnd                  |
| 13        | gnd      | Arduino  | gnd                  |
| 14        | output4  | Motor #2 | red                  |
| 15        | input4   | Arduino  | 12                   |
| 16        | Vss.     | Arduino  | +5V                  |

</td>
</tr>
</table>

#### Commands

The following commands are programmed into the Arduino:

1. Direct control: `PWM;100;100;`
2. PID control: `SPD;100;100;`
3. PID values: `PID;0.7;0.003;0.0;`
4. Reset encoders: `ZERO;`
5. Adjust alive value (0 = off): `ALIVE;3;`

PWM and SPD values range from -255 to +255. These values themselves do not represent speed in meters per second (m/s), but the conversion occurs in the ROS node. The direction of rotation is determined by the sign of the value.

All commands return a string: `encoder1;encoder2;rpm1;rpm2;pwm1;pwm2`

### Direct PWM control

`PWM;64;191;` means that motor #1 is supplied with a 25% PWM signal and motor #2 with a 75% PWM signal. When these signals pass through the L293D chip, the chip amplifies them based on its supply voltage, thus achieving a suitable voltage level for the motors. The L293D acts as a signal amplifier and control element here.

![https://docs.arduino.cc/learn/microcontrollers/analog-output/](kuvat/mypwm.png)

The maximum speed of the motor is achieved with a PWM value of 255, but the lowest speed depends on several factors, such as motor characteristics, load, PWM signal quality, and environmental conditions. This value can be determined by practical tests and, if necessary, optimized by various methods.

Maximum acceleration is achieved when the motor starts from a standstill (PWM = 0) and is immediately given maximum input (PWM = 255). In this case, the motor operates at full power from the beginning, achieving maximum acceleration.

We test the controller by simply sending the desired duty cycle, which causes the motors to rotate at a constant voltage without feedback. This allows checking the basic functions of the control system before implementing closed-loop control.

We connect the motor controller to the computer with a USB cable, allowing it to be controlled via serial communication. This connection provides a simple and reliable way to send control commands to the motor controller.

**pwm.py**

```python
import serial
import time

try:
    speed = 100
    arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    time.sleep(2.0) # wait until the line is definitely open
    arduino.write(("PWM;%s;%s;\n"%(speed,speed)).encode()) # give pwm instruction to both motors
    if arduino.isOpen():
        while(True):
            print("Motors are still rotating")
            time.sleep(3.0)

except KeyboardInterrupt:
        print("\nProgram interrupted, stopping motors.")
        arduino.write(("PWM;0;0").encode())

finally:
        print("Exiting program")
```

A control value of 100 is sent to each motor, which corresponds to approximately a 40% duty cycle and rotates the motors in the same direction. However, it is important to note that if the motors are installed in the robot in a differential drive configuration (opposite to each other), this control value will cause the motors to rotate in opposite directions, making the robot spin in place instead of moving forwards or backwards. This phenomenon is essential to consider when synchronizing motors and control values.

```bash
# Run the program with the command
python3 pwm.py
```

##### If nothing happens, check the following:

1. Connections: Ensure that all connections are tight, especially the USB cable and any power cables for the motor controller.
2. Power supply: Check that the motor controller is powered and that the power supply is working.
3. Control value: Depending on the motor type and its characteristics, the given control value (e.g., 100) may be too small for the motor to rotate. Try increasing the control value gradually and observe if the motor starts to operate.

If problems persist, also check that the serial communication protocol and configurations (e.g., baud rate) used are correct and compatible with the motor controller settings.

### Feedback

We will make a small addition to the code to print the response received from the motor controller. The response arrives in the format:

`motor1_encoder;motor2_encoder;motor1_speed;motor2_speed;motor1_pwm_set;motor2_pwm_set`

This addition allows us to check the motor encoder values, speeds, and PWM settings directly from the code output. The code also has a commented-out line that causes the motor speeds to vary randomly for interest.

```python
import serial
import time
import random
try:

    speed = 100
    arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    time.sleep(2.0)
    if arduino.isOpen():
        while(True):
            # speed += random.randint(-10,10) # Uncomment if you want to try changing the speed randomly.
            print(f"Changing speed = {speed}")
            arduino.write(("PWM;%s;%s;\n"%(speed,speed)).encode())
            time.sleep(0.5) # length of sampling interval

            if arduino.inWaiting()>0:
                answer=arduino.readline()
                print(answer)
                arduino.flushInput()

except KeyboardInterrupt:
        print("\nProgram interrupted, stopping motors.")
        arduino.write(("PWM;0;0").encode())

finally:
        print("Exiting program")
```

And when we run the program, we get responses

```
python pwm.py

b'-552;-518;169;158;100;100\n'
b'-1324;-1237;179;166;100;100\n'
b'-2103;-1963;179;167;100;100\n'
b'-2884;-2692;180;168;100;100\n'
b'-3666;-3422;181;168;100;100\n'
b'-4449;-4154;180;168;100;100\n'
b'-5233;-4887;180;169;100;100\n'
b'-6018;-5621;181;169;100;100\n'
b'-6802;-6356;181;170;100;100\n'
b'-7588;-7093;181;170;100;100\n'
b'-8372;-7828;181;170;100;100\n'
b'-9158;-8564;181;169;100;100\n'
b'-9946;-9300;181;169;100;100\n'
b'-10735;-10037;181;169;100;100\n'
b'-11523;-10772;182;169;100;100\n'
b'-12312;-11508;182;169;100;100\n'
b'-13102;-12245;182;170;100;100\n'
```

From the obtained data, curves can be formed that clarify the interpretation of the results. With the help of the curves, we can ensure that both encoders work as expected, and observe that motor #2 rotates slightly slower at the given control value, which also leads to a slightly shorter travel distance. Visualization provides a clear way to evaluate the system's operation and identify potential deviations or areas requiring fine-tuning.

Analyzing the values is easy by copying them to an Excel spreadsheet and creating a line graph. By trying different values, you can observe how they affect motor rotation.

![pwm](kuvat/pwm.png)

If the encoder values do not update even though the motor is rotating, check the connections carefully. If the encoder values appear to be in the wrong direction (e.g., motors rotate in the same direction but values decrease on one encoder), the signals may be crossed. In this case, correct the connections by swapping the incorrectly connected signal wires.

### PID Controller

You can learn about the operation of the PID controller by examining the code in the Arduinos.

![pwm](kuvat/pid.png)

Once it has been confirmed that the motor rotates as expected with PWM control and the encoders return correct values, you can move on to using a PID controller. With a PID controller, we achieve more precise speed control, so the motors rotate at the desired speed regardless of load or other disturbances. This step enables optimizing system performance and lays the foundation for more precise control.

`SPD;127;127;` means that each motor tries to maintain a speed of 127.

The motor controller has a built-in safety feature for the SPD command, which automatically stops the motor if it does not receive a new instruction within a specified time (default 3 seconds). This feature ensures that the motor does not continue to rotate uncontrollably due to possible error situations or disturbances in the higher-level control system. This way, the motor stops safely, which increases the reliability of the system and protects both the hardware and the environment.

We can make a simple change by replacing the PWM command with the SPD command, so the motor controller takes care of calculating the PWM settings itself to achieve the desired speed.

```python
import serial
import time

try:
    speed = 100
    arduino = serial.Serial("/dev/ttyACM0", 115200, timeout=1)
    time.sleep(2.0)
    if arduino.isOpen():
      while True:
        arduino.write(("SPD;%s;%s;\n"%(speed,speed)).encode())
        time.sleep(0.5) # sampling interval, you can experiment with how a shorter interval affects controllability.

        if arduino.inWaiting()>0:
          answer=arduino.readline()
          print(answer)
          arduino.flushInput()

except KeyboardInterrupt:
    print("Stopping motors")
    arduino.write(("SPD;0;0").encode())
finally:
    print("Exiting program")
```

And the response is obtained in the same way as with the PWM command, but now we can directly observe that the motor speed tends to stay at the given value, and the PWM value varies automatically by the motor controller. This confirms that the motor controller dynamically adjusts the PWM values to compensate for changes in load or other conditions, resulting in smoother speed control.

```
b'-510;-498;141;135;20;32\n'
b'-926;-924;105;104;52;58\n'
b'-1354;-1354;101;100;57;61\n'
b'-1787;-1786;101;102;57;60\n'
b'-2216;-2216;99;99;58;62\n'
b'-2648;-2645;100;97;57;63\n'
b'-3081;-3075;101;98;57;62\n'
b'-3511;-3507;99;100;58;61\n'
b'-3945;-3939;100;100;57;62\n'
b'-4375;-4372;100;100;57;61\n'
b'-4806;-4802;99;100;58;61\n'
b'-5236;-5233;99;101;58;61\n'
b'-5668;-5665;101;100;57;61\n'
b'-6102;-6099;100;100;57;61\n'
b'-6532;-6527;100;99;57;62\n'
b'-6964;-6960;99;99;58;62\n'
b'-7399;-7393;101;99;56;61\n'
```

![pwm](kuvat/spd.png)

When comparing the curves of steady PWM control with those obtained from the PID controller, we can observe a significant improvement: with the PID controller, motor speeds remain more precisely at the set value. In addition, we see that the PWM set values differ between the motors such that the slower rotating motor #2 requires slightly more power to keep up with motor #1. This demonstrates the effectiveness of the PID controller in equalizing speeds and compensating for individual differences between motors.

The peculiarity visible at the beginning of the curve, where the speed is high and the PWM value is low, is due to the fact that the first adjustment values of the PID controller do not have time to be recorded in the diagram when we use a 0.5-second delay in printing the results. This delay causes the data at the beginning of the diagram not to fully reflect the controller's actual behavior.

When we reduce the sampling interval to 0.1 seconds, we can see the event better, and thus the operation of the PID controller in the initial phase can be analyzed more accurately. This helps to detect possible deviations or optimization needs.

![pwm](kuvat/spd2.png)

We apply the same 0.1-second sampling interval also at the beginning of the PWM control to get a better understanding of the system's behavior immediately at startup. This helps to compare PWM control and the PID controller more accurately from the beginning and to observe, for example, phenomena occurring in the transient phase, such as motor acceleration and changes in PWM values.

![pwm](kuvat/pwm2.png)

However, it is important to consider the limitations of the motor controller used: too frequent data collection can overload the controller and slow down the operation of the PID controller itself. In this case, system performance may degrade, which can lead to incorrect conclusions about the functionality of the PID circuit. Thus, in choosing the sampling interval, a balance must be found between accuracy and system functionality. If the controller starts to slow down, rarer sampling should be considered or data collection should be optimized by avoiding unnecessary requests.

### Alternatives

When the goal is to achieve better performance from the motor controller, FPGA (Field Programmable Gate Array) is an excellent choice as a processor. FPGA allows parallel execution of multiple tasks, which ensures fast and efficient operation. This is particularly useful in critical motor control tasks, such as the PID controller, where performance must remain stable and accurate regardless of other system functions. The parallelism of FPGA makes it an ideal choice for high-performance applications.

If the project budget allows, a wide range of commercial motor controllers are also available on the market that are well-tested and reliable. These include simple DC motor controllers, precise servo controllers, and versatile robotics control systems. Most of these products offer comprehensive documentation, technical support, and ready-made integrations, for example, with the ROS system, which makes them a reliable and easy-to-use solution. The trade-off for high quality and reliability is often a higher price, so the choice of these products depends on the project's needs and budget.

- Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
