// #include "rclcpp/rclcpp.hpp"
// #include "sensor_msgs/msg/imu.hpp"
// #include "nav_msgs/msg/odometry.hpp"
// #include "tf2/utils.h"
// #include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
// #include "tf2_ros/transform_broadcaster.h"
// #include "geometry_msgs/msg/transform_stamped.hpp"
// #include "geometry_msgs/msg/pose_stamped.hpp"
// #include <memory>
// #include "ekf.hpp"

// using std::placeholders::_1;

// class EkfNode : public rclcpp::Node
// {
// public:
//     EkfNode() : Node("ekf_node")
//     {
//         ekf_ = std::make_unique<ExtendedKalmanFilter>(0.0, 0.0, 0.0, 0.0, 0.1);

//         odom_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("ekf_odom", 10);
//         ekf_pose_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/filtered/global", 10);

//         wheel_odom_sub = this->create_subscription<nav_msgs::msg::Odometry>(
//             "wheel/odom", 10, std::bind(&EkfNode::wheel_odom_callback, this, _1));

//         imu_sub = this->create_subscription<sensor_msgs::msg::Imu>(
//             "imu/data", 10, std::bind(&EkfNode::imu_callback, this, _1));

//         transform_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
//             "odometry/uwb", 10, std::bind(&EkfNode::transformCallback, this, _1));

//         tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

//         timer_ = this->create_wall_timer(
//             std::chrono::milliseconds(100), std::bind(&EkfNode::publish_odom, this));
//     }

// private:
//     std::unique_ptr<ExtendedKalmanFilter> ekf_;
//     std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;
//     rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr odom_pub_;
//     rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ekf_pose_pub_;
//     rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr wheel_odom_sub;
//     rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub;
//     rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr uwb_sub;
//     rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr transform_sub_;
//     rclcpp::TimerBase::SharedPtr timer_;

//     void wheel_odom_callback(const nav_msgs::msg::Odometry::SharedPtr msg)
//     {
//         ekf_->predict(msg->twist.twist.linear.x, msg->twist.twist.angular.z);
//     }

//     void imu_callback(const sensor_msgs::msg::Imu::SharedPtr msg)
//     {
//         double yaw = ekf_->quaternionToYaw(msg->orientation.x, msg->orientation.y, 
//                                            msg->orientation.z, msg->orientation.w);
//         double wz = msg->angular_velocity.z;

//         Eigen::VectorXd z_imu(2);
//         z_imu << yaw, wz;
//         Eigen::VectorXi indices(2);
//         indices << 2, 3;
//         ekf_->update(z_imu, indices);
//     }

//     void transformCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
//     {
//         Eigen::VectorXd z_uwb(2);
//         z_uwb << msg->pose.pose.position.x, msg->pose.pose.position.y;
//         Eigen::VectorXi indices(2);
//         indices << 0, 1;
//         ekf_->update(z_uwb, indices);

//         auto state = ekf_->getState();
//         nav_msgs::msg::Odometry ekf_odom;
//         ekf_odom.header.stamp = msg->header.stamp;
//         ekf_odom.header.frame_id = "map";
//         ekf_odom.child_frame_id = "base_link"; 
        
//         ekf_odom.pose.pose.position.x = state(0);
//         ekf_odom.pose.pose.position.y = state(1);
        
//         tf2::Quaternion q;
//         q.setRPY(0, 0, state(2));
//         ekf_odom.pose.pose.orientation = tf2::toMsg(q);
//         ekf_odom.pose.covariance = msg->pose.covariance;
        
//         ekf_pose_pub_->publish(ekf_odom);
//     }

//     void publish_odom()
//     {
//         auto state = ekf_->getState();
//         auto now = this->get_clock()->now();

//         tf2::Quaternion q;
//         q.setRPY(0, 0, state(2));
//         geometry_msgs::msg::Quaternion q_msg = tf2::toMsg(q);

//         nav_msgs::msg::Odometry odom_msg;
//         odom_msg.header.stamp = now;
//         odom_msg.header.frame_id = "map";
//         odom_msg.child_frame_id = "odom"; 
//         odom_msg.pose.pose.position.x = state(0);
//         odom_msg.pose.pose.position.y = state(1);
//         odom_msg.pose.pose.orientation = q_msg;
//         odom_pub_->publish(odom_msg);

//         geometry_msgs::msg::TransformStamped t;
//         t.header.stamp = now;
//         t.header.frame_id = "map";
//         t.child_frame_id = "odom";
//         t.transform.translation.x = state(0);
//         t.transform.translation.y = state(1);
//         t.transform.translation.z = 0.0;
//         t.transform.rotation = q_msg;

//         tf_broadcaster_->sendTransform(t);
//     }
// };

// int main(int argc, char **argv)
// {
//     rclcpp::init(argc, argv);
//     auto node = std::make_shared<EkfNode>();
//     rclcpp::spin(node);
//     rclcpp::shutdown();
//     return 0;
// }



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