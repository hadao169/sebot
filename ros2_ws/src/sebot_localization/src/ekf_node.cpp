#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/utils.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "ekf.hpp"
#include <tf2_ros/transform_broadcaster.h>
#include <mutex>

using std::placeholders::_1;

class EkfNode : public rclcpp::Node
{
public:
    EkfNode() : Node("ekf_node")
    {
        // Khởi tạo EKF tạm thời với giá trị 0 (sẽ được khởi tạo lại khi có wheel odom)
        ekf_ = std::make_unique<ExtendedKalmanFilter>(0.0, 0.0, 0.0, 0.0);

        ekf_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/filtered", 10);
        tf_broadcaster_ = std::make_unique<tf2_ros::TransformBroadcaster>(*this);

        wheel_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "wheel/odom_transformed", 10, std::bind(&EkfNode::wheelCallback, this, _1));

        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&EkfNode::imuCallback, this, _1));

        uwb_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "uwb/fix", 10, std::bind(&EkfNode::uwbCallback, this, _1));

        timer_ = this->create_wall_timer(
            std::chrono::milliseconds(20), std::bind(&EkfNode::timerCallback, this));

        current_v_ = 0.0;
        initialized_ = false;
        wheel_x_ = wheel_y_ = wheel_yaw_ = 0.0;
    }

private:
    std::unique_ptr<ExtendedKalmanFilter> ekf_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr ekf_pub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr wheel_sub_, uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::TimerBase::SharedPtr timer_;
    std::unique_ptr<tf2_ros::TransformBroadcaster> tf_broadcaster_;

    rclcpp::Time last_predict_time_;
    double current_v_;
    bool initialized_;
    double wheel_x_, wheel_y_, wheel_yaw_;

    std::mutex ekf_mutex_;

    void predictStep(const rclcpp::Time & now)
    {
        if (!initialized_) return;

        double dt = (now - last_predict_time_).seconds();
        if (dt > 0.0) {
            if (dt > 0.2) dt = 0.02;
            ekf_->predict(current_v_, dt);
            last_predict_time_ = now;
        }
    }

    void wheelCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(ekf_mutex_);

        // Lưu pose wheel trong frame odom
        wheel_x_ = msg->pose.pose.position.x;
        wheel_y_ = msg->pose.pose.position.y;
        wheel_yaw_ = tf2::getYaw(msg->pose.pose.orientation);
        current_v_ = msg->twist.twist.linear.x;

        if (!initialized_) {
            // Khởi tạo lại EKF với trạng thái ban đầu lấy từ wheel odometry
            ekf_ = std::make_unique<ExtendedKalmanFilter>(wheel_x_, wheel_y_, wheel_yaw_, 0.0);
            last_predict_time_ = msg->header.stamp;
            initialized_ = true;
            RCLCPP_INFO(this->get_logger(), "EKF initialized from wheel odom");        
        }

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
        if (!initialized_) return;

        std::lock_guard<std::mutex> lock(ekf_mutex_);

        Eigen::VectorXd state = ekf_->getState();
        Eigen::MatrixXd P = ekf_->getP();

        if (std::isnan(state(0)) || std::isnan(state(1)) || std::isnan(state(2))) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 1000,
                                 "EKF state contains NaN, skipping publish.");
            return;
        }

        rclcpp::Time now = this->now();

        // --- Publish odometry filtered (map -> base_link) ---
        nav_msgs::msg::Odometry out_msg;
        out_msg.header.stamp = now;
        out_msg.header.frame_id = "map";
        out_msg.child_frame_id = "base_link";

        out_msg.pose.pose.position.x = state(0);
        out_msg.pose.pose.position.y = state(1);
        out_msg.pose.pose.position.z = 0.0;

        tf2::Quaternion q;
        q.setRPY(0, 0, state(2));
        out_msg.pose.pose.orientation = tf2::toMsg(q);

        out_msg.pose.covariance.fill(0.0);
        out_msg.pose.covariance[0]  = P(0,0);
        out_msg.pose.covariance[7]  = P(1,1);
        out_msg.pose.covariance[35] = P(2,2);

        out_msg.twist.twist.linear.x = current_v_;

        ekf_pub_->publish(out_msg);

        // --- Publish TF map -> odom ---
        double map_x = state(0);
        double map_y = state(1);
        double map_yaw = state(2);

        double cos_w = cos(wheel_yaw_);
        double sin_w = sin(wheel_yaw_);
        double t_base_odom_x = -cos_w * wheel_x_ - sin_w * wheel_y_;
        double t_base_odom_y =  sin_w * wheel_x_ - cos_w * wheel_y_;
        double r_base_odom = -wheel_yaw_;

        double cos_m = cos(map_yaw);
        double sin_m = sin(map_yaw);
        double map_odom_x = map_x + cos_m * t_base_odom_x - sin_m * t_base_odom_y;
        double map_odom_y = map_y + sin_m * t_base_odom_x + cos_m * t_base_odom_y;
        double map_odom_yaw = map_yaw + r_base_odom;

        geometry_msgs::msg::TransformStamped tf_msg;
        tf_msg.header.stamp = now;
        tf_msg.header.frame_id = "map";
        tf_msg.child_frame_id = "odom";
        tf_msg.transform.translation.x = map_odom_x;
        tf_msg.transform.translation.y = map_odom_y;
        tf_msg.transform.translation.z = 0.0;

        tf2::Quaternion q_odom;
        q_odom.setRPY(0, 0, map_odom_yaw);
        tf_msg.transform.rotation = tf2::toMsg(q_odom);

        tf_broadcaster_->sendTransform(tf_msg);
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<EkfNode>());
    rclcpp::shutdown();
    return 0;
}