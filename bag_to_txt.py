from pathlib import Path
from rosbags.highlevel import AnyReader

# Đường dẫn tệp tin của bạn
bag_path = Path('/home/k5001682/sebot_uwb_localization/new_tests/rosbag2_2026_03_02-02_11_23/rosbag2_2026_03_02-02_11_23_0.mcap') 
output_file = 'sebot_multi_column.txt'

# Danh sách topic theo đúng thứ tự meas0 -> meas5
target_topics = [
    '/wheel/odom',                  # ID 0 (Cột 2, 3)
    '/odometry/uwb_data',           # ID 1 (Cột 4, 5)
    '/odometry/filter',             # ID 2 (Cột 6, 7)
    '/odometry/filtered/local',      # ID 3 (Cột 8, 9)
    '/odometry/filtered/global',     # ID 4 (Cột 10, 11)
    '/dwm1001/id_DW878F/pose'       # ID 5 (Cột 12, 13)
]

def export_to_space_separated():
    if not bag_path.exists():
        print(f"LỖI: Không tìm thấy file tại {bag_path}")
        return

    # Khởi tạo mảng 12 phần tử (6 topic * 2 tọa độ x,y)
    current_values = [0.0] * 12
    
    try:
        with open(output_file, 'w') as f:
            with AnyReader([bag_path]) as reader:
                # Lọc các kết nối khớp với danh sách target_topics
                connections = [c for c in reader.connections if c.topic in target_topics]
                
                for connection, timestamp, rawdata in reader.messages(connections=connections):
                    msg = reader.deserialize(rawdata, connection.msgtype)
                    
                    # Xác định ID để biết cập nhật vào cặp cột nào
                    topic_id = target_topics.index(connection.topic)
                    
                    # Trích xuất tọa độ linh hoạt
                    try:
                        if hasattr(msg, 'pose') and hasattr(msg.pose, 'pose'): # nav_msgs/Odometry
                            current_values[topic_id*2] = msg.pose.pose.position.x
                            current_values[topic_id*2 + 1] = msg.pose.pose.position.y
                        elif hasattr(msg, 'pose'): # geometry_msgs/PoseStamped
                            x = msg.pose.position.x
                            y = msg.pose.position.y
                            current_values[topic_id*2] = x
                            current_values[topic_id*2 + 1] = y
                    except Exception:
                        continue

                    # Tạo chuỗi dữ liệu phân cách bằng KHOẢNG TRẮNG
                    # Cấu trúc: timestamp x0 y0 x1 y1 x2 y2 x3 y3 x4 y4 x5 y5
                    values_str = " ".join(f"{v:.6f}" for v in current_values)
                    f.write(f"{timestamp} {values_str}\n")

        print(f"Thành công! Dữ liệu xuất ra: {output_file}")
        print("Định dạng: Timestamp Meas0X Meas0Y Meas1X Meas1Y ... Meas5X Meas5Y")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    export_to_space_separated()