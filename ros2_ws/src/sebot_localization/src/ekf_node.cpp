#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/utils.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include "geometry_msgs/msg/transform_stamped.hpp"
#include <memory>
#include "ekf.hpp"

using std::placeholders::_1;

class EkfNode : public rclcpp::Node
{
public:
    EkfNode() : Node("ekf_node")
    {
        // Khởi tạo EKF: x, y, theta, wz, dt
        ekf_ = std::make_unique<ExtendedKalmanFilter>(0.0, 0.0, 0.0, 0.0, 0.1);

        odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("ekf_odom", 10);

        wheel_odom_sub = this->create_subscription<nav_msgs::msg::Odometry>(
            "wheel/odom", 10, std::bind(&EkfNode::wheel_odom_callback, this, _1));

        imu_sub = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&EkfNode::imu_callback, this, _1));

        uwb_sub = this->create_subscription<nav_msgs::msg::Odometry>(
            "uwb_odom", 10, std::bind(&EkfNode::uwb_callback, this, _1));

        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(100), std::bind(&EkfNode::publish_odom, this));
    }

private:
    std::unique_ptr<ExtendedKalmanFilter> ekf_;
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr wheel_odom_sub;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr uwb_sub;
    rclcpp::TimerBase::SharedPtr timer_;

    void wheel_odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        ekf_->predict(msg->twist.twist.linear.x, msg->twist.twist.angular.z);
    }

    void imu_callback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        double yaw = ekf_->quaternionToYaw(msg->orientation.x, msg->orientation.y, 
                                           msg->orientation.z, msg->orientation.w);
        double wz = msg->angular_velocity.z;

        Eigen::VectorXd z_imu(2);
        z_imu << yaw, wz;

        Eigen::VectorXi indices(2);
        indices << 2, 3; // Cập nhật theta và wz
        ekf_->update(z_imu, indices);
    }

    void uwb_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        Eigen::VectorXd z_uwb(2);
        z_uwb << msg->pose.pose.position.x, msg->pose.pose.position.y;

        Eigen::VectorXi indices(2);
        indices << 0, 1; // Cập nhật x và y
        ekf_->update(z_uwb, indices);
    }

    void publish_odom()
    {
        auto state = ekf_->getState();
        auto now = this->get_clock()->now();

        // Chuẩn bị Quaternion chung
        tf2::Quaternion q;
        q.setRPY(0, 0, state(2));
        geometry_msgs::msg::Quaternion q_msg = tf2::toMsg(q);

        // 1. Publish Odometry Message
        nav_msgs::msg::Odometry odom_msg;
        odom_msg.header.stamp = now;
        odom_msg.header.frame_id = "odom";
        odom_msg.child_frame_id = "base_footprint";
        odom_msg.pose.pose.position.x = state(0);
        odom_msg.pose.pose.position.y = state(1);
        odom_msg.pose.pose.orientation = q_msg;
        odom_pub_->publish(odom_msg);

        // 2. Broadcast TF Transform
        geometry_msgs::msg::TransformStamped t;
        t.header.stamp = now;
        t.header.frame_id = "odom";
        t.child_frame_id = "base_footprint";
        t.transform.translation.x = state(0);
        t.transform.translation.y = state(1);
        t.transform.translation.z = 0.0;
        t.transform.rotation.x = q.x();
        t.transform.rotation.y = q.y();
        t.transform.rotation.z = q.z();
        t.transform.rotation.w = q.w();

        tf_broadcaster_->sendTransform(t);
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<EkfNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}