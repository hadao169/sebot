import rclpy
import time
import serial
import numpy as np

from rclpy.node import Node
from .dwm1001_apiCommands import DWM1001_API_COMMANDS
# from geometry_msgs.msg import PoseStamped
# from .KalmanFilter import KalmanFilter as kf
from .Helpers import get_tag_publisher, update_multitags_list, create_pose_stamped, CsvLogger
from .LeastSquare import LeastSquare as ls
from citrack_ros_msgs.msg import CustomTag
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
            serialReadLine = self.serialPortDWM1001.readline()
            # self.get_logger().info(serialReadLine.decode('UTF-8'))
            if not serialReadLine:
                return
            pose_data = self._extract_pose_data(serialReadLine)
            if self.use_least_square:
                    self.publishTagPoseLS(self.tag_id, self.tag_macID, serialReadLine, pose_data)
            if pose_data and not self.use_least_square:
                self.publishTagPositions(pose_data)
        except Exception:
            pass

    def publishTagPoseLS(self, tag_id: int, tag_macID: str, serialReadLine, pose_data):
        serialReadLine_str = serialReadLine.decode('UTF-8', errors='ignore')
        raw_uwb_data = serialReadLine_str.strip().split() # ['A1[...]=...', 'A2[...]=...', ...]
        # self.logger.log_raw(raw_uwb_data)

        if tag_macID not in self.topics_ls:
            self.topics_ls[tag_macID] = ls()

        ls_object = self.topics_ls[tag_macID]

        ls_object.process_uwb_data(raw_uwb_data)

        estimated_x, estimated_y = ls_object.estimate_position(
                max_iterations=self.least_square_max_iterations, tolerance=self.least_square_tolerance)
        
        pos = ls_object.original_position

        self.get_logger().info(f"[LS] Estimated: x={estimated_x}, y={estimated_y}")


        xyz = [estimated_x, estimated_y, 0.0]
        ps = create_pose_stamped(self, xyz, tag_macID)
        clean_id_str = tag_macID.replace(':', '_')

        pub = get_tag_publisher(self, self.topics_ls, clean_id_str, suffix="pose_ls")

        pub.publish(ps)
        

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

        update_multitags_list(self.multipleTags, tag, self.tag_macID)

        self.pub_tags.publish(self.multipleTags)


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

