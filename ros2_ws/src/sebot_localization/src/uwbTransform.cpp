#include <deque>
#include <memory>
#include <string>
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
                         base_link_frame_id_("base_link"),
                         sample_threshold_(50) {

        this->declare_parameter("sample_threshold", 50);
        this->declare_parameter("xy_variance", 0.01);
        this->declare_parameter("z_variance", 1e9);
        this->declare_parameter("orientation_variance", 1e9);
        this->declare_parameter("world_frame_id", "map");
        this->declare_parameter("base_link_frame_id", "base_link");
        this->declare_parameter("uwb_link_frame_id", "uwb_link");

        sample_threshold_ = this->get_parameter("sample_threshold").as_int();
        xy_variance_ = this->get_parameter("xy_variance").as_double();
        z_variance_ = this->get_parameter("z_variance").as_double();
        orientation_variance_ = this->get_parameter("orientation_variance").as_double();
        world_frame_id_ = this->get_parameter("world_frame_id").as_string();
        base_link_frame_id_ = this->get_parameter("base_link_frame_id").as_string();
        uwb_link_frame_id_ = this->get_parameter("uwb_link_frame_id").as_string();

        tf_buffer_ = std::make_unique<tf2_ros::Buffer>(this->get_clock());
        tf_listener_ = std::make_unique<tf2_ros::TransformListener>(*tf_buffer_);

        uwb_sub_ = this->create_subscription<geometry_msgs::msg::PoseStamped>(
            "dwm1001/id_DW878F/pose", 10, std::bind(&UwbTransformNode::uwbCallback, this, _1));
        imu_sub_ = this->create_subscription<sensor_msgs::msg::Imu>(
            "imu/data", 10, std::bind(&UwbTransformNode::imuCallback, this, _1));
        odom_sub_ = this->create_subscription<nav_msgs::msg::Odometry>(
            "odometry/global", 10, std::bind(&UwbTransformNode::odomCallback, this, _1));

        transform_pub_ = this->create_publisher<nav_msgs::msg::Odometry>("odometry/uwb_data", 10);

        // Initialize datum; counters and accumulators for setting datum
        datum_set_ = false;
        uwb_count_ = 0;
        imu_count_ = 0;
        odom_received_ = false;
        accum_uwb_x_ = 0.0; accum_uwb_y_ = 0.0;
        accum_imu_sin_ = 0.0; accum_imu_cos_ = 0.0;
    }

private:
    const size_t IMU_HISTORY_SIZE = 200;
    // Parameters
    size_t sample_threshold_;
    double xy_variance_;
    double z_variance_;
    double orientation_variance_;
    std::string world_frame_id_;
    std::string base_link_frame_id_;
    std::string uwb_link_frame_id_;

    std::unique_ptr<tf2_ros::Buffer> tf_buffer_;
    std::unique_ptr<tf2_ros::TransformListener> tf_listener_;

    rclcpp::Subscription<geometry_msgs::msg::PoseStamped>::SharedPtr uwb_sub_;
    rclcpp::Subscription<sensor_msgs::msg::Imu>::SharedPtr imu_sub_;
    rclcpp::Subscription<nav_msgs::msg::Odometry>::SharedPtr odom_sub_;
    rclcpp::Publisher<nav_msgs::msg::Odometry>::SharedPtr transform_pub_;

    bool datum_set_;
    size_t uwb_count_, imu_count_;
    bool odom_received_;
    nav_msgs::msg::Odometry::SharedPtr latest_odom_;
    std::deque<sensor_msgs::msg::Imu> imu_history_;

    double accum_uwb_x_, accum_uwb_y_;
    double accum_imu_sin_, accum_imu_cos_;
    double yaw0_, cos_yaw0_, sin_yaw0_;
    Eigen::Vector2d pos0_uwb_;
    Eigen::Vector2d pos0_map_;

    void odomCallback(const nav_msgs::msg::Odometry::SharedPtr msg) {
        latest_odom_ = msg;
        odom_received_ = true;
    }

    void imuCallback(const sensor_msgs::msg::Imu::SharedPtr msg) {
        imu_history_.push_back(*msg);
        if (imu_history_.size() > IMU_HISTORY_SIZE) {
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
            // Wait for enough samples (more stable than just using one message)
            if (uwb_count_ >= sample_threshold_ && imu_count_ >= sample_threshold_ && odom_received_) {
                pos0_uwb_ << (accum_uwb_x_ / uwb_count_), (accum_uwb_y_ / uwb_count_);
                yaw0_ = std::atan2(accum_imu_sin_ / imu_count_, accum_imu_cos_ / imu_count_);
                // Robot's position in map frame at t0 (from ekf global)
                pos0_map_ << latest_odom_->pose.pose.position.x, latest_odom_->pose.pose.position.y;
                
                cos_yaw0_ = std::cos(-yaw0_);
                sin_yaw0_ = std::sin(-yaw0_);
                
                datum_set_ = true;
                RCLCPP_INFO(this->get_logger(), 
                    "Datum set: map origin at (%.3f, %.3f), yaw0 = %.3f",
                    pos0_map_.x(), pos0_map_.y(), yaw0_);
            }
            return;
        }

        double interpolated_yaw = 0.0;
        if (!getInterpolatedYaw(msg->header.stamp, interpolated_yaw)) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 5000,
                "Cannot interpolate IMU yaw for UWB message at time %.3f", 
                msg->header.stamp.sec + msg->header.stamp.nanosec * 1e-9);
            return;
        }

        // Offset between base_link and uwb_link (define in the URDF or static transform node)
        tf2::Quaternion q_robot;
        q_robot.setRPY(0, 0, interpolated_yaw);
        Eigen::Vector2d offset_world = getOffsetInWorldFrame(q_robot);
        Eigen::Vector2d pos_sensor_uwb(msg->pose.position.x, msg->pose.position.y);
        Eigen::Vector2d pos_robot_uwb = pos_sensor_uwb - offset_world; // Transform sensor reading to robot's center in UWB frame

        // Transform from UWB frame (4 anchors) to map frame
        double dx = pos_robot_uwb.x() - pos0_uwb_.x();
        double dy = pos_robot_uwb.y() - pos0_uwb_.y();
        double map_x = cos_yaw0_ * dx - sin_yaw0_ * dy + pos0_map_.x();
        double map_y = sin_yaw0_ * dx + cos_yaw0_ * dy + pos0_map_.y();

        nav_msgs::msg::Odometry out_msg;
        out_msg.header.stamp = msg->header.stamp;
        out_msg.header.frame_id = world_frame_id_;
        out_msg.child_frame_id = base_link_frame_id_;
        
        out_msg.pose.pose.position.x = map_x;
        out_msg.pose.pose.position.y = map_y;
        out_msg.pose.pose.position.z = 0.0;
        out_msg.pose.pose.orientation.w = 1.0;  // identity since UWB doesn't provide orientation

        // Covariance matrix (6x6)
        std::fill(out_msg.pose.covariance.begin(), out_msg.pose.covariance.end(), 0.0);
        out_msg.pose.covariance[0] = xy_variance_;   
        out_msg.pose.covariance[7] = xy_variance_;   
        out_msg.pose.covariance[14] = z_variance_;   
        out_msg.pose.covariance[21] = orientation_variance_; // roll
        out_msg.pose.covariance[28] = orientation_variance_; // pitch
        out_msg.pose.covariance[35] = orientation_variance_; // yaw

        transform_pub_->publish(out_msg);
    }

    Eigen::Vector2d getOffsetInWorldFrame(const tf2::Quaternion & robot_q) {
        try {
            geometry_msgs::msg::TransformStamped t;
            t = tf_buffer_->lookupTransform(base_link_frame_id_, uwb_link_frame_id_, tf2::TimePointZero);
            RCLCPP_INFO_ONCE(this->get_logger(), 
                "Received static transform %s -> %s: translation (%.3f, %.3f, %.3f)",
                base_link_frame_id_.c_str(), uwb_link_frame_id_.c_str(),
                t.transform.translation.x, t.transform.translation.y, t.transform.translation.z);
            
            tf2::Vector3 offset_local(t.transform.translation.x, t.transform.translation.y, 0.0);
            tf2::Vector3 offset_world = tf2::quatRotate(robot_q, offset_local);
            return Eigen::Vector2d(offset_world.x(), offset_world.y());
        } catch (const tf2::TransformException & ex) {
            RCLCPP_WARN_THROTTLE(this->get_logger(), *this->get_clock(), 5000,
                "Cannot get transform %s -> %s: %s",
                base_link_frame_id_.c_str(), uwb_link_frame_id_.c_str(), ex.what());
            return Eigen::Vector2d(0.0, 0.0);
        }
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<UwbTransformNode>());
    rclcpp::shutdown();
    return 0;
}