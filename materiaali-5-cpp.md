### odom and cmd_vel Implemented in C++

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_cmake diffdrivec
```

**~/ros2_ws/src/diffdrivec/src/encoder.hpp**

```cpp
#ifndef ENCODER_HPP
#define ENCODER_HPP

#include <cmath>

class Encoder {
public:
    Encoder(double wheel_radius, int ticks_per_revolution);

    void update(int encoder);
    double deltam();

private:
    static constexpr int encoder_min_ = -32768;
    static constexpr int encoder_max_ = 32768;
    static constexpr int encoder_range_ = encoder_max_ - encoder_min_;
    static constexpr double encoder_low_wrap_ = ((encoder_max_ - encoder_min_) * 0.3) + encoder_min_;
    static constexpr double encoder_high_wrap_ = ((encoder_max_ - encoder_min_) * 0.7) + encoder_min_;

    double wheel_radius_;
    int ticks_per_revolution_;
    double ticks_per_meter_;

    int offset_;
    int encoder_;
    int prev_encoder_;
    double position_;
    double prev_position_;

    int multiplier_;
    bool initialized_ = false;
    bool prev_position_initialized_ = false;
};

#endif // ENCODER_HPP
```

**~/ros2_ws/src/diffdrivec/src/encoder.cpp**

```cpp
#include "encoder.hpp"

Encoder::Encoder(double wheel_radius, int ticks_per_revolution)
    : wheel_radius_(wheel_radius),
      ticks_per_revolution_(ticks_per_revolution),
      ticks_per_meter_(ticks_per_revolution / (2.0 * M_PI * wheel_radius)),
      offset_(0),
      encoder_(0),
      prev_encoder_(0),
      position_(0),
      prev_position_(0),
      multiplier_(0),
      initialized_(false),
      prev_position_initialized_(false) {}

void Encoder::update(int encoder) {
    if (!initialized_) {
        offset_ = encoder;
        prev_encoder_ = encoder;
        initialized_ = true;
    }

    encoder_ = encoder;

    if ((encoder_ < encoder_low_wrap_) && (prev_encoder_ > encoder_high_wrap_)) {
        multiplier_++;
    } else if ((encoder_ > encoder_high_wrap_) && (prev_encoder_ < encoder_low_wrap_)) {
        multiplier_--;
    }

    position_ = encoder_ + multiplier_ * encoder_range_ - offset_;
    prev_encoder_ = encoder_;
}

double Encoder::deltam() {
    if (!prev_position_initialized_) {
        prev_position_ = position_;
        prev_position_initialized_ = true;
        return 0.0;
    } else {
        double d = (prev_position_ - position_) / ticks_per_meter_;
        prev_position_ = position_;
        return d;
    }
}
```

**~/ros2_ws/src/diffdrivec/src/odom.cpp**

```cpp
#include "rclcpp/rclcpp.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include <tf2/LinearMath/Quaternion.h>
#include "motordriver_msgs/msg/motordriver_message.hpp"
#include "encoder.hpp"
#include <cmath>

class OdomNode : public rclcpp::Node {
public:
    OdomNode() : Node("odom"), theta_(0.0), x_(0.0), y_(0.0) {
        // Declare parameters
        this->declare_parameter("wheel_radius", 0.1);
        this->declare_parameter("wheel_base", 0.5);
        this->declare_parameter("ticks_per_revolution", 1075);

        // Get parameter values
        wheel_radius_ = this->get_parameter("wheel_radius").as_double();
        wheel_base_ = this->get_parameter("wheel_base").as_double();
        ticks_per_revolution_ = this->get_parameter("ticks_per_revolution").as_int();

        RCLCPP_INFO(this->get_logger(), "Wheel radius: %f", wheel_radius_);
        RCLCPP_INFO(this->get_logger(), "Wheel base: %f", wheel_base_);
        RCLCPP_INFO(this->get_logger(), "Ticks per revolution: %d", ticks_per_revolution_);

        left_encoder_ = std::make_unique<Encoder>(wheel_radius_, ticks_per_revolution_);
        right_encoder_ = std::make_unique<Encoder>(wheel_radius_, ticks_per_revolution_);

        // Create subscriptions and publishers
        motor_subscriber_ = this->create_subscription<motordriver_msgs::msg::MotordriverMessage>(
            "motor_data", 10, std::bind(&OdomNode::updateEncodersCallback, this, std::placeholders::_1));

        odom_publisher_ = this->create_publisher<nav_msgs::msg::Odometry>("odom", 10);

        tf_broadcaster_ = std::make_shared<tf2_ros::TransformBroadcaster>(this);

        prev_time_ = this->get_clock()->now();

        timer_ = this->create_wall_timer(std::chrono::milliseconds(100), std::bind(&OdomNode::timerCallback, this));
    }

private:
    void updateEncodersCallback(const motordriver_msgs::msg::MotordriverMessage::SharedPtr msg) {
        left_encoder_->update(msg->encoder1);
        right_encoder_->update(-msg->encoder2);
    }

    void timerCallback() {
        auto current_time = this->get_clock()->now();
        double elapsed = (current_time - prev_time_).seconds();
        prev_time_ = current_time;

        double d_left = left_encoder_->deltam();
        double d_right = right_encoder_->deltam();

        double delta_distance = (d_left + d_right) / 2.0;
        double delta_theta = (d_left - d_right) / wheel_base_;

        if (delta_distance != 0) {
            double x = std::cos(delta_theta) * delta_distance;
            double y = -std::sin(delta_theta) * delta_distance;
            x_ += std::cos(theta_) * x - std::sin(theta_) * y;
            y_ += std::sin(theta_) * x + std::cos(theta_) * y;
        }

        theta_ = std::atan2(std::sin(theta_ + delta_theta), std::cos(theta_ + delta_theta));

        // **Calculate velocities**
        double linear_velocity = delta_distance / elapsed;
        double angular_velocity = delta_theta / elapsed;

        // Create and publish Odometry message
        auto odom_msg = nav_msgs::msg::Odometry();
        odom_msg.header.stamp = current_time;
        odom_msg.header.frame_id = "odom";
        odom_msg.child_frame_id = "base_footprint";

        odom_msg.pose.pose.position.x = x_;
        odom_msg.pose.pose.position.y = y_;
        odom_msg.pose.pose.position.z = 0.0;

        auto quat = tf2::Quaternion();
        quat.setRPY(0.0, 0.0, theta_);
        odom_msg.pose.pose.orientation.x = quat.x();
        odom_msg.pose.pose.orientation.y = quat.y();
        odom_msg.pose.pose.orientation.z = quat.z();
        odom_msg.pose.pose.orientation.w = quat.w();

        // **Add twist (linear and angular velocities)**
        odom_msg.twist.twist.linear.x = linear_velocity * std::cos(theta_);
        odom_msg.twist.twist.linear.y = linear_velocity * std::sin(theta_);
        odom_msg.twist.twist.linear.z = 0.0;

        odom_msg.twist.twist.angular.x = 0.0;
        odom_msg.twist.twist.angular.y = 0.0;
        odom_msg.twist.twist.angular.z = angular_velocity;

        odom_publisher_->publish(odom_msg);

        // Create and send Transform
        geometry_msgs::msg::TransformStamped t;
        t.header.stamp = current_time;
        t.header.frame_id = "odom";
        t.child_frame_id = "base_footprint";

        t.transform.translation.x = x_;
        t.transform.translation.y = y_;
        t.transform.translation.z = 0.0;
        t.transform.rotation.x = quat.x();
        t.transform.rotation.y = quat.y();
        t.transform.rotation.z = quat.z();
        t.transform.rotation.w = quat.w();

        tf_broadcaster_->sendTransform(t);
    }

    // Parameters
    double wheel_radius_;
    double wheel_base_;
    int ticks_per_revolution_;

    // State variables
    double theta_;
    double x_;
    double y_;

    // ROS 2 interfaces
    rclcpp::Subscription<motordriver_msgs::msg::MotordriverMessage>::SharedPtr motor_subscriber_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_publisher_;
    std::shared_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

    std::unique_ptr<Encoder> left_encoder_;
    std::unique_ptr<Encoder> right_encoder_;

    rclcpp::Time prev_time_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<OdomNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}
```

**~/ros2_ws/src/diffdrivec/src/cmd_vel.cpp**

```cpp
#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "std_msgs/msg/string.hpp"
#include <cmath>
#include <string>

class CmdVelNode : public rclcpp::Node {
public:
    CmdVelNode() : Node("cmd_vel") {
        // Read parameters
        this->declare_parameter<double>("wheel_radius", 0.1);
        this->declare_parameter<double>("wheel_base", 0.5);

        // Get parameter values
        wheel_radius_ = this->get_parameter("wheel_radius").as_double();
        wheel_base_ = this->get_parameter("wheel_base").as_double();

        RCLCPP_INFO(this->get_logger(), "Wheel radius: %f", wheel_radius_);
        RCLCPP_INFO(this->get_logger(), "Wheel base: %f", wheel_base_);

        // Create subscribers and publishers
        cmd_vel_subscriber_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "cmd_vel",
            10,
            std::bind(&CmdVelNode::cmdVelCallback, this, std::placeholders::_1)
        );

        mc_publisher_ = this->create_publisher<std_msgs::msg::String>(
            "motor_command",
            10
        );
    }

private:
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        // Calculate left and right wheel speeds
        double vel_l = +((msg->linear.x + (msg->angular.z * wheel_base_ / 2.0)) / wheel_radius_) * 60 / (2 * M_PI);
        double vel_r = -((msg->linear.x - (msg->angular.z * wheel_base_ / 2.0)) / wheel_radius_) * 60 / (2 * M_PI);

        // Create and publish motor_command message
        auto string_msg = std_msgs::msg::String();
        string_msg.data = "SPD;" + std::to_string(static_cast<int>(vel_l)) + ";" + std::to_string(static_cast<int>(vel_r)) + ";";
        mc_publisher_->publish(string_msg);
    }

    // Parameters
    double wheel_radius_;
    double wheel_base_;

    // ROS 2 subscribers and publishers
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_subscriber_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr mc_publisher_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<CmdVelNode>();
    rclcpp::spin(node);

    rclcpp::shutdown();
    return 0;
}
```

**~/ros2_ws/src/diffdrivec/CMakeLists.txt**

```bash
cmake_minimum_required(VERSION 3.8)
project(diffdrivec)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(motordriver_msgs REQUIRED)

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

# Add the Encoder library
add_library(encoder src/encoder.cpp)
target_include_directories(encoder PUBLIC include)
ament_target_dependencies(encoder rclcpp)

add_executable(cmd_vel src/cmd_vel.cpp)
ament_target_dependencies(cmd_vel rclcpp geometry_msgs std_msgs)

install(TARGETS
  cmd_vel
  DESTINATION lib/${PROJECT_NAME})

# Add the odom executable
add_executable(odom src/odom.cpp)
ament_target_dependencies(odom rclcpp nav_msgs geometry_msgs tf2_ros motordriver_msgs)
target_link_libraries(odom encoder)

# Install the encoder library
install(TARGETS
  encoder
  DESTINATION lib/${PROJECT_NAME})

# Install the odom executable
install(TARGETS
  odom
  DESTINATION lib/${PROJECT_NAME})

ament_package()
```

**~/ros2_ws/src/diffdrivec/package.xml**

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
  <name>diffdrivec</name>
  <version>0.0.0</version>
  <description>TODO: Package description</description>
  <maintainer email="ros2@todo.todo">ros2</maintainer>
  <license>TODO: License declaration</license>

  <buildtool_depend>ament_cmake</buildtool_depend>

  <test_depend>ament_lint_auto</test_depend>
  <test_depend>ament_lint_common</test_depend>

  <build_depend>rclcpp</build_depend>
  <build_depend>geometry_msgs</build_depend>
  <build_depend>std_msgs</build_depend>
  <build_depend>nav_msgs</build_depend>
  <build_depend>tf2_ros</build_depend>
  <build_depend>motordriver_msgs</build_depend>

  <exec_depend>rclcpp</exec_depend>
  <exec_depend>geometry_msgs</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>nav_msgs</exec_depend>
  <exec_depend>tf2_ros</exec_depend>
  <exec_depend>motordriver_msgs</exec_depend>

  <export>
    <build_type>ament_cmake</build_type>
  </export>
</package>
```

Compilation and Launch

```bash
cd ~/ros2_ws
colcon build --packages-select diffdrivec

source ~/ros2_ws/install/setup.bash

# note, python versions use the same topic names, so
# stop them or give the topics new names to avoid conflicts

ros2 run diffdrivec odom
ros2 run diffdrivec cmd_vel
```

- Nomga Oy - SeAMK - ROS 2 and motor control: From PWM signal to robot motion control
