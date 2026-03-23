import pandas as pd
import matplotlib.pyplot as plt

try:
    df = pd.read_csv('pos_data19.csv')
    print("Data loaded successfully.")
except FileNotFoundError:
    print("File pos_data.csv not found.")
    exit()

# Calculate relative time (starting from 0s)
df['Time_Relative'] = df['Timestamp'] - df['Timestamp'].iloc[0]

# CREATE PLOT 1: TRAJECTORY COMPARISON (X vs Y)
plt.figure(figsize=(10, 7))
plt.plot(df['Enc_X_Transformed'], df['Enc_Y_Transformed'], label='Encoder (Transformed)', color='blue', linestyle='--', linewidth=2)
plt.plot(df['UWB_X'], df['UWB_Y'], label='Actual UWB', color='red', alpha=0.6)

# Mark the starting point
plt.scatter(df['Enc_X_Transformed'].iloc[0], df['Enc_Y_Transformed'].iloc[0], color='green', s=100, label='Start Point', zorder=5)

plt.xlabel('X Coordinate (m)')
plt.ylabel('Y Coordinate (m)')
plt.title('Trajectory Comparison: Encoder Transformed vs UWB')
plt.legend()
plt.grid(True, linestyle=':', alpha=0.7)
plt.axis('equal') # Keep X and Y axis scale equal to prevent trajectory distortion
plt.savefig('trajectory_comparison.png')
print("Trajectory plot saved: trajectory_comparison.png")

# CREATE PLOT 2: ERROR OVER TIME
plt.figure(figsize=(10, 5))
plt.plot(df['Time_Relative'], df['Delta_Error'], color='darkviolet', linewidth=1.5)

plt.xlabel('Time (s)')
plt.ylabel('Euclidean Error (m)')
plt.title('Position Error Variation Over Time')
plt.grid(True, alpha=0.3)
plt.savefig('error_over_time.png')
print("Error plot saved: error_over_time.png")

# Display both plots
plt.show()