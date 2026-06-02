#pragma once
#include <Eigen/Dense>
#include <vector>
#include <cmath>

class CoreUKF {
protected:
    int dim_x = 3;  
    int n_sig;      
		double alpha = 1.0;   // Đổi từ 1e-3 thành 1.0
    double beta  = 0.0;   // Đổi từ 2.0 thành 0.0
    double kappa = 0.0;
    double lambda;

    Eigen::VectorXd Wm, Wc;
    Eigen::MatrixXd sigmas_pred;

    double normalizeAngle(double angle) {
        while (angle > M_PI)  angle -= 2.0 * M_PI;
        while (angle < -M_PI) angle += 2.0 * M_PI;
        return angle;
    }

public:
    Eigen::VectorXd x;    
    Eigen::MatrixXd P;    
    Eigen::MatrixXd Q;    

    CoreUKF() {
        n_sig = 2 * dim_x + 1;

        x = Eigen::VectorXd::Zero(dim_x);
        P = Eigen::MatrixXd::Identity(dim_x, dim_x);
        Q = Eigen::MatrixXd::Identity(dim_x, dim_x);

        lambda = alpha * alpha * (dim_x + kappa) - dim_x;

        Wm = Eigen::VectorXd::Constant(n_sig, 0.5 / (dim_x + lambda));
        Wc = Eigen::VectorXd::Constant(n_sig, 0.5 / (dim_x + lambda));

        Wm(0) = lambda / (dim_x + lambda);
        Wc(0) = Wm(0) + (1.0 - alpha * alpha + beta);

        sigmas_pred = Eigen::MatrixXd::Zero(dim_x, n_sig);
    }

    virtual ~CoreUKF() = default;

    virtual Eigen::VectorXd process_model(const Eigen::VectorXd& state, double dt, double v, double w) = 0;

    Eigen::MatrixXd generate_sigma_points() {
        Eigen::MatrixXd sigmas = Eigen::MatrixXd::Zero(dim_x, n_sig);
        sigmas.col(0) = x;

        Eigen::LLT<Eigen::MatrixXd> lltOfP(P);
        if (lltOfP.info() == Eigen::NumericalIssue) {
            Eigen::MatrixXd P_safe = P + Eigen::MatrixXd::Identity(dim_x, dim_x) * 1e-6;
            lltOfP.compute(P_safe);
        }

        Eigen::MatrixXd L = lltOfP.matrixL();
        double gamma = std::sqrt(dim_x + lambda);

        for (int i = 0; i < dim_x; ++i) {
            sigmas.col(i + 1)         = x + gamma * L.col(i);
            sigmas.col(i + 1 + dim_x) = x - gamma * L.col(i);
        }
        return sigmas;
    }

    void predict(double dt, double v, double w) {
        Eigen::MatrixXd sigmas = generate_sigma_points();
        sigmas_pred.setZero();

        for (int i = 0; i < n_sig; ++i) {
            sigmas_pred.col(i) = process_model(sigmas.col(i), dt, v, w);
        }

        x.setZero();
        for (int i = 0; i < n_sig; ++i) {
            x += Wm(i) * sigmas_pred.col(i);
        }
        x(2) = normalizeAngle(x(2));

        P.setZero();
        for (int i = 0; i < n_sig; ++i) {
            Eigen::VectorXd diff = sigmas_pred.col(i) - x;
            diff(2) = normalizeAngle(diff(2));
            P += Wc(i) * diff * diff.transpose();
        }
        P += Q;
    }

    void update_measurement(const Eigen::VectorXd& z, const Eigen::MatrixXd& Z_sigmas, const Eigen::MatrixXd& R_sensor, bool is_angle) {
        int m_dim = z.size();
        Eigen::VectorXd z_pred = Eigen::VectorXd::Zero(m_dim);
        
        for (int i = 0; i < n_sig; ++i) {
            z_pred += Wm(i) * Z_sigmas.col(i);
        }
        if (is_angle) z_pred(0) = normalizeAngle(z_pred(0));

        Eigen::MatrixXd S = Eigen::MatrixXd::Zero(m_dim, m_dim);
        Eigen::MatrixXd Pxz = Eigen::MatrixXd::Zero(dim_x, m_dim);

        for (int i = 0; i < n_sig; ++i) {
            Eigen::VectorXd z_diff = Z_sigmas.col(i) - z_pred;
            if (is_angle) z_diff(0) = normalizeAngle(z_diff(0));

            Eigen::VectorXd x_diff = sigmas_pred.col(i) - x;
            x_diff(2) = normalizeAngle(x_diff(2));

            S += Wc(i) * z_diff * z_diff.transpose();
            Pxz += Wc(i) * x_diff * z_diff.transpose();
        }
        S += R_sensor;

        Eigen::MatrixXd K = Pxz * S.inverse();
        Eigen::VectorXd z_diff = z - z_pred;
        if (is_angle) z_diff(0) = normalizeAngle(z_diff(0));

        x = x + K * z_diff;
        x(2) = normalizeAngle(x(2));
        P = P - K * S * K.transpose();
				P = 0.5 * (P + P.transpose());
    }
};

class DifferentialDriveUKF : public CoreUKF {
public:
    DifferentialDriveUKF() {
        x(0) = 0.0;  
        x(1) = 0.0;  
        x(2) = 0.0;  

        Q.diagonal() << 0.01, 0.01, 0.02;
    }

    Eigen::VectorXd process_model(const Eigen::VectorXd& state, double dt, double v, double w) override {
        Eigen::VectorXd next_state(3);
        double theta = state(2);

        next_state(0) = state(0) + v * dt * std::cos(theta + w * dt / 2.0);
        next_state(1) = state(1) + v * dt * std::sin(theta + w * dt / 2.0);
        next_state(2) = normalizeAngle(state(2) + w * dt);

        return next_state;
    }

    void updateUWB(const Eigen::VectorXd& z) {
        Eigen::MatrixXd Z_sigmas = Eigen::MatrixXd::Zero(2, n_sig);
        Eigen::MatrixXd R_uwb = Eigen::MatrixXd::Identity(2, 2) * 0.1; 

        for (int i = 0; i < n_sig; ++i) {
            Z_sigmas(0, i) = sigmas_pred(0, i);
            Z_sigmas(1, i) = sigmas_pred(1, i);
        }
        update_measurement(z, Z_sigmas, R_uwb, false);
    }

    void updateIMU_Yaw(double theta_imu) {
        Eigen::VectorXd z(1);
        z << theta_imu;
        
        Eigen::MatrixXd Z_sigmas = Eigen::MatrixXd::Zero(1, n_sig);
        Eigen::MatrixXd R_imu = Eigen::MatrixXd::Identity(1, 1) * 0.01;

        for (int i = 0; i < n_sig; ++i) {
            Z_sigmas(0, i) = sigmas_pred(2, i);
        }
        update_measurement(z, Z_sigmas, R_imu, true);
    }
};