# Process noise covariance Qk
process_noise_covariance = [
			[0.05, 0, 0],
			[0, 0.05, 0],	
			[0, 0, 0.06]
]

# Initial state covariance P0
initial_estimate_covariance = [
			[1e-9, 0, 0],
			[0, 1e-9, 0],
			[0, 0, 1e-9]
]	

# Measurement noise covariance R
measurement_noise_covariance = [
			[0.01, 0],
			[0, 0.01],
			# [0, 0, 0.0005]
]
