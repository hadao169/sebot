#!/usr/bin/env python3

# The helper functions regarding motion models for Kalman filter implementation
import numpy as np 


# Initialize the Constant Velocity model for UWB-based Positioning in KF 
def initConstVelocityKF():

    dt = 0.1    # system update rate (10 Hz)
    
    # variance of the measurement noise, supposing the error is 15 cm (0.15 * 0.15) on X- & Y-axes
    # Tune the values based on your set-up and the demanded performance
    v_n = np.array([ 0.0225, 0.0225,  0.08])
    sigma_sq = 0.01    # Process noise value based on 10cm precision
    
    # Initial assumed values of the state which includes pose and their corresponding velocites
    x_0 = np.array([1.2, 1.82 , 0.885 , 1, 2, 1.5])  #  Initial guest
    x_0.shape = (len(x_0),1)      # force to be a column vector (6,1)
    
    # Initial value of State Covariance Matrix or Error Covariance 
    P_0 = np.multiply(2, np.eye(6))
    
    # State Model or Transition Matrix 
    A = np.array([[1, 0, 0, dt, 0, 0],
                  [0, 1, 0, 0, dt, 0],
                  [0, 0, 1, 0, 0, dt],
                  [0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 1]])
    
    B = 0 # No control input
    
    #  Relation b/w the observed Measurement and the State vector
    H = np.array([[1, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0]])
    
    # Measurement Noise Covariance
    R = np.array([[v_n[0], 0, 0],
                  [0, v_n[1], 0],
                  [0, 0, v_n[2]]])
    
    '''
    Process Noise Covariance (6x6)
    Ref1: Survey of Maneuvering Target Tracking. Part I: Dynamic Models bz X. Rong Li and et.
    Ref2: Estimation with applications to Tracking and Navigation by Z. Bar-Shalom and et al. [chap. 6]
    Ref3: Mobile Positioning and Tracking (2nd Edition) by S. Frattasi & F. D. Rosa [sec: 6.4]
    '''
    q_uD = (np.power(dt, 4))/4   # (dt, 3)/3  in some lit.
    q_oD = (np.power(dt, 3))/2   # (dt, 2)/2  in some lit.
    q_lD = np.square(dt)         # dt         in some lit.
    
    Q_0 = np.array([[q_uD, 0, 0, q_oD, 0, 0],
                    [0, q_uD, 0, 0, q_oD, 0],
                    [0, 0, q_uD, 0, 0, q_oD],
                    [q_oD, 0, 0, q_lD, 0, 0],
                    [0, q_oD, 0, 0, q_lD, 0],
                    [0, 0, q_oD, 0, 0, q_lD]])

    Q = Q_0 * sigma_sq
    
    return A, B, H, Q, R, P_0, x_0 


# Constant acceleration Motion Model for UWB-based Positioning in KF 
def initConstAccelerationKF():
    
    dt = 0.1    # system update rate (10Hz)
    
    # variance of the measurement noise, supposing the error is 15 cm (0.15 * 0.15) on X- & Y-axes
    # Tune the values based on your set-up and the demanded performance
    v_n = np.array([ 0.0225, 0.0225,  0.08])
    sigma_sq = 0.01    # Process noise value based on 10cm precision

    # Initial guest for state vector 
    x_0 = np.array([1.2, 1.82 , 0.885 , 1, 2, 1.5, 0.5, 1.0, 0.75])  #  Initial guest
    x_0.shape = (len(x_0),1)      # force to be a column vector  (9, 1)

    # Initial guese of State Covariance Matrix shoudn't be zeros 
    P_0 = np.multiply(2, np.eye(len(x_0)))  # (9x9)


    # State Model or Transition Matrix  (9x9)
    A_oD = (np.power(dt, 2))/2  # coefficient for acceleration (off-diagonal)
    A = np.array([[1, 0, 0, dt, 0, 0, A_oD, 0, 0],
                  [0, 1, 0, 0, dt, 0, 0, A_oD, 0],
                  [0, 0, 1, 0, 0, dt, 0, 0, A_oD],
                  [0, 0, 0, 1, 0, 0, dt, 0, 0],
                  [0, 0, 0, 0, 1, 0, 0, dt, 0],
                  [0, 0, 0, 0, 0, 1, 0, 0, dt],
                  [0, 0, 0, 0, 0, 0, 1, 0, 0],
                  [0, 0, 0, 0, 0, 0, 0, 1, 0],
                  [0, 0, 0, 0, 0, 0, 0, 0, 1]])

    B = 0 # No control input
    
    #  Relation b/w the observed Measurement and the State vector (3x9)
    H = np.array([[1, 0, 0, 0, 0, 0, 0, 0, 0],
                  [0, 1, 0, 0, 0, 0, 0, 0, 0],
                  [0, 0, 1, 0, 0, 0, 0, 0, 0]])
    
    # Measurement Noise Covariance (3x3) 
    R = np.array([[v_n[0], 0, 0],
                  [0, v_n[1], 0],
                  [0, 0, v_n[2]]])
    
    '''
    Process Noise Covariance (9x9)
    Ref1: Survey of Maneuvering Target Tracking. Part I: Dynamic Models bz X. Rong Li and et.
    Ref2: Estimation with applications to Tracking and Navigation by Z. Bar-Shalom and et al. [chap. 6]
    Ref3: Mobile Positioning and Tracking (2nd Edition) by S. Frattasi & F. D. Rosa [sec: 6.4]
    '''
    q_t4 = (np.power(dt, 4))/4   # (dt, 3)/3  in some lit.
    q_t3 = (np.power(dt, 3))/2   # (dt, 2)/2  in some lit.
    q_t2 = np.square(dt)         # dt         in some lit.
    
    Q_0 = np.array([[q_t4, 0, 0, q_t3, 0, 0, q_t2, 0, 0],
                    [0, q_t4, 0, 0, q_t3, 0, 0, q_t2, 0],
                    [0, 0, q_t4, 0, 0, q_t3, 0, 0, q_t2],
                    [q_t3, 0, 0, q_t2, 0, 0, dt, 0, 0],
                    [0, q_t3, 0, 0, q_t2, 0, 0, dt, 0],
                    [0, 0, q_t3, 0, 0, q_t2, 0, 0, dt],
                    [q_t2, 0, 0, dt, 0, 0, 1, 0, 0],
                    [0, q_t2, 0, 0, dt, 0, 0, 1, 0],
                    [0, 0, q_t2, 0, 0, dt, 0, 0, 1]])

    Q = Q_0 * sigma_sq
    
    return A, B, H, Q, R, P_0, x_0 


import config


class Measurements:
    """Range measurement class."""

    def __init__(self) -> None:
        # Measured ranges.
        self.r1 = 0
        self.r2 = 0
        self.r3 = 0
        self.r4 = 0
        # Estimated position.
        self.px = 0
        self.py = 0
        self.pz = 0
        # Quality factor.
        self.qf = 0


def read_measurements(output: str) -> Measurements:
    """
    Read the range measurements and the estimated position of the tag.

    :param str output: Output of the 'les' shell command.
    :return: An instance of the Measurements class.
    :rtype: object

    """
    measurements = Measurements()
    
    for item in output.split(" "):
        if item.startswith("le_us"):
            continue
        
        elif item.startswith("est"):
            position = item.split("[")[1].split("]")[0].split(",")
            measurements.px = float(position[0])
            measurements.py = float(position[1])
            measurements.pz = float(position[2])
            measurements.qf = int(position[3])
        
        else:
            anchor_id = item[0:4]
            measured_range = float(item.split("=")[1])
            if anchor_id == config.ID_ANCHOR1:
                measurements.r1 = measured_range
            elif anchor_id == config.ID_ANCHOR2:
                measurements.r2 = measured_range
            elif anchor_id == config.ID_ANCHOR3:
                measurements.r3 = measured_range
            elif anchor_id == config.ID_ANCHOR4:
                measurements.r4 = measured_range

    return measurements


def validate(output: str) -> bool:
    """
    Validate the output data of the 'les' shell command.

    :param str output: Output data of the 'les' shell command.
    :return: True, if data is valid, False otherwise.
    :rtype: bool

    """
    # The output is expected to contain 4 range measurements, value of
    # the le_us parameter, and the estimated position:
    # <meas1> <meas2> <meas3> <meas4> le_us=<value> est[<px>,<py>,<pz>,<qf>]
    items = output.split(" ")
    if not len(items) == 6:
        return False

    index = output.find("est")
    if index == -1:
        return False
    
    return True


from geometry_msgs.msg import PoseStamped

def get_tag_publisher(node, topics_dict, clean_macID, suffix):
    """Get or create a PoseStamped publisher for a specific tag."""
    topic_name = f"/dwm1001/id_{clean_macID}/{suffix}"
    if topic_name not in topics_dict:
        topics_dict[topic_name] = node.create_publisher(PoseStamped, topic_name, 10)
    return topics_dict[topic_name]

def update_multitags_list(multitags_obj, tag_msg, mac_id):
    """Replace existing tag or append new one."""
    current_idx = [i for i, t in enumerate(multitags_obj.tags_list) if t.header.frame_id == mac_id]
        
    if not current_idx:
        multitags_obj.tags_list.append(tag_msg)
    else:
        multitags_obj.tags_list[current_idx[0]] = tag_msg

def create_pose_stamped(node, xyz, frame_id):
    ps = PoseStamped()
    ps.pose.position.x = float(xyz[0])
    ps.pose.position.y = float(xyz[1])
    ps.pose.position.z = float(xyz[2])
    ps.pose.orientation.x = 0.0
    ps.pose.orientation.y = 0.0
    ps.pose.orientation.z = 0.0
    ps.pose.orientation.w = 1.0
    ps.header.stamp = node.get_clock().now().to_msg()
    ps.header.frame_id = frame_id
    return ps
