
                               EMBEDDED EXAMPLES

The embedded examples show how to control the MTi1-s module from an embedded 
system, using the SPI or I2C bus. The examples are written in C/C++ and can be 
build using either IAR or GCC. The examples run on a NUCLEO-F401RE board, but 
should be easily portable to other boards.

There are currently three examples:

The measurement data example:       example_mti1_i2c_spi_receive_measurement_data
The protocol explorer:              example_mti1_i2c_spi_mtssp_protocol_explorer
The Firmware update example:        example_mti1_i2c_spi_firmware_updater

The purpose of the measurement data example is to show the typical program flow
required to read measurement data from the device using the MTSSP protocol. This
example is typically the first example to try out.

The purpose of the protocol explorer is to gain some more insight in the MTSSP
protocol, by interactively sending low level commands to the device and viewing
the response from the device. With this example it is easier to analyze low
level problems which may occur while embedding an MTi1-s device in your
solution.

The firmware update example demonstrates how a device can be set in bootloader mode
and how a firmware update can be done by using the firmware update protocol.


                                 REQUIREMENTS

- An Xsens MTi3 or MTi7 module

- An Xsens development kit shield board (MTi 1-s DEV board Rev 2.1)

- An STM32 NUCLEO-F401RE development board

- IAR Embedded Workbench for ARM version 7.80.3 or higher, or the arm-none-eabi
  GCC tool chain.

- A Terminal emulator such as Putty or Tera Term

- Optionally an oscilloscope or logic analyzer (with SPI/I2C decoding) for
  viewing signals



                               HARDWARE SETUP
                               
Insert the MTi1 module in the dev board socket, and plug the dev board onto the 
arduino connector of the NUCLEO board. Connect the NUCLEO board with a USB cable 
to the PC. Observe that (in Windows) a virtual COM port and a virtual drive are 
created for the NUCLEO board. Connect a terminal emulator to the virtual COM 
port using a baud rate of 921600, 8 data bits, no parity bit and 1 stop bit. 
Please consult the development kit manual [1] for more information regarding the 
hardware setup.


                         THE MEASUREMENT DATA EXAMPLE

Build the project in the example_mti1_i2c_spi_receive_measurement_data directory 
and observe that the file example_mti1_i2c_spi_receive_measurement_data.bin is 
created in the compiler output directory. Run the example on the NUCLEO board, 
either by programming it with the debugger, or by copying the built file to the 
NUCLEO virtual drive.

The following text should appear on the terminal window:

    ----------------------------------------------------------------
    Example MTi I2C/SPI: Receive Measurement data
    Enter bus mode:
    Press 's' for SPI mode
    Press 'i' for I2C mode

Next, select the required bus mode by pressing 's' or 'i'. Next, the following
text should appear:

    Resetting the device
    Got Wake-up from device
    Got DeviceId
    Got firmware revision
    Output configuration written to device

    (h) help:     Print this help text
    (R) reset:    Reset the device
    (c) config:   Goto config mode
    (m) measure:  Goto measurement mode
    (d) deviceid: Request device id


press 'm' to set the device in measurement mode. The following output should
appear:

m
XMID_GotoMeasurementAck
XMID_MtData2: roll = 0.54, pitch = 0.75, yaw = -56.53
XMID_MtData2: roll = 0.64, pitch = 0.55, yaw = -56.71
XMID_MtData2: roll = 0.73, pitch = 0.34, yaw = -56.90
XMID_MtData2: roll = 0.82, pitch = 0.13, yaw = -57.09
XMID_MtData2: roll = 0.91, pitch = -0.08, yaw = -57.27
XMID_MtData2: roll = 1.00, pitch = -0.28, yaw = -57.46
XMID_MtData2: roll = 1.09, pitch = -0.48, yaw = -57.65
XMID_MtData2: roll = 1.18, pitch = -0.68, yaw = -57.83
...

Press 'c' to switch the device back to config mode.


                          THE MTSSP PROTOCOL EXPLORER

Build the project in the example_mti1_i2c_spi_mtssp_protocol_explorer directory 
and observe that the file example_mti1_i2c_spi_mtssp_protocol_explorer.bin is 
created in the compiler output directory. Run the example on the NUCLEO board, 
either by programming it with the debugger, or by copying the file to the NUCLEO 
virtual drive.

The following text should appear on the terminal window:

    ----------------------------------------------------------------
    Example MTi I2C/SPI: Protocol Explorer
    Bus mode: SPI

    (h) help:     Print this help text
    (R) reset:    Reset the device
    (i) info:     Request protocol information (Opcode 0x01)
    (o) options:  Configure protocol options (Opcode 0x02)
    (c) config:   Goto config mode (Opcode 0x03)
    (m) measure:  Goto measurement mode (Opcode 0x03)
    (d) deviceid: Request device id (Opcode 0x03)
    (f) fwrev:    Request firmware revision (Opcode 0x03)
    (s) status:   Request pipe status (Opcode 0x04))
    (r) read:     Read data from notification or measurement pipe (Opcode 0x05/0x06)

By default, the example uses the SPI bus. The I2C mode can be selected by
changing a macro at the top of the main.cpp file and rebuilding the example. The
following assumes the device is in SPI mode, but the I2C mode works almost
identical.

While using this example, it is best to have the MTi1-s datasheet [2] nearby,
especially section 3.4.3 which explains the MTSSP protocol. Also the Base
article 'Best practices I2C and SPI for MTi 1-series' [4] provides much useful
information.

One of the first things to try is to read the protocol information by pressing 'i'.

The response should look like this:

    Protocol version: 2
    DataReady config: 12 (0x0C)
            Polarity: Idle low
            Output type: Push-pull
            DRDY on notification pipe is enabled
            DRDY on measurement pipe is enabled

When the SPI bus is monitored on the oscilloscope, the following SPI transfer
would be visible

    MOSI:   01 00 00 00 XX XX
    MISO:   FA FF FF FF 02 0C

in which XX are don't care bytes.

On the MOSI line the opcode 0x01 (ProtocolInfo) is sent to the device, followed
by three padding bytes. Next, on the MISO line, the device answers with two
bytes 0x02 0x0C, which are the protocol version (2) and the data ready
configuration (0x0C). For more details, refer to the MTI1-s datasheet [2].


Next we read the pipe status by pressing 's'

The response should be something similar to:

    notificationMessageSize = 3, measurementMessageSize = 18

which means that the length of the first message in the notification pipe is
three bytes, and the first message in the measurement pipe has a length of 18
bytes. Note that the size of the measurement message may vary depending on the
actual configuration of the device. The three byte message in the notification
pipe is expected after a reset. This message should be the Wake-up message.

Next we read the pending data from the notification pipe by entering the read
command (pressing 'r'). Next, press 'n' to select the notification pipe, and
enter '3' to read three bytes. The output on the terminal should be similar to:

    r
    From which pipe?
    Press 'n' for notification pipe
    Press 'm' for measurement pipe
    n
    How many bytes should be read?
    3
    Data read from notification pipe
    3E 00 C3


The response 3E 00 C3 is the Wake-up message from the device, which is the first
message the MTi sends after a power-up. As explained in the datasheet, this
three byte message is the short form of the Xbus message FA FF 3E 00 C3, in
which 3E is the MessageId of the Wake-up message and C3 is the checksum (see [3]).

Next, we can read the pipe status again to see if there is any more data
pending. Whether or not this is the case depends on the configuration of the
device.



                           THE FIRMWARE UPDATE EXAMPLE

Connect an MTi-3 device as described in the Hardware setup section, build the
example_mti1_i2c_spi_firmware_updater project and run it on the NUCLEO board.

Press 'h' in the connected terminal to get the following help menu:

                           
    I2C/SPI Firmware updater example
    Press one of the following keys to execute a command:
    (h) help:       Print this help text
    (R) Reset:      Hard reset the device
    (r) reset:      Soft reset the device
    (v) version:    Request firmware version
    (b) bootloader: Goto bootloader mode
    (u) update:     Start firmware update

Reset the device by pressing 'r'. The device should respond with:

    Got Xbus message: XMID_ResetAck
    Got Xbus message: XMID_Wakeup

Press 'v' to request the firmware version number. You should get the following 
response:

    Got Xbus message: Firmware revision: x.y.z
    
in which x.y.z is the version in major.minor.revision format.

A firmware update can only be started when the device is in bootloader mode. To 
set the device in bootloader mode, press 'b'. You should get the following 
response:

    Got Xbus message: XMID_GotoBootLoaderAck
    Got Xbus message: XMID_FirmwareUpdate

Request the firmware version again by pressing 'v'. The version number should 
now be something like 255.x.y, in which 255 indicates that the bootloader is 
running.

A firmware update can now be started by pressing 'u'. Alternatively, one can 
keep the current firmware and get the device out of bootloader mode by resetting 
or power cycling it.

When 'u' is pressed while the device is in bootloader mode, the firmware update is
started. On the terminal window now some log statements will scroll by. The firmware
update should complete in about 20 seconds. When the firmware update was successful,
the new firmware starts to run automatically and send a wake-up message.

When a firmware update fails half-way for some reason (power outage during the
update, corrupt firmware file, etc.) the device remains in bootloader mode, even 
after a power-cycle. This can be seen by the major version number being 255. 
Normal operation of the device can be restored by a succesful firmware update. 
When a firmware updated is interrupted half-way, the device should be reset, and 
a new firmware update should be started.

The embedded firmware update example provides firmware data for MTi1, MTi2 and 
MTi3 devices. To update an MTi7 device, one must link the file 
src/xffdata_mti7.c instead of src/xffdata_mti3.c. The firmware version which is 
provided with the current example is 1.4.0. For other version, please contact 
Xsens support.

Please note that the firmware update example is only meant to demonstrate the 
Xsens firmware update protocol. For critical applications the code should be 
properly adapted and tested for the specific application.





                                   REMARKS

One particular settings of the device which the user might want to change while
using the protocol explorer example is the Auto-GotoMeasurement setting of the
device. By default, the device automatically goes to measurement mode after
power-up. This means that the measurement pipe will directly start to fill up
with data messages. Since they are not automatically read by the example, the
measurement pipe will quickly overflow, which results in error messages in the
notification pipe. To prevent this, the device can be configured not to
automatically go to measurement mode.

To configure this setting the following Xbus message must be sent to the device:

    FA FF 48 08 00000002 00000000

This message sets the device option flag XDOF_DisableAutoMeasurement in the non-
volatile memory of the device. One way of sending this message is via the
Device Data Viewer dialog of MT-Manager. Refer to the MT-Manager user manual [5]
for further details on how to use MT-Manager. Another way is to modify one of
the embedded examples to make it sent this message.

When using the protocol explorer, no feedback is given by the example after 
executing low-level commands (c) GotoConfig, (m) GotoMeasurement, (d) ReqDID or 
(f) ReqFWRev. Instead, the user should check the response of the MTi by using 
the (s) Pipe Status and (r) read commands.

When using the protocol explorer, as mentioned in [3], the low-level commands 
(d) ReqDID and (f) ReqFWRev can only be used when in Config Mode.


                                  REFERENCES

[1] https://www.xsens.com/download/pdf/documentation/mti-1/mti-1-series_dk_user_manual.pdf
[2] https://www.xsens.com/download/pdf/documentation/mti-1/mti-1-series_datasheet.pdf
[3] https://www.xsens.com/download/usermanual/ISM/MT_LowLevelCommunicationProtocol_Documentation.pdf
[4] https://base.xsens.com/hc/en-us/articles/115002856865-Best-practices-I2C-and-SPI-for-MTi-1-series
[5] https://xsens.com/download/usermanual/ISM/MT_Manager_User_Manual.pdf





