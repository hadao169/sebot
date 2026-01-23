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

        if (has_yaw0_ && has_uwbPos0_)
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
            tf2::Vector3 offset(0.0,0.0,0.0);
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