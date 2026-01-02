import numpy as np
import matplotlib.pyplot as plt

def read_and_plot(csv_file):
    # Đọc file CSV
    try:
        data = np.genfromtxt(csv_file, delimiter=',', skip_header=1)
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return

    if data.ndim == 1:
        data = data.reshape(1, -1)

    # Tách các cột
    timestamp = data[:, 0]
    encoder_L = data[:, 1]
    encoder_R = data[:, 2]
    delta_l = data[:, 3]
    delta_r = data[:, 4]
    delta_distance = data[:, 5]
    total_distance = data[:, 6]
    odom_x = data[:, 7]
    odom_y = data[:, 8]
    odom_theta = data[:, 9]

    # Tính tick trên 1 m cho mỗi bánh
    try:
        total_ticks_L = encoder_L[-1] - encoder_L[0]
        total_ticks_R = encoder_R[-1] - encoder_R[0]
        total_moved = total_distance[-1] - total_distance[0]  # m
        ticks_per_m_L = total_ticks_L / total_moved
        ticks_per_m_R = total_ticks_R / total_moved
        print(f"Left wheel ticks per meter: {ticks_per_m_L:.2f}")
        print(f"Right wheel ticks per meter: {ticks_per_m_R:.2f}")
    except:
        ticks_per_m_L = ticks_per_m_R = 0

    # Tính vận tốc xấp xỉ (Δd / Δt)
    dt = np.diff(timestamp)
    dt = np.where(dt == 0, 1e-6, dt)  # tránh chia 0
    vel_L = np.diff(delta_l) / dt
    vel_R = np.diff(delta_r) / dt
    vel_total = np.diff(delta_distance) / dt

    # === Plot dữ liệu ===
    plt.figure(figsize=(14, 10))

    # Encoder tổng
    plt.subplot(4, 1, 1)
    plt.plot(timestamp, encoder_L, label="Encoder L")
    plt.plot(timestamp, encoder_R, label="Encoder R")
    plt.title("Encoder Counts")
    plt.xlabel("Time (s)")
    plt.ylabel("Ticks")
    plt.legend()
    plt.grid(True)

    # Delta distance từng bước
    plt.subplot(4, 1, 2)
    plt.plot(timestamp, delta_l, label="Δ Left")
    plt.plot(timestamp, delta_r, label="Δ Right")
    plt.title("Delta Distance per Step")
    plt.xlabel("Time (s)")
    plt.ylabel("Δd (m)")
    plt.legend()
    plt.grid(True)

    # Tốc độ xấp xỉ
    plt.subplot(4, 1, 3)
    plt.plot(timestamp[1:], vel_L, label="v Left")
    plt.plot(timestamp[1:], vel_R, label="v Right")
    plt.plot(timestamp[1:], vel_total, label="v Total")
    plt.title("Estimated Velocity")
    plt.xlabel("Time (s)")
    plt.ylabel("v (m/s)")
    plt.legend()
    plt.grid(True)

    # Quãng đường tích lũy
    plt.subplot(4, 1, 4)
    plt.plot(timestamp, total_distance, label="Total Distance")
    plt.title("Cumulative Distance")
    plt.xlabel("Time (s)")
    plt.ylabel("Distance (m)")
    plt.grid(True)
    plt.legend()

    plt.tight_layout()
    plt.show()


# Example usage
if __name__ == "__main__":
    read_and_plot("odom_log.csv")
