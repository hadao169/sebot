#include <iostream>
#include <Eigen/Dense>
#include <cmath>

class ExtendedKalmanFilter {
private:
    Eigen::Vector4d x;       
    Eigen::Matrix4d P;       
    Eigen::Matrix4d Fk;      
    Eigen::Matrix4d Qk;      
    Eigen::MatrixXd R_config; 
    Eigen::Matrix4d I;       

    double normalize_angle(double angle) {
        while (angle > M_PI)  angle -= 2.0 * M_PI;
        while (angle < -M_PI) angle += 2.0 * M_PI;
        return angle;
    }
public:
    ExtendedKalmanFilter(double x0 = 0, double y0 = 0, double theta0 = 0, double wz0 = 0) {
        x << x0, y0, theta0, wz0;
        
        //State Error Covariance
        P = Eigen::Matrix4d::Zero();
        P(0, 0) = 1.0;      
        P(1, 1) = 1.0;      
        P(2, 2) = 0.01;    
        P(3, 3) = 0.01;    
        
        // Process noise covariance
        Qk = Eigen::Matrix4d::Zero();
        Qk << 0.0001, 0,      0,      0,
              0,      0.0001, 0,      0,
              0,      0,      0.0001, 0,
              0,      0,      0,      0.005;  

        // Measurement noise covariance
        R_config = Eigen::MatrixXd::Zero(4, 4);
        R_config << 0.5, 0,    0,      0,
                    0,    0.5, 0,      0,
                    0,    0,    0.0003, 0,
                    0,    0,    0,      0.01; 

        I = Eigen::Matrix4d::Identity();
    }

    void predict(double v, double dt) {
        double theta = x(2);
        double wz_current = x(3);

        x(0) += v * dt * std::cos(theta + wz_current * dt / 2.0);
        x(1) += v * dt * std::sin(theta + wz_current * dt / 2.0);
        x(2) += wz_current * dt;
        x(2) = normalize_angle(x(2));

        Fk = Eigen::Matrix4d::Identity();
        Fk(0, 2) = -v * dt * std::sin(theta + wz_current * dt / 2.0);
        Fk(0, 3) = -v * dt * std::sin(theta + wz_current * dt / 2.0) * (dt / 2.0);
        Fk(1, 2) =  v * dt * std::cos(theta + wz_current * dt / 2.0);
        Fk(1, 3) =  v * dt * std::cos(theta + wz_current * dt / 2.0) * (dt / 2.0);
        Fk(2, 3) = dt;

        P = Fk * P * Fk.transpose() + Qk;   
    }

    void update(const Eigen::VectorXd& z, const Eigen::VectorXi& measured_indices) {
        int m = measured_indices.size();
        int n = x.size(); 
        Eigen::MatrixXd H_m = Eigen::MatrixXd::Zero(m, n); 
        Eigen::MatrixXd R_m = Eigen::MatrixXd::Zero(m, m); 
        for (int i = 0; i < m; ++i){
            int idx = measured_indices(i);
            H_m(i, idx) = 1.0;
            R_m(i, i) = R_config(idx, idx);
        }
        
        Eigen::MatrixXd S = H_m * P * H_m.transpose() + R_m;
        Eigen::MatrixXd K = P * H_m.transpose() * S.inverse();
        Eigen::VectorXd y = z - H_m * x;
        
        for(int i = 0; i < m; ++i){
            if (measured_indices(i) == 2){ 
                y(i) = normalize_angle(y(i));
            }
        }
        
        x = x + K * y;
        x(2) = normalize_angle(x(2));
        
        Eigen::MatrixXd gain_residual = I - K * H_m;
        P = gain_residual * P * gain_residual.transpose() + K * R_m * K.transpose();
    }

    Eigen::Vector4d getState() const { return x; }
    
    Eigen::Matrix4d getP() const { return P; }

    double quaternionToYaw(double x, double y, double z, double w) {
        double siny_cosp = 2 * (w * z + x * y);
        double cosy_cosp = 1 - 2 * (y * y + z * z);
        return std::atan2(siny_cosp, cosy_cosp); 
    }
};