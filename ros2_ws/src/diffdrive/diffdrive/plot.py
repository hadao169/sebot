import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Thay ten file CSV cua ban vao day
file_path = 'optimal_sync_log_20260109_xxxxxx.csv'

try:
    data = pd.read_csv(file_path)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # 1. Plot Quy dao 2D
    ax1.plot(data['EKF_X'], data['EKF_Y'], label='Fused Path (EKF)', color='blue', linewidth=2)
    ax1.scatter(data['UWB_X'], data['UWB_Y'], label='Raw UWB (Transformed)', color='red', s=10, alpha=0.4)
    ax1.set_title('Robot Trajectory Comparison')
    ax1.set_xlabel('X (meters)')
    ax1.set_ylabel('Y (meters)')
    ax1.legend()
    ax1.grid(True)
    ax1.axis('equal')

    # 2. Plot Sai so (Error)
    time_axis = data['Timestamp'] - data['Timestamp'].iloc[0]
    ax2.plot(time_axis, data['Error'], color='green', label='Distance Error')
    ax2.axhline(y=np.mean(data['Error']), color='orange', linestyle='--', label=f'Mean Error: {np.mean(data["Error"]):.3f}m')
    ax2.set_title('Localization Error Over Time')
    ax2.set_xlabel('Time (seconds)')
    ax2.set_ylabel('Error (meters)')
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

    # In thong so thong ke
    print(f"Mean Error: {np.mean(data['Error']):.4f} m")
    print(f"Max Error: {np.max(data['Error']):.4f} m")
    print(f"RMSE: {np.sqrt(np.mean(data['Error']**2)):.4f} m")

except FileNotFoundError:
    print("Khong tim thay file CSV. Vui long kiem tra lai duong dan.")