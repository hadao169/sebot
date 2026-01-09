# Localization System Architecture Documentation

This document details the two localization architectures designed for the robot: **Single EKF (Loosely Coupled)** and **Dual EKF (Local & Global Fusion)**.

---

## DOCUMENT 1: SINGLE EKF ARCHITECTURE (LOOSELY COUPLED)

### 1. System Overview
The **Single EKF (Loosely Coupled)** architecture utilizes a single Extended Kalman Filter (EKF) instance to fuse all sensor data sources: **Wheel Odometry**, **IMU**, and **UWB**. 

This system is suitable for:
* Environments with minimal obstacles.
* Scenarios where UWB signals are relatively stable (Line-of-Sight).
* Systems with limited computational resources.

The core mechanism is the **Closed-loop Feedback**: The output pose from the EKF is fed back to the UWB pre-processing node to assist in correcting the raw UWB data (specifically for offset compensation).



### 2. Data Flow

The system consists of three main components working in coordination:

#### A. Hardware Drivers
* **Wheel Encoder:** Provides linear velocity ($v_x$) and angular velocity ($v_{yaw}$).
* **IMU (Xsens):** Provides acceleration and angular velocity, specifically precise Heading ($Yaw$).
* **UWB (Decawave):** Provides raw Euclidean coordinates ($x, y$) relative to the fixed Anchors.

#### B. UwbTransformNode (Pre-processor)
This is a critical intermediary node that handles spatial data transformation.
* **Inputs:**
    * `/dwm1001/DW878F/pose`: Raw UWB pose.
    * `/odometry/filtered/global`: Feedback data from the EKF.
    * **TF (`base_link` -> `uwb_link`):** Static mounting offset via TF tree.
* **Functions:**
    1.  **Datum Alignment:** Determines the origin $(0,0)$ and initial rotation of the UWB frame relative to the Map frame.
    2.  **Offset Compensation:** Uses the current Robot $Yaw$ (from EKF feedback) to rotate the mounting offset vector, thereby calculating the robot's center position from the sensor's position.
* **Output:** `/odometry/uwb` (Corrected robot position in Map frame).

#### C. EkfNode (Sensor Fusion)
* **Inputs:**
    * `/wheel/odom`: Used for the **Predict** step (State prediction).
    * `/imu/data`: Used for the **Update** step (Heading correction).
    * `/odometry/uwb`: Used for the **Update** step (Absolute position correction).
* **Output:** `/odometry/filtered/global` (Final estimated state).

### 3. TF Tree
In this Single EKF model, the TF tree is simplified:

`map` $\rightarrow$ `base_link` $\rightarrow$ `uwb_link`

* **EkfNode** publishes the transform from `map` to `base_link`.
* **Static Publisher** publishes the transform from `base_link` to `uwb_link`.

### 4. Pros and Cons
* **Pros:** Simple architecture, easy to deploy, low latency (single filter path), efficient CPU usage.
* **Cons:** Sensitive to noise. If UWB data contains outliers (jumps), the EKF may be pulled incorrectly, corrupting the estimated $Yaw$. This incorrect Yaw feeds back into the Offset calculation, potentially creating a **positive feedback loop** that destabilizes the system.

---

## DOCUMENT 2: DUAL EKF ARCHITECTURE (LOCAL & GLOBAL FUSION)

### 1. System Overview
The **Dual EKF** architecture adheres to the ROS industrial standard (**REP-105**), separating state estimation into two layers: **Local** (smooth/continuous) and **Global** (absolute/accurate).

The goal is to ensure the robot moves smoothly for control purposes (PID/Path tracking) while maintaining accurate global positioning on the map.



### 2. Node Structure

#### A. EKF Local (Continuous Filter)
* **Role:** Estimates the robot's motion relative to its starting point (Odom frame).
* **Inputs:** Uses only continuous sensors: **Wheel Odometry** + **IMU**.
* **Output:** Topic `/odometry/filtered/local`.
* **TF:** Publishes the `odom` $\rightarrow$ `base_link` transform.
* **Characteristics:** Extremely smooth data, no discrete jumps, but subject to drift over time.

#### B. EKF Global (Absolute Filter)
* **Role:** Estimates absolute position on the map, correcting the drift of the Local EKF.
* **Inputs:** **Local Odometry** (as a source) + **IMU** + **UWB**.
* **Output:** Topic `/odometry/filtered/global`.
* **TF:** Publishes the `map` $\rightarrow$ `odom` transform.
* **Characteristics:** Geographically accurate, but the pose may "jump" when UWB signals are unstable.

#### C. UwbTransformNode (Bridge)
This node is adjusted to break the dangerous feedback loop found in the Single EKF model.
* **Key Change:** Instead of listening to the Global EKF, this node listens to the **Local EKF** (`/odometry/filtered/local`).
* **Reasoning:** The $Yaw$ from the Local EKF is highly stable (derived only from Gyro/Encoders). Using this stable Yaw to compensate for UWB Offset ensures the output UWB data remains clean, even if the Global EKF is experiencing coordinate jumps.

### 3. TF Tree
The TF tree fully complies with ROS REP-105 standards:

`map` $\xrightarrow{\text{EKF Global}}$ `odom` $\xrightarrow{\text{EKF Local}}$ `base_link` $\xrightarrow{\text{Static}}$ `uwb_link`

1.  **`map` -> `odom`**: Represents the accumulated drift of the robot relative to the real-world map. The Global EKF calculates and publishes this link.
2.  **`odom` -> `base_link`**: Represents the smooth, continuous motion of the robot. The Local EKF publishes this link.

### 4. Pros and Cons
* **Pros:**
    * **High Stability:** Robot control is smooth due to the Local EKF.
    * **Safety:** Fault isolation. If UWB fails or sends bad data, the robot continues to operate smoothly using the Local EKF (for short durations).
    * **Accuracy:** The Offset compensation logic uses the stable Local Yaw, eliminating jitter/oscillation noise.
* **Cons:** More complex configuration (requires two config files, careful TF management). Higher CPU resource consumption (running two filters in parallel).

---

### Summary Recommendation
* **Choose Document 1 (Single EKF)** if you are working on a smaller scale project, a simple environment, or have limited hardware resources.
* **Choose Document 2 (Dual EKF)** if you are aiming for a commercial product, a robust navigation stack, or operating in complex environments (e.g., warehouses).