#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/utils.h"
#include "ekf.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include <mutex>

using std::placeholders::_1;

class EkfNode : public rclcpp::Node
{
public:
    EkfNode() : Node("ekf_node")
    {
        ekf_ = std::make_unique<ExtendedKalmanFilter>(0.0, 0.0, 0.0, 0.0);
        ekf_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/filter", 10);

        wheel_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "wheel/odom", 10, std::bind(&EkfNode::wheelCallback, this, _1));
        
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&EkfNode::imuCallback, this, _1));
        
        uwb_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "odometry/uwb_data", 10, std::bind(&EkfNode::uwbCallback, this, _1));

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20), std::bind(&EkfNode::timerCallback, this));

        current_v_ = 0.0;
        initialized_ = false;
    }

private:
    std::unique_ptr<ExtendedKalmanFilter> ekf_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ekf_pub_;    
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr wheel_sub_, uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::TimerBase::SharedPtr timer_;

    rclcpp::Time last_predict_time_;
    double current_v_;
    bool initialized_;
    std::mutex ekf_mutex_;

    void predictStep(const rclcpp::Time & now)
    {
        double dt = (now - last_predict_time_).seconds();
        if (dt > 0) {
            if (dt > 0.2) {
                dt = 0.02;
            }
            ekf_->predict(current_v_, dt);
            last_predict_time_ = now;
        }
    }

    void wheelCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(ekf_mutex_);
        if (!initialized_) {
            initialized_ = true;
            last_predict_time_ = msg->header.stamp;
        }
        current_v_ = msg->twist.twist.linear.x;
        predictStep(msg->header.stamp);
    }

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        if (!initialized_) return;
        std::lock_guard<std::mutex> lock(ekf_mutex_);
        
        predictStep(msg->header.stamp);

        Eigen::VectorXd z(2);
        z << tf2::getYaw(msg->orientation), msg->angular_velocity.z;
        Eigen::VectorXi indices(2);
        indices << 2, 3;
        ekf_->update(z, indices);
    }

    void uwbCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        if (!initialized_) return;
        std::lock_guard<std::mutex> lock(ekf_mutex_);

        predictStep(msg->header.stamp);

        Eigen::VectorXd z(2);
        z << msg->pose.pose.position.x, msg->pose.pose.position.y;
        Eigen::VectorXi indices(2);
        indices << 0, 1;
        ekf_->update(z, indices);
    }

    void timerCallback()
    {
        if (!initialized_) {
            return;
        }
        
        std::lock_guard<std::mutex> lock(ekf_mutex_);
        
        Eigen::VectorXd state = ekf_->getState();
        Eigen::MatrixXd P = ekf_->getP();

        if (std::isnan(state(0)) || std::isnan(state(1))) {
            return;
        }

        nav_msgs::msg::Odometry out_msg;
        out_msg.header.stamp = this->now();
        out_msg.header.frame_id = "map";
        out_msg.child_frame_id = "base_link";

        out_msg.pose.pose.position.x = state(0);
        out_msg.pose.pose.position.y = state(1);
        
        tf2::Quaternion q;
        q.setRPY(0, 0, state(2));
        out_msg.pose.pose.orientation = tf2::toMsg(q);

        std::fill(out_msg.pose.covariance.begin(), out_msg.pose.covariance.end(), 0.0);
        out_msg.pose.covariance[0] = P(0, 0);   
        out_msg.pose.covariance[7] = P(1, 1);   
        out_msg.pose.covariance[35] = P(2, 2);  

        ekf_pub_->publish(out_msg);
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<EkfNode>());
    rclcpp::shutdown();
    return 0;
}
