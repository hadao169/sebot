import rclpy
import time
import serial
import numpy as np

from rclpy.node import Node
from .dwm1001_apiCommands import DWM1001_API_COMMANDS
# from geometry_msgs.msg import PoseStamped
# from .KalmanFilter import KalmanFilter as kf
from .Helpers import get_tag_publisher, update_multitags_list, create_pose_stamped, CsvLogger
from .uwb_processor import UWBProcessor
from nav_msgs.msg import Odometry
from citrack_ros_msgs.msg import CustomTag
import re
# import traceback

class dwm1001_localizer(Node):

    def __init__(self):
        Node.__init__(self, 'DWM1001_Listener_Mode')

        self.topics = {}
        self.topics_kf = {}
        self.kalman_list = {}
        self.topics_ls = {}
        self.logger = CsvLogger()

        self.declare_parameter('port', '/dev/ttyACM0')
        self.declare_parameter('verbose', True)
        self.declare_parameter('read_rate', 10.0)
        self.declare_parameter('tag_id', '0xDECAC2066165878F')
        self.declare_parameter('mac_id', 'C4:22:04:B9:DE:53')
        self.declare_parameter('use_least_square', True)
        self.declare_parameter('least_square_max_iterations', 20)
        self.declare_parameter('least_square_tolerance', 0.001)

        self.dwm_port = self.get_parameter(
            'port').get_parameter_value().string_value
        self.verbose = self.get_parameter(
            'verbose').get_parameter_value().bool_value
        self.tag_id = int(self.get_parameter(
            'tag_id').get_parameter_value().string_value, 16)
        self.tag_macID = self.get_parameter(
            'mac_id').get_parameter_value().string_value
        self.read_rate = self.get_parameter(
            'read_rate').get_parameter_value().double_value
        self.use_least_square = self.get_parameter(
            'use_least_square').get_parameter_value().bool_value
        self.least_square_max_iterations = self.get_parameter(
            'least_square_max_iterations').get_parameter_value().integer_value
        self.least_square_tolerance = self.get_parameter(
            'least_square_tolerance').get_parameter_value().double_value

        self.uwb_processor = UWBProcessor()

        self.anchor_pattern = re.compile(
            r"([0-9A-F]{4})\[\s*([-0-9.]+),\s*([-0-9.]+),\s*([-0-9.]+)\]\s*=\s*([-0-9.]+)"
        )

        self.pub_fix = self.create_publisher(Odometry, "uwb/fix", 10)

        timer_period = 1.0 / self.read_rate
        self.serialPortDWM1001 = serial.Serial(
            port=self.dwm_port,
            baudrate=115200,
            parity=serial.PARITY_NONE,
            bytesize=serial.EIGHTBITS,
            timeout=1.0
        )
        self.timer = self.create_timer(
            timer_period, self.serial_read_callback)

    def initialize_hardware(self):
        self.serialPortDWM1001.close()
        time.sleep(0.1)
        self.serialPortDWM1001.open()

        if (self.serialPortDWM1001.isOpen()):
            self.initializeDWM1001API()
            time.sleep(2)

            if self.use_least_square:
                self.serialPortDWM1001.write(DWM1001_API_COMMANDS.LES)
            else:
                self.serialPortDWM1001.write(DWM1001_API_COMMANDS.LEP)

            self.serialPortDWM1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
            serialReadLine = self.serialPortDWM1001.read_until()
            self.get_logger().info(serialReadLine)
        else:
            raise IOError("Serial Port Failed to Open")

    def shutdown_hardware(self):
        try:
            self.serialPortDWM1001.write(DWM1001_API_COMMANDS.RESET)
            self.serialPortDWM1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
            time.sleep(0.5)
            self.serialPortDWM1001.read_until()

            if self.serialPortDWM1001.isOpen():
                self.serialPortDWM1001.close()

        except Exception:
            pass
            
    def initializeDWM1001API(self):
        self.serialPortDWM1001.write(DWM1001_API_COMMANDS.RESET)
        self.serialPortDWM1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serialPortDWM1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)
        time.sleep(0.5)
        self.serialPortDWM1001.write(DWM1001_API_COMMANDS.SINGLE_ENTER)

    def _extract_pose_data(self, serialData) -> list | None:
        if not serialData:
            return None
        try:
            serialDataList = [x.strip()
                              for x in serialData.strip().split(b',')]
            if b"POS" not in serialDataList[0]:
                return None

            t_pose_x = float(serialDataList[1].decode('utf-8'))
            t_pose_y = float(serialDataList[2].decode('utf-8'))
            t_pose_z = float(serialDataList[3].decode('utf-8'))
            t_pose_list = [t_pose_x, t_pose_y, t_pose_z]

            if np.isnan(t_pose_list).any():
                return None

            return t_pose_list

        except (IndexError, ValueError):
            return None

    def serial_read_callback(self):
        try:
            line = self.serialPortDWM1001.readline().decode('utf-8').strip()
            if not line:
                return
            # DEBUG (rất nên bật lúc đầu)
            self.get_logger().info(line)
            matches = self.anchor_pattern.findall(line)

            if self.use_least_square and len(matches) >= 4:

                anchor_ids = []
                anchors = []
                distances = []

                for m in matches:
                    anchor_ids.append(m[0])
                    anchors.append([
                        float(m[1]),
                        float(m[2]),
                        float(m[3])
                    ])
                    distances.append(float(m[4]))

                pos = self.uwb_processor.process(anchor_ids, anchors, distances)

                if pos is not None:
                    self.publishTagPoseLS(pos)

            # fallback: dùng est từ hardware
            elif not self.use_least_square:
                pose_data = self._extract_pose_data(line.encode())
                if pose_data:
                    self.publishTagPositions(pose_data)

        except Exception as e:
            self.get_logger().error(f"Serial error: {e}")

    def publishTagPoseLS(self, pos):

        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = "map"
        msg.child_frame_id = "base_link"

        msg.pose.pose.position.x = float(pos[0])
        msg.pose.pose.position.y = float(pos[1])
        msg.pose.pose.position.z = float(pos[2])

        msg.pose.pose.orientation.w = 1.0

        self.pub_fix.publish(msg)        
        

    def publishTagPositions(self, pose_data: list):
        """Publish raw pose data (Non-KF) to ROS."""
        ps = create_pose_stamped(self, pose_data, self.tag_id)
        tag = CustomTag()
        tag.header = ps.header
        tag.pose_x = ps.pose.position.x
        tag.pose_y = ps.pose.position.y
        tag.pose_z = ps.pose.position.z
        tag.orientation_x = ps.pose.orientation.x
        tag.orientation_y = ps.pose.orientation.y
        tag.orientation_z = ps.pose.orientation.z
        tag.orientation_w = ps.pose.orientation.w

        pub = get_tag_publisher(
            self, self.topics, self.tag_id, suffix="pose")
        pub.publish(ps)


def main(args=None):
    rclpy.init(args=args)
    dwm1001 = dwm1001_localizer()
    try:
        dwm1001.initialize_hardware()
        rclpy.spin(dwm1001)
    except KeyboardInterrupt:
        pass
    except IOError:
        pass
    finally:
        dwm1001.shutdown_hardware()
        dwm1001.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

