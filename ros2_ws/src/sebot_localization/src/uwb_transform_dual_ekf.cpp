#include <iostream>
#include <memory>
#include <string>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "tf2_ros/transform_broadcaster.h"
#include "tf2_ros/transform_listener.h"
#include "tf2_ros/buffer.h"
#include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
#include "geometry_msgs/msg/pose_stamped.hpp"
#include "sensor_msgs/msg/imu.hpp"
#include "nav_msgs/msg/odometry.hpp"
#include "Eigen/Dense"

using std::placeholders::_1;

class UwbTransformNodeDualEkf : public rclcpp::Node
{
public:
    UwbTransformNodeDualEkf() : Node("uwb_transform_node"), 
                         base_link_frame_id_("base_footprint"),
                         world_frame_id_("map"),
                         transform_timeout_(0.1)
    {

        tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
        tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_);

        uwb_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "/dwm1001/DW878F/pose", 10, std::bind(&UwbTransformNodeDualEkf::uwbCallback, this, _1));

        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu", 10, std::bind(&UwbTransformNodeDualEkf::imuCallback, this, _1));

        ekf_global_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
          "odometry/filtered", 10, std::bind(&UwbTransformNodeDualEkf::ekfGlobalCallback, this, _1));
        
        transform_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/uwb", 10);

        RCLCPP_INFO(this->get_logger(), "Initialized transform node for dual ekf!");

        yaw0 = 0.0;
        pos0_x = 0.0;
        pos0_y = 0.0;
        current_ekf_quat_ = tf2::Quaternion::getIdentity();
        has_yaw0 = false;
        has_uwbPos0 = false;

        sample_count = 50;
        cout_yaw_ = 0;
        uwb_count_ = 0;

        yaw_accu = 0.0;
        pos_accum = Eigen::Vector2d(0.0, 0.0);
    }

private:
    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;

    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr ekf_global_sub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr transform_pub_;
    
    std::string base_link_frame_id_;
    std::string world_frame_id_;
    double transform_timeout_;

    double yaw0;
    double pos0_x;
    double pos0_y;
    tf2::Quaternion current_ekf_quat_;
    bool has_yaw0;
    bool has_uwbPos0;

    size_t sample_count;
    size_t cout_yaw_;
    size_t uwb_count_;

    double yaw_accu;
    Eigen::Vector2d pos_accum;

    double getYawFromImu(const sensor_msgs::msg::Imu & imu_msg)
    {
        tf2::Quaternion q;
        tf2::fromMsg(imu_msg.orientation, q);
        double roll, pitch, yaw;
        tf2::Matrix3x3(q).getRPY(roll, pitch, yaw);
        return yaw;
    }

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        if (has_yaw0) return; 

        yaw_accu += getYawFromImu(*msg);
        cout_yaw_++;
        if (cout_yaw_ >= sample_count)
        {
            yaw0 = yaw_accu / double(sample_count);
            has_yaw0 = true;
            RCLCPP_INFO(this->get_logger(), "Datum Alignment: Initial Map Yaw set to %.3f rad", yaw0);
        }
    }

    void ekfGlobalCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
    {
        tf2::fromMsg(msg->pose.pose.orientation, current_ekf_quat_);
    }

    void uwbCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
    {
        if (!has_uwbPos0) {
            pos_accum(0) += msg->pose.position.x;
            pos_accum(1) += msg->pose.position.y;
            uwb_count_++;

            if (uwb_count_ >= sample_count) {
                pos0_x = pos_accum(0) / double(sample_count);
                pos0_y = pos_accum(1) / double(sample_count);
                has_uwbPos0 = true;
                RCLCPP_INFO(this->get_logger(), "Datum Alignment: Initial UWB Origin set to (%.3f, %.3f)", pos0_x, pos0_y);
            }
            return;
        }

        if (has_yaw0 && has_uwbPos0)
        {
            // transform uwb map to robot map frame
            Eigen::Vector2d sensor_pos_map;
            transformUwbToMap(msg->pose.position.x, msg->pose.position.y, sensor_pos_map(0), sensor_pos_map(1));

            // Remove sensor offset
            Eigen::Vector2d robot_pos_map = removeSensorOffset(sensor_pos_map, msg->header.frame_id);

            auto out_msg = nav_msgs::msg::Odometry();
            out_msg.header.stamp = msg->header.stamp; 
            out_msg.header.frame_id = world_frame_id_; 
            out_msg.child_frame_id = base_link_frame_id_; 
            
            out_msg.pose.pose.position.x = robot_pos_map(0);
            out_msg.pose.pose.position.y = robot_pos_map(1);
            out_msg.pose.pose.position.z = 0.0; 
            out_msg.pose.covariance[0] = 0.1; 
            out_msg.pose.covariance[7] = 0.1; 
            out_msg.pose.covariance[14] = 0.1; 
            
            transform_pub_->publish(out_msg);
        }
    }

    void transformUwbToMap(double uwb_x, double uwb_y, double &map_x, double &map_y)
    {
        // Rotation
        double cos_t = std::cos(yaw0);
        double sin_t = std::sin(yaw0);

        // Translation
        double dx = uwb_x - pos0_x;
        double dy = uwb_y - pos0_y;

        map_x = dx * cos_t - dy * sin_t;
        map_y = dx * sin_t + dy * cos_t;
    }

    Eigen::Vector2d removeSensorOffset(const Eigen::Vector2d &sensor_map_pos, const std::string &sensor_frame_id)
    {
        geometry_msgs::msg::TransformStamped transform_stamped;
        try {
            transform_stamped = tf_buffer_->lookupTransform(
                base_link_frame_id_, 
                sensor_frame_id,    
                tf2::TimePointZero);
        } catch (tf2::TransformException &ex) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 5000, 
                "Could not transform %s to %s: %s", sensor_frame_id.c_str(), base_link_frame_id_.c_str(), ex.what());
            return sensor_map_pos; 
        }

        tf2::Vector3 offset_vec(
            transform_stamped.transform.translation.x,
            transform_stamped.transform.translation.y,
            transform_stamped.transform.translation.z
        );


        tf2::Vector3 offset_rotated = tf2::quatRotate(current_ekf_quat_, offset_vec);

        double rx = sensor_map_pos(0) - offset_rotated.x();
        double ry = sensor_map_pos(1) - offset_rotated.y();

        return Eigen::Vector2d(rx, ry);
    }
};

int main(int argc, char **argv)
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<UwbTransformNodeDualEkf>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}