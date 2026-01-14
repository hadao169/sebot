// #include <iostream>
// #include <memory>
// #include <string>
// #include <vector>
// #include <cmath>

// #include "rclcpp/rclcpp.hpp"
// #include "tf2_ros/transform_broadcaster.h"
// #include "tf2_ros/transform_listener.h"
// #include "tf2_ros/buffer.h"
// #include "tf2_geometry_msgs/tf2_geometry_msgs.hpp"
// #include "geometry_msgs/msg/pose_stamped.hpp"
// #include "sensor_msgs/msg/imu.hpp"
// #include "nav_msgs/msg/odometry.hpp"
// #include "Eigen/Dense"

// using std::placeholders::_1;

// class UwbTransformNode : public rclcpp::Node
// {
// public:
//     UwbTransformNode() : Node("uwb_transform_node"), 
//                          base_link_frame_id_("base_link"),
//                          world_frame_id_("map"),
//                          sensor_frame_id_("uwb_link") 
//     {
//         tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
//         tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_);

//         uwb_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
//             "/dwm1001/DW878F/pose", 10, std::bind(&UwbTransformNode::uwbCallback, this, _1));

//         imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
//             "imu", 10, std::bind(&UwbTransformNode::imuCallback, this, _1));

//         ekf_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
//           "odometry/filtered/global", 10, std::bind(&UwbTransformNode::ekfCallback, this, _1));
        
//         transform_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/uwb", 10);
        
//         RCLCPP_INFO(this->get_logger(), "Initialized transform node for loosely couple!");

//         yaw0 = 0.0;
//         pos0_x = 0.0;
//         pos0_y = 0.0;
//         current_ekf_quat_ = tf2::Quaternion::getIdentity();
        
//         has_yaw0 = false;
//         has_uwbPos0 = false;
//         has_ekf_odom_ = false;

//         sample_count = 50;
//         cout_yaw_ = 0;
//         uwb_count_ = 0;
//         yaw_accu = 0.0;
//         pos_accum = Eigen::Vector2d(0.0, 0.0);
//     }

// private:
//     std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
//     std::unique_ptr<tf2_ros::TransformListener> tf_listener_;

//     rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr uwb_sub_;
//     rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
//     rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr ekf_sub_;
//     rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr transform_pub_;

//     std::string base_link_frame_id_;
//     std::string world_frame_id_;
//     std::string sensor_frame_id_;

//     double yaw0;
//     double pos0_x;
//     double pos0_y;
//     tf2::Quaternion current_ekf_quat_;
    
//     bool has_yaw0;
//     bool has_uwbPos0;
//     bool has_ekf_odom_;

//     size_t sample_count;
//     size_t cout_yaw_;
//     size_t uwb_count_;
//     double yaw_accu;
//     Eigen::Vector2d pos_accum;

//     double getYawFromImu(const sensor_msgs::msg::Imu & imu_msg)
//     {
//         tf2::Quaternion q;
//         tf2::fromMsg(imu_msg.orientation, q);
//         double roll, pitch, yaw;
//         tf2::Matrix3x3(q).getRPY(roll, pitch, yaw);
//         return yaw;
//     }

//     void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
//     {
//         if (has_yaw0) return;

//         yaw_accu += getYawFromImu(*msg);
//         cout_yaw_++;
//         if (cout_yaw_ >= sample_count)
//         {
//             yaw0 = yaw_accu / double(sample_count);
//             has_yaw0 = true;
//             RCLCPP_INFO(this->get_logger(), "Initialized Map Datum Yaw: %.3f rad", yaw0);
//         }
//     }

//     void ekfCallback(const nav_msgs::msg::Odometry::SharedPtr msg)
//     {
//         tf2::fromMsg(msg->pose.pose.orientation, current_ekf_quat_);
//         has_ekf_odom_ = true;
//     }

//     void uwbCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
//     {
//         if (!has_uwbPos0) {
//             pos_accum(0) += msg->pose.position.x;
//             pos_accum(1) += msg->pose.position.y;
//             uwb_count_++;

//             if (uwb_count_ >= sample_count) {
//                 pos0_x = pos_accum(0) / double(sample_count);
//                 pos0_y = pos_accum(1) / double(sample_count);
//                 has_uwbPos0 = true;
//                 RCLCPP_INFO(this->get_logger(), "Initialized UWB Datum Origin: (%.3f, %.3f)", pos0_x, pos0_y);
//             }
//             return;
//         }

//         if (has_yaw0 && has_uwbPos0 && has_ekf_odom_)
//         {
//             Eigen::Vector2d sensor_pos_map;
//             transformUwbToMap(msg->pose.position.x, msg->pose.position.y, sensor_pos_map(0), sensor_pos_map(1));

//             Eigen::Vector2d robot_pos_map = removeSensorOffset(sensor_pos_map);

//             nav_msgs::msg::Odometry out_msg;
//             out_msg.header.stamp = msg->header.stamp;
//             out_msg.header.frame_id = world_frame_id_;
//             out_msg.child_frame_id = base_link_frame_id_;
            
//             out_msg.pose.pose.position.x = robot_pos_map(0);
//             out_msg.pose.pose.position.y = robot_pos_map(1);
//             out_msg.pose.pose.position.z = 0.0;
//             out_msg.pose.pose.orientation.w = 1.0;
//             out_msg.pose.covariance[0] = 0.1;
//             out_msg.pose.covariance[7] = 0.1;
//             out_msg.pose.covariance[14] = 0.1;

//             transform_pub_->publish(out_msg);
//         }
//     }

//     void transformUwbToMap(double uwb_x, double uwb_y, double &map_x, double &map_y)
//     {
//         double cos_t = std::cos(yaw0);
//         double sin_t = std::sin(yaw0);
//         double dx = uwb_x - pos0_x;
//         double dy = uwb_y - pos0_y;

//         map_x = dx * cos_t - dy * sin_t;
//         map_y = dx * sin_t + dy * cos_t;
//     }

//     Eigen::Vector2d removeSensorOffset(const Eigen::Vector2d &sensor_map_pos)
//     {
//         geometry_msgs::msg::TransformStamped transform_stamped;
//         try {
//             transform_stamped = tf_buffer_->lookupTransform(
//                 base_link_frame_id_, 
//                 sensor_frame_id_,
//                 tf2::TimePointZero);
//         } catch (tf2::TransformException &ex) {
//             return sensor_map_pos; 
//         }

//         tf2::Vector3 offset_vec(
//             transform_stamped.transform.translation.x,
//             transform_stamped.transform.translation.y,
//             transform_stamped.transform.translation.z
//         );

//         tf2::Vector3 offset_rotated = tf2::quatRotate(current_ekf_quat_, offset_vec);

//         return Eigen::Vector2d(
//             sensor_map_pos(0) - offset_rotated.x(),
//             sensor_map_pos(1) - offset_rotated.y()
//         );
//     }
// };

// int main(int argc, char **argv)
// {
//     rclcpp::init(argc, argv);
//     auto node = std::make_shared<UwbTransformNode>();
//     rclcpp::spin(node);
//     rclcpp::shutdown();
//     return 0;
// }


#include <deque> // Thư viện cho bộ đệm
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

class UwbTransformNode : public rclcpp::Node
{
public:
    UwbTransformNode() : Node("uwb_transform_node")
    {
        // TF Buffer chỉ để lấy Static Offset (không dùng để tra cứu thời gian)
        tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
        tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_);

        uwb_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "/dwm1001/DW878F/pose", 10, std::bind(&UwbTransformNode::uwbCallback, this, _1));

        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&UwbTransformNode::imuCallback, this, _1));
                
        uwb_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/uwb_data", 10);
        
        yaw0_ = 0.0; pos0_x_ = 0.0; pos0_y_ = 0.0;
        has_yaw0_ = false; has_uwbPos0_ = false;
        sample_count_ = 50; count_yaw_ = 0; count_uwb_ = 0;
        yaw_accum_ = 0.0; pos_accum_ = Eigen::Vector2d(0.0, 0.0);
        RCLCPP_INFO(this->get_logger(), "[UWB TRANSFORM SIMPLE] constructor running");
    }

private:
    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;
    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr uwb_pub_;

    // Bộ đệm lưu lịch sử IMU để nội suy
    std::deque<sensor_msgs::msg::Imu> imu_history_; 
    
    double yaw0_, pos0_x_, pos0_y_;
    bool has_yaw0_, has_uwbPos0_;
    size_t sample_count_, count_yaw_, count_uwb_;
    double yaw_accum_;
    Eigen::Vector2d pos_accum_;

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg)
    {
        // 1. Lưu vào lịch sử (Buffer)
        imu_history_.push_back(*msg);
        // Giữ buffer khoảng 2 giây (giả sử 100Hz -> 200 mẫu) để tiết kiệm Ram
        if (imu_history_.size() > 200) {
            imu_history_.pop_front();
        }

        // 2. Tính toán Yaw0 khởi tạo (chỉ dùng lúc đầu)
        if (!has_yaw0_) {
            double yaw = tf2::getYaw(msg->orientation);
            yaw_accum_ += yaw;
            count_yaw_++;
            if (count_yaw_ >= sample_count_) {
                yaw0_ = yaw_accum_ / double(sample_count_);
                has_yaw0_ = true;
                RCLCPP_INFO(this->get_logger(), "Datum Yaw Initialized: %.3f", yaw0_);
            }
        }
    }

    // Hàm nội suy quan trọng để giải quyết Time Sync
    bool getInterpolatedYaw(const rclcpp::Time& target_time, double& out_yaw)
    {
        if (imu_history_.empty()) return false;

        // Nếu thời điểm cần tìm còn mới hơn cả tin nhắn IMU mới nhất -> Dùng cái mới nhất (chấp nhận trễ nhỏ)
        if (target_time > rclcpp::Time(imu_history_.back().header.stamp)) {
            out_yaw = tf2::getYaw(imu_history_.back().orientation);
            return true;
        }

        // Nếu thời điểm cần tìm cũ hơn tin nhắn IMU cũ nhất -> Không có dữ liệu
        if (target_time < rclcpp::Time(imu_history_.front().header.stamp)) {
            return false;
        }

        // Tìm 2 tin nhắn IMU bao quanh target_time
        for (size_t i = 0; i < imu_history_.size() - 1; ++i) {
            rclcpp::Time t1 = imu_history_[i].header.stamp;
            rclcpp::Time t2 = imu_history_[i+1].header.stamp;

            if (t1 <= target_time && target_time <= t2) {
                // Tìm thấy khoảng bao quanh, bắt đầu nội suy tuyến tính
                double yaw1 = tf2::getYaw(imu_history_[i].orientation);
                double yaw2 = tf2::getYaw(imu_history_[i+1].orientation);
                
                // Xử lý trường hợp góc qua mốc -PI/PI (ví dụ: 3.14 -> -3.14)
                if (yaw2 - yaw1 > M_PI) yaw2 -= 2 * M_PI;
                if (yaw1 - yaw2 > M_PI) yaw1 -= 2 * M_PI;

                double ratio = (target_time - t1).seconds() / (t2 - t1).seconds();
                out_yaw = yaw1 + ratio * (yaw2 - yaw1);
                return true;
            }
        }
        return false;
    }

    void uwbCallback(const geometry_msgs::msg::PoseStamped::SharedPtr msg)
    {
        if (!has_uwbPos0_) {
            pos_accum_(0) += msg->pose.position.x;
            pos_accum_(1) += msg->pose.position.y;
            count_uwb_++;
            if (count_uwb_ >= sample_count_) {
                pos0_x_ = pos_accum_(0) / double(sample_count_);
                pos0_y_ = pos_accum_(1) / double(sample_count_);
                has_uwbPos0_ = true;
                RCLCPP_INFO(this->get_logger(), "Datum UWB Origin Initialized");
            }
            return;
        }

        if (hasy_aw0_ && has_uwbPos0_)
        {
            double current_yaw_at_uwb_time = 0.0;
            rclcpp::Time uwb_time = msg->header.stamp;
            
            if (!getInterpolatedYaw(uwb_time, current_yaw_at_uwb_time)) {
                return; 
            }

            double dx = msg->pose.position.x - pos0_x_;
            double dy = msg->pose.position.y - pos0_y_;
            double cos_t = std::cos(yaw0_);
            double sin_t = std::sin(yaw0_);
            
            double map_x = dx * cos_t - dy * sin_t;
            double map_y = dx * sin_t + dy * cos_t;

            double robot_yaw_map = current_yaw_at_uwb_time - yaw0_;
            
            tf2::Quaternion q_robot;
            q_robot.setRPY(0, 0, robot_yaw_map);

            Eigen::Vector2d robot_pos = removeSensorOffset(Eigen::Vector2d(map_x, map_y), q_robot);

            nav_msgs::msg::Odometry out;
            out.header.stamp = msg->header.stamp; 
            out.header.frame_id = "map";
            out.child_frame_id = "base_footprint";
            
            out.pose.pose.position.x = robot_pos(0);
            out.pose.pose.position.y = robot_pos(1);
            out.pose.pose.orientation = tf2::toMsg(q_robot);

            uwb_pub_->publish(out);
        }
    }

    Eigen::Vector2d removeSensorOffset(const Eigen::Vector2d &raw_pos, const tf2::Quaternion &robot_q)
    {
        try {
            auto t = tf_buffer_->lookupTransform("base_footprint", "uwb_link", tf2::TimePointZero);
            // tf2::Vector3 offset(t.transform.translation.x, t.transform.translation.y, 0.0);
            tf2::Vector3 offset(0.0,0.0, 0.0);
            tf2::Vector3 rotated_offset = tf2::quatRotate(robot_q, offset);
            return Eigen::Vector2d(raw_pos(0) - rotated_offset.x(), raw_pos(1) - rotated_offset.y());
        } catch (...) {
            return raw_pos;
        }
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<UwbTransformNode>());
    rclcpp::shutdown();
    return 0;
}