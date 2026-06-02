// ukf_node.cpp
#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/utils.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include <memory>
#include <mutex>

#include "ukf.hpp"  // DifferentialDriveUKF

using namespace std::placeholders;

class UkfNode : public rclcpp::Node {
public:
    UkfNode() : Node("ukf_node") {
        ukf_ = std::make_unique<DifferentialDriveUKF>();
        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/ukf_filter", 10);

        wheel_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "wheel/odom", 10,
            std::bind(&UkfNode::wheelCallback, this, _1));

        uwb_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "odometry/uwb_data", 10,
            std::bind(&UkfNode::uwbCallback, this, _1));

        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10,
            std::bind(&UkfNode::imuCallback, this, _1));

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20),  
            std::bind(&UkfNode::timerCallback, this));

        initialized_ = false;
        current_v_ = 0.0;
        current_w_ = 0.0;
    }

private:
    std::unique_ptr<DifferentialDriveUKF> ukf_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr wheel_sub_, uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::TimerBase::SharedPtr timer_;

    mutable std::mutex ukf_mutex_;
    rclcpp::Time last_predict_time_;
    double current_v_, current_w_;
    bool initialized_;

    void predictStep(rclcpp::Time now) {
        double dt = (now - last_predict_time_).seconds();
        if (dt <= 0) return;
        if (dt > 0.2) dt = 0.02;  
				RCLCPP_INFO(this->get_logger(), "dt%.3f", dt);
        ukf_->predict(dt, current_v_, current_w_);
        last_predict_time_ = now;
    }

    void wheelCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        if (!initialized_) return;

        std::lock_guard<std::mutex> lock(ukf_mutex_);
        current_v_ = msg->twist.twist.linear.x;
        current_w_ = msg->twist.twist.angular.z;
        predictStep(msg->header.stamp);
    }

    void uwbCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        std::lock_guard<std::mutex> lock(ukf_mutex_);

        if (!initialized_) {
            ukf_->x << msg->pose.pose.position.x, msg->pose.pose.position.y, 0.0;
            initialized_ = true;
            last_predict_time_ = msg->header.stamp;
            RCLCPP_INFO(this->get_logger(), "UKF Initialized (x=%.3f, y=%.3f)", ukf_->x(0), ukf_->x(1));
            return;
        }

        predictStep(msg->header.stamp);

        Eigen::VectorXd z(2);
        z << msg->pose.pose.position.x, msg->pose.pose.position.y;
        ukf_->updateUWB(z);
    }

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg) {
        if (!initialized_) return;

        double w_imu = msg->angular_velocity.z;
        double theta_imu = tf2::getYaw(msg->orientation);

        std::lock_guard<std::mutex> lock(ukf_mutex_);
        current_w_ = w_imu;
        predictStep(msg->header.stamp);

        ukf_->updateIMU_Yaw(theta_imu);
    }

    void timerCallback() {
        if (!initialized_) return;

        std::lock_guard<std::mutex> lock(ukf_mutex_);
        auto x = ukf_->x;
        auto P = ukf_->P;

        nav_msgs::msg::Odometry odom;
        odom.header.stamp = this->now();
        odom.header.frame_id = "map";
        odom.child_frame_id = "base_link";

        odom.pose.pose.position.x = x(0);
        odom.pose.pose.position.y = x(1);
        tf2::Quaternion q;
        q.setRPY(0, 0, x(2));
        odom.pose.pose.orientation = tf2::toMsg(q);

        odom.twist.twist.linear.x  = current_v_;
        odom.twist.twist.angular.z = current_w_;

        std::fill(odom.pose.covariance.begin(), odom.pose.covariance.end(), 0.0);
        odom.pose.covariance[0]  = P(0, 0);  
        odom.pose.covariance[7]  = P(1, 1);  
        odom.pose.covariance[35] = P(2, 2);  

        odom_pub_->publish(odom);
    }
};

int main(int argc, char** argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<UkfNode>());
    rclcpp::shutdown();
    return 0;
}