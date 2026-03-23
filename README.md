# SeBot – ROS2 Mobile Robot with Localization & Navigation

[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📌 Overview

SeBot is a ROS2‑based mobile robot platform featuring **localization** (IMU + UWB least‑squares positioning) and **navigation** capabilities. It uses an Arduino for low‑level motor control and integrates the XSens MTi IMU driver, Decawave DWM1001 UWB module, . The repository provides a complete ROS2 workspace with hardware drivers, estimation nodes, and navigation stacks.

For detailed setup, and usage instructions, please refer to the **[docs](./docs)** folder.

## 🚀 Key Features

- **Localization**: UWB‑based position estimation using least‑squares method, fused with IMU data.
- **Navigation**: ROS2 Navigation Stack (Nav2) ready – path planning, obstacle avoidance, and autonomous control.
- **Hardware Integration**: Arduino motor controller, MTi IMU (XSens), and Decawave UWB modules, 2D Lidar.

       