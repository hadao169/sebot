#include <iostream>
#include <Eigen/Dense>
#include <cmath>

class ExtendedKalmanFilter {
private:
    Eigen::Vector4d x;       // State vector [x, y, theta, wz]
    Eigen::Matrix4d P;       // State covariance
    Eigen::Matrix4d Fk;      // State transition Jacobian
    Eigen::Matrix4d Qk;      // Process noise covariance
    Eigen::MatrixXd R_config; // Measurement noise covariance
    Eigen::Matrix4d I;       // Identity matrix
    double dt;               // Time step

    /**
     * Yaw angle normalization to [-pi, pi]
     */
    double normalize_angle(double angle) {
        while (angle > M_PI)  angle -= 2.0 * M_PI;
        while (angle < -M_PI) angle += 2.0 * M_PI;
        return angle;
    }
public:
    // Motion model: Unicycle Model with Runge-Kutta 2nd Order
    // x_k = x_k-1 + v_k * dt * math.cos(phi_k-1 + omega_k * dt / 2)
    // y_k = y_k-1 + v_k * dt * math.sin(phi_k-1 + omega_k * dt / 2)
    // wz_k = wz_k-1 (Constant velocity model for angular velocity)
    
    ExtendedKalmanFilter(double x0 = 0, double y0 = 0, double theta0 = 0, double wz0 = 0, double dt = 0.1) {
        // State vector [x, y, theta, wz]
        x << x0, y0, theta0, wz0;
        
        this->dt = dt;

        // Initial state covariance matrix (P0)
        P = Eigen::Matrix4d::Zero();
        P(0, 0) = 1.0;      
        P(1, 1) = 1.0;      
        P(2, 2) = 0.1;    
        P(3, 3) = 0.1;    
        
        // Process noise covariance (Qk)
        Qk = Eigen::Matrix4d::Zero();
        Qk(0, 0) = 0.001;
        Qk(1, 1) = 0.001;
        Qk(2, 2) = 0.001;
        Qk(3, 3) = 0.005;

        // Measurement noise covariance (Rk) - 
        R_config = Eigen::MatrixXd::Zero(4, 4);
        R_config << 0.1, 0,    0,      0,
                    0,    0.1, 0,      0,
                    0,    0,    0.0003, 0,
                    0,    0,    0,      0.01; 

        // Identity matrix
        I = Eigen::Matrix4d::Identity();
    }

    void predict(double v, double omega, double dt_actual) {
        this->dt = dt_actual; // Update dt with the actual time delta from the sensor/timer
        double theta = x(2);

        // State prediction using Runge-Kutta 2nd Order
        x(0) += v * dt * std::cos(theta + omega * dt / 2.0);
        x(1) += v * dt * std::sin(theta + omega * dt / 2.0);
        x(2) += omega * dt;
        x(3) = omega;

        x(2) = normalize_angle(x(2));

        // Jacobian matrix calculation
        // State transition model (Jacobian matrix) 4x4
        Fk = Eigen::Matrix4d::Identity();
        Fk(0, 2) = -v * dt * std::sin(theta + omega * dt / 2.0);
        Fk(1, 2) =  v * dt * std::cos(theta + omega * dt / 2.0);
        Fk(2, 3) = 0; // wz_k follows input omega directly in this model

        // Covariance prediction (Scaling process noise by dt)
        P = Fk * P * Fk.transpose() + (Qk * dt);
    }

    void update(const Eigen::VectorXd& z, const Eigen::VectorXi& measured_indices) {
        int m = measured_indices.size();
        int n = x.size(); // n = 4
        Eigen::MatrixXd H_m = Eigen::MatrixXd::Zero(m, n); // Measurement matrix
        Eigen::MatrixXd R_m = Eigen::MatrixXd::Zero(m, m); // Measurement noise covariance for measured indices
        for (int i = 0; i < m; ++i){
            int idx = measured_indices(i);
            H_m(i, idx) = 1.0;
            R_m(i, i) = R_config(idx, idx);
        }
        // System uncertainty
        Eigen::MatrixXd S = H_m * P * H_m.transpose() + R_m;
        // Kalman gain
        Eigen::MatrixXd K = P * H_m.transpose() * S.inverse();
        // Innovation
        Eigen::VectorXd y = z - H_m * x;
        // Normalize angle in innovation if theta is measured (yaw is only from -pi to pi)
        for(int i = 0; i < m; ++i){
            if (measured_indices(i) == 2){ // If theta is measured
                y(i) = normalize_angle(y(i));
            }
        }
        // State update
        x = x + K * y;
        x(2) = normalize_angle(x(2));
        // Covariance update using the Joseph form: (I - KH)P(I - KH)' + KRK'
        Eigen::MatrixXd gain_residual = I - K * H_m;
        P = gain_residual * P * gain_residual.transpose() + K * R_m * K.transpose();
    }

    Eigen::Vector4d getState() const { return x; }

    double quaternionToYaw(double x, double y, double z, double w) {
        // sin (yaw)
        double siny_cosp = 2 * (w * z + x * y);
        // cos (yaw)
        double cosy_cosp = 1 - 2 * (y * y + z * z);
        return std::atan2(siny_cosp, cosy_cosp); 
    }
};