import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class ExtendedKalmanFilter:
    def __init__(self, x0=0.0, y0=0.0, theta0=0.0, dt=0.1):
        # State: [x, y, theta]
        self.x = np.array([x0, y0, theta0], dtype=float)
        self.dt = dt
        
        # Ma trận hiệp phương sai P (Initial confidence)
        self.P = np.eye(3) * 0.1
        
        # Process noise Q (Độ tin cậy vào mô hình vật lý)
        self.Q = np.diag([0.05, 0.05, 0.06])
        
        # Measurement noise R (Độ tin cậy vào cảm biến - sẽ được trích xuất sub-matrix)
        self.R_global = np.diag([25, 25, 0.1]) # x, y, theta

    def normalize_angle(self, angle):
        return (angle + np.pi) % (2 * np.pi) - np.pi

    def predict(self, v, omega):
        theta = self.x[2]
        dt = self.dt

        # 1. State prediction (Runge-Kutta 2nd order)
        self.x[0] += v * dt * np.cos(theta + omega * dt / 2.0)
        self.x[1] += v * dt * np.sin(theta + omega * dt / 2.0)
        self.x[2] += omega * dt
        self.x[2] = self.normalize_angle(self.x[2])

        # 2. Jacobian Fk
        Fk = np.array([
            [1, 0, -v * dt * np.sin(theta + omega * dt / 2.0)],
            [0, 1,  v * dt * np.cos(theta + omega * dt / 2.0)],
            [0, 0, 1]
        ])

        # 3. Covariance prediction
        self.P = Fk @ self.P @ Fk.T + self.Q

    def update(self, z_raw, measured_indices):
        """
        z_raw: mảng dữ liệu (ví dụ [x, y] từ UWB)
        measured_indices: list các chỉ số đo (ví dụ [0, 1])
        """
        z = np.array(z_raw)
        m = len(measured_indices)
        n = 3

        # Tạo H và R con
        H = np.zeros((m, n))
        R = np.zeros((m, m))
        for i, idx in enumerate(measured_indices):
            H[i, idx] = 1.0
            R[i, i] = self.R_global[idx, idx]

        # Innovation
        y = z - H @ self.x
        for i, idx in enumerate(measured_indices):
            if idx == 2: # Nếu đo yaw
                y[i] = self.normalize_angle(y[i])

        # Kalman Gain
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)

        # Update
        self.x = self.x + K @ y
        self.x[2] = self.normalize_angle(self.x[2])
        self.P = (np.eye(n) - K @ H) @ self.P

# --- TẠO DATASET ---
def generate_data(dt=0.1, duration=50):
    t = np.arange(0, duration, dt)
    a = 0.2
    true_x = 10 * np.sin(a * t)
    true_y = 5 * np.sin(2 * a * t)
    
    dx = np.gradient(true_x, dt)
    dy = np.gradient(true_y, dt)
    true_theta = np.arctan2(dy, dx)
    
    v = np.sqrt(dx**2 + dy**2)
    omega = np.gradient(true_theta, dt)
    
    # UWB đo x, y với nhiễu 0.5m
    noisy_x = true_x + np.random.normal(0, 0.5, len(t))
    noisy_y = true_y + np.random.normal(0, 0.5, len(t))
    
    return t, v, omega, true_x, true_y, true_theta, noisy_x, noisy_y

# --- CHẠY TEST ---
t, v_in, w_in, tx, ty, tth, nx, ny = generate_data()
ekf = ExtendedKalmanFilter(x0=tx[0], y0=ty[0], theta0=tth[0], dt=0.1)

est_path = []
for i in range(len(t)):
    ekf.predict(v_in[i], w_in[i])
    # Giả sử chỉ có UWB đo x, y
    ekf.update([nx[i], ny[i]], [0, 1])
    est_path.append(ekf.x.copy())

est_path = np.array(est_path)

# --- TÍNH TOÁN RMSE ---
rmse_pos = np.sqrt(np.mean((est_path[:,0] - tx)**2 + (est_path[:,1] - ty)**2))
print(f"RMSE Position: {rmse_pos:.4f} m")

# --- VẼ ĐỒ THỊ ---

plt.figure(figsize=(12, 6))
plt.plot(tx, ty, 'g', label='Ground Truth', linewidth=2)
plt.scatter(nx, ny, c='r', s=1, alpha=0.3, label='UWB Noisy')
plt.plot(est_path[:,0], est_path[:,1], 'b--', label='EKF Estimated')
plt.legend()
plt.title("EKF Performance Test (Eight Curve)")
plt.axis('equal')

# Vẽ sai số Theta (Góc hướng)
plt.figure(figsize=(12, 4))
error_theta = (est_path[:,2] - tth + np.pi) % (2*np.pi) - np.pi
plt.plot(t, np.degrees(error_theta))
plt.ylabel("Yaw Error (degrees)")
plt.xlabel("Time (s)")
plt.title("EKF Heading Estimation Accuracy (UWB only)")
plt.show()