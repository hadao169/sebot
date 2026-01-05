import numpy as np
from config import initial_estimate_covariance as P0, process_noise_covariance as Qk, measurement_noise_covariance as Rk	

class ExtendedKalmanFilter:
  # Motion model: Unicycle Model with Runge-Kutta 2nd Order
  # x_k = x_k-1 + v_k * dt * math.cos(phi_k-1 + omega_k * dt / 2)
  # y_k = y_k-1 + v_k * dt * math.sin(phi_k-1 + omega_k * dt / 2)
  
	def __init__(self, x0=0.0, y0=0.0, theta0=0.0, dt:float=0.1):
		# State vector [x, y, theta]
		self.x = np.array([x0, y0, theta0], dtype=float).T
		self.Fk = None	# State transition model (Jacobian matrix)
		self.Qk = Qk  # Process noise covariance 
		self.R = Rk     # Measurement noise covariance
		self.H = np.array([[1, 0, 0], [0, 1, 0]])  # Measurement matrix 
		self.I = np.eye(3)	# Identity matrix
		self.P = np.array(P0)  # Initial state covariance matrix
		self.dt = dt                 # Time step

	def predict(self, v:float, omega:float):
		theta = self.x[2]
		dt = self.dt

		# State prediction using Runge-Kutta 2nd Order
		self.x[0] += v * dt * np.cos(theta + omega * dt / 2)
		self.x[1] += v * dt * np.sin(theta + omega * dt / 2)
		self.x[2] += omega * dt

		# Jacobian matrix calculation
		self.Fk = np.array([
			[1, 0, -v * dt * np.sin(theta + omega * dt / 2)],
			[0, 1,  v * dt * np.cos(theta + omega * dt / 2)],
			[0, 0, 1]
		])

		# Covariance prediction
		self.P = self.Fk @ self.P @ self.Fk.T + self.Qk 

	def update(self, z:np.ndarray):
    # System uncertainty
		S = self.H @ self.P @ self.H.T + self.R 
		# Kalman gain
		K = self.P @ self.H.T @ np.linalg.inv(S)
    # Innovation
		y = z - self.H @ self.x
		# y[2] = self.normalize_angle(y[2])
		# State update
		self.x = self.x + K @ y
		self.x[2] = self.normalize_angle(self.x[2])
		# Covariance update
		self.P = (self.I - K @ self.H) @ self.P @ (self.I - K @ self.H).T + K @ self.R @ K.T

	def normalize_angle(self, angle):
		"""Yaw angle normalization to [-pi, pi]"""
		return (angle + np.pi) % (2 * np.pi) - np.pi

