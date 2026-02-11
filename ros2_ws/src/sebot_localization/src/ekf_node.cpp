#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/utils.h"
#include "ekf.hpp"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"

using std::placeholders::_1;

class EkfNode : public rclcpp::Node
{
public:
    EkfNode() : Node("ekf_node")
    {
        ekf_ = std::make_unique<ExtendedKalmanFilter>(0.0, 0.0, 0.0, 0.0, 0.1);

        ekf_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/filtered", 10);

        ekf_synced_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/ekf_synced", 10);

        wheel_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "wheel/odom", 10, std::bind(&EkfNode::wheelCallback, this, _1));
        
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&EkfNode::imuCallback, this, _1));
        
        uwb_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "odometry/uwb_data", 10, std::bind(&EkfNode::uwbCallback, this, _1));
            
        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20), std::bind(&EkfNode::publishEkfState, this));
    }

private:
    std::unique_ptr<ExtendedKalmanFilter> ekf_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ekf_pub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ekf_synced_pub_; // Publisher mới
    
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr wheel_sub_, uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::TimerBase::SharedPtr timer_;

    rclcpp::Time last_time_;
    
    void wheelCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        rclcpp::Time now = msg->header.stamp;
        if (last_time_.nanoseconds() == 0) { last_time_ = now; return; }
        
        double dt = (now - last_time_).seconds();
        last_time_ = now;
        if (dt <= 0 || dt > 1.0) dt = 0.05; 

        ekf_->predict(msg->twist.twist.linear.x, msg->twist.twist.angular.z, dt);
    }

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        double yaw = tf2::getYaw(msg->orientation);
        double wz = msg->angular_velocity.z;

        Eigen::VectorXd z(2);
        z << yaw, wz;
        Eigen::VectorXi indices(2);
        indices << 2, 3;
        ekf_->update(z, indices);
    }

    void uwbCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        Eigen::VectorXd z(2);
        z << msg->pose.pose.position.x, msg->pose.pose.position.y;
        Eigen::VectorXi indices(2);
        indices << 0, 1;
        ekf_->update(z, indices);

        publishSyncedEkf(msg->header.stamp);
    }

    void publishSyncedEkf(const rclcpp::Time &timestamp)
    {
        Eigen::VectorXd state = ekf_->getState(); 

        nav_msgs::msg::Odometry msg;
        msg.header.stamp = timestamp; 
        msg.header.frame_id = "map";
        
        msg.pose.pose.position.x = state(0);
        msg.pose.pose.position.y = state(1);
        
        tf2::Quaternion q;
        q.setRPY(0, 0, state(2));
        msg.pose.pose.orientation = tf2::toMsg(q);
        
        ekf_synced_pub_->publish(msg);
    }

    void publishEkfState()
    {
        Eigen::VectorXd state = ekf_->getState(); 
        nav_msgs::msg::Odometry msg;
        msg.header.stamp = this->get_clock()->now();
        msg.header.frame_id = "map";
        msg.pose.pose.position.x = state(0);
        msg.pose.pose.position.y = state(1);
        tf2::Quaternion q;
        q.setRPY(0, 0, state(2));
        msg.pose.pose.orientation = tf2::toMsg(q);
        ekf_pub_->publish(msg);
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<EkfNode>());
    rclcpp::shutdown();
    return 0;
}