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
    OdomNode() : Node("odom_node"), theta_(0.0), x_(0.0), y_(0.0) {
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

