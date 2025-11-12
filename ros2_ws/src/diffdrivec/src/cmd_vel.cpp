#include "rclcpp/rclcpp.hpp"
#include "geometry_msgs/msg/twist.hpp"
#include "std_msgs/msg/string.hpp"
#include <cmath>
#include <string>

class CmdVelNode : public rclcpp::Node {
public:
    CmdVelNode() : Node("cmd_vel_node") {
        // Lue parametrit
        this->declare_parameter<double>("wheel_radius", 0.1);
        this->declare_parameter<double>("wheel_base", 0.5);

        // Hae parametrien arvot
        wheel_radius_ = this->get_parameter("wheel_radius").as_double();
        wheel_base_ = this->get_parameter("wheel_base").as_double();

        RCLCPP_INFO(this->get_logger(), "Wheel radius: %f", wheel_radius_);
        RCLCPP_INFO(this->get_logger(), "Wheel base: %f", wheel_base_);

        // Luo tilaajat ja julkaisijat
        cmd_vel_subscriber_ = this->create_subscription<geometry_msgs::msg::Twist>(
            "cmd_vel",
            10,
            std::bind(&CmdVelNode::cmdVelCallback, this, std::placeholders::_1)
        );

        mc_publisher_ = this->create_publisher<std_msgs::msg::String>(
            "motor_command",
            10
        );
    }

private:
    void cmdVelCallback(const geometry_msgs::msg::Twist::SharedPtr msg) {
        // Laske vasemman ja oikean pyörän nopeudet
        double vel_l = +((msg->linear.x + (msg->angular.z * wheel_base_ / 2.0)) / wheel_radius_) * 60 / (2 * M_PI);
        double vel_r = -((msg->linear.x - (msg->angular.z * wheel_base_ / 2.0)) / wheel_radius_) * 60 / (2 * M_PI);

        // Luo ja julkaise motor_command-viesti
        auto string_msg = std_msgs::msg::String();
        string_msg.data = "SPD;" + std::to_string(static_cast<int>(vel_l)) + ";" + std::to_string(static_cast<int>(vel_r)) + ";";
        mc_publisher_->publish(string_msg);
    }

    // Parametrit
    double wheel_radius_;
    double wheel_base_;

    // ROS 2 tilaajat ja julkaisijat
    rclcpp::Subscription<geometry_msgs::msg::Twist>::SharedPtr cmd_vel_subscriber_;
    rclcpp::Publisher<std_msgs::msg::String>::SharedPtr mc_publisher_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);

    auto node = std::make_shared<CmdVelNode>();
    rclcpp::spin(node);

    rclcpp::shutdown();
    return 0;
}

