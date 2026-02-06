#include <deque>
#include <iostream>
#include <memory>
#include <string>
#include <vector>
#include <cmath>
#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_listener.h"
#include "tf2_ros/buffer.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "tf2/utils.h"
#include "Eigen/Dense"

using std::placeholders::_1;

class UwbTransformNode : public rclcpp::Node {
public:
    UwbTransformNode() : Node("uwb_transform_node"), 
                         world_frame_id_("map"),
                         base_link_frame_id_("base_footprint"),
                         sample_threshold_(50) {
        tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
        tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_);

        uwb_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "/dwm1001/DW878F/pose", 10, std::bind(&UwbTransformNode::uwbCallback, this, _1));
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&UwbTransformNode::imuCallback, this, _1));
        transform_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/uwb_data", 10);

        datum_set_ = false;
        uwb_count_ = 0;
        imu_count_ = 0;
        accum_uwb_x_ = 0.0; accum_uwb_y_ = 0.0;
        accum_imu_sin_ = 0.0; accum_imu_cos_ = 0.0;
        
        xy_variance_ = 0.5;
        z_variance_ = 9999.0;
        yaw_variance_ = 9999.0;
    }

private:
    std::deque<sensor_msgs::msg::Imu> imu_history_;

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg) {
        imu_history_.push_back(*msg);
        if (imu_history_.size() > 200) {
            imu_history_.pop_front();
        }

        if (!datum_set_ && imu_count_ < sample_threshold_) {
            double yaw = tf2::getYaw(msg->orientation);
            accum_imu_sin_ += std::sin(yaw);
            accum_imu_cos_ += std::cos(yaw);
            imu_count_++;
        }
    }

    bool getInterpolatedYaw(const rclcpp::Time& target_time, double& out_yaw) {
        if (imu_history_.empty()) return false;

        if (target_time > rclcpp::Time(imu_history_.back().header.stamp)) {
            out_yaw = tf2::getYaw(imu_history_.back().orientation);
            return true;
        }

        if (target_time < rclcpp::Time(imu_history_.front().header.stamp)) {
            return false;
        }

        for (size_t i = 0; i < imu_history_.size() - 1; ++i) {
            rclcpp::Time t1 = imu_history_[i].header.stamp;
            rclcpp::Time t2 = imu_history_[i+1].header.stamp;

            if (t1 <= target_time && target_time <= t2) {
                double yaw1 = tf2::getYaw(imu_history_[i].orientation);
                double yaw2 = tf2::getYaw(imu_history_[i+1].orientation);
                
                if (yaw2 - yaw1 > M_PI) yaw2 -= 2 * M_PI;
                if (yaw1 - yaw2 > M_PI) yaw1 -= 2 * M_PI;

                double ratio = (target_time - t1).seconds() / (t2 - t1).seconds();
                out_yaw = yaw1 + ratio * (yaw2 - yaw1);
                return true;
            }
        }
        return false;
    }

    void uwbCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg) {
        if (!datum_set_) {
            if (uwb_count_ < sample_threshold_) {
                accum_uwb_x_ += msg->pose.position.x;
                accum_uwb_y_ += msg->pose.position.y;
                uwb_count_++;
            }
            if (uwb_count_ >= sample_threshold_ && imu_count_ >= sample_threshold_) {
                pos0_uwb_ << (accum_uwb_x_ / uwb_count_), (accum_uwb_y_ / uwb_count_);
                yaw0_ = std::atan2(accum_imu_sin_ / imu_count_, accum_imu_cos_ / imu_count_);
                datum_set_ = true;
                RCLCPP_INFO(this->get_logger(), "DATUM SET");
            }
            return;
        }

        double interpolated_yaw = 0.0;
        if (!getInterpolatedYaw(msg->header.stamp, interpolated_yaw)) return;

        tf2::Quaternion q_interp;
        q_interp.setRPY(0, 0, interpolated_yaw);

        Eigen::Vector2d pos_sensor_world(msg->pose.position.x, msg->pose.position.y);
        Eigen::Vector2d offset_world = getOffsetInWorldFrame(q_interp);
        Eigen::Vector2d pos_robot_world = pos_sensor_world - offset_world;

        double dx = pos_robot_world.x() - pos0_uwb_.x();
        double dy = pos_robot_world.y() - pos0_uwb_.y();

        double cos_t = std::cos(-yaw0_);
        double sin_t = std::sin(-yaw0_);
        double map_x = dx * cos_t - dy * sin_t;
        double map_y = dx * sin_t + dy * cos_t;

        nav_msgs::msg::Odometry out_msg;
        out_msg.header.stamp = msg->header.stamp;
        out_msg.header.frame_id = world_frame_id_;
        out_msg.child_frame_id = base_link_frame_id_;
        out_msg.pose.pose.position.x = map_x;
        out_msg.pose.pose.position.y = map_y;
        out_msg.pose.pose.orientation.w = 1.0;

        std::fill(out_msg.pose.covariance.begin(), out_msg.pose.covariance.end(), 0.0);
        out_msg.pose.covariance[0] = xy_variance_;
        out_msg.pose.covariance[7] = xy_variance_;
        out_msg.pose.covariance[14] = z_variance_;
        out_msg.pose.covariance[21] = 9999.0;
        out_msg.pose.covariance[28] = 9999.0;
        out_msg.pose.covariance[35] = yaw_variance_;

        transform_pub_->publish(out_msg);
    }

    Eigen::Vector2d getOffsetInWorldFrame(const tf2::Quaternion & robot_q) {
        try {
            auto t = tf_buffer_->lookupTransform(base_link_frame_id_, "uwb_link", tf2::TimePointZero);
            tf2::Vector3 offset_local(t.transform.translation.x, t.transform.translation.y, 0.0);
            tf2::Vector3 offset_world = tf2::quatRotate(robot_q, offset_local);
            return Eigen::Vector2d(offset_world.x(), offset_world.y());
        } catch (...) {
            return Eigen::Vector2d(0.0, 0.0);
        }
    }

    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr transform_pub_;
    std::string world_frame_id_, base_link_frame_id_;
    bool datum_set_;
    size_t uwb_count_, imu_count_, sample_threshold_;
    double accum_uwb_x_, accum_uwb_y_, accum_imu_sin_, accum_imu_cos_, xy_variance_, z_variance_, yaw_variance_, yaw0_;
    Eigen::Vector2d pos0_uwb_;
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<UwbTransformNode>());
    rclcpp::shutdown();
    return 0;
}