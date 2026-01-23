import numpy as np
import matplotlib.pyplot as plt
from LeastSquare import LeastSquare
import ast

FILE_NAME = 'uwb_raw_16_1246.csv'
QUALITY_THRESHOLD = 90


def main():
    ls_solver = LeastSquare(num_anchors=4)

    ls_path = []
    deca_path = []
    quality_list = []
    last_anchors = []
    i = 0
    try:
        with open(FILE_NAME, 'r') as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                uwb_data = ast.literal_eval(line)
                
                if isinstance(uwb_data, str):
                    uwb_data = ast.literal_eval(uwb_data)
                
                # Skip lines that do not have exactly 6 elements (error due to logging issues)
                if len(uwb_data) != 6:
                    continue

                ls_solver.process_uwb_data(uwb_data)
                anchors = ls_solver.measurements
                deca_pos = ls_solver.original_position
                q = ls_solver.quality

                est_x, est_y = ls_solver.estimate_position()

                if est_x is None or est_y is None:
                    continue

                ls_path.append((est_x, est_y))
                deca_path.append([deca_pos[0], deca_pos[1]])
                quality_list.append(q)
                last_anchors = anchors

    except FileNotFoundError:
        print(f"Error: {FILE_NAME} not found.")
        return

    if not ls_path:
        print("No valid data processed.")
        return

    ls_path = np.array(ls_path)
    deca_path = np.array(deca_path)
    quality_list = np.array(quality_list)
    samples = np.arange(len(ls_path))

    err_x = ls_path[:, 0] - deca_path[:, 0]
    err_y = ls_path[:, 1] - deca_path[:, 1]
    euclidean_diff = np.sqrt(err_x**2 + err_y**2)

    # Plot 1: 2D Trajectory
    plt.figure(figsize=(10, 8))
    plt.plot(ls_path[:, 0], ls_path[:, 1], 'r.', markersize=4, alpha=0.3, label='LS Points')
    plt.plot(deca_path[:, 0], deca_path[:, 1], 'b-', alpha=0.6, label='UWB Path')
    # Plot anchors (last known)
    unique_anchors = {a['id']: (a['x'], a['y']) for a in last_anchors}
    for aid, (ax, ay) in unique_anchors.items():
        plt.scatter(ax, ay, c='black', marker='s', s=100)
        plt.text(ax, ay + 0.1, aid, fontweight='bold', ha='center')

    plt.title("Graph 1: 2D Trajectory Comparison")
    plt.xlabel("X Position (m)")
    plt.ylabel("Y Position (m)")
    plt.axis('equal')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Plot 2: X & Y Error
    fig, (ax_x, ax_y) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    ax_x.plot(samples, err_x)
    ax_x.axhline(0, linestyle='--')
    ax_x.set_ylabel("Error X (m)")
    ax_x.set_title("Positional Error Components")
    ax_y.plot(samples, err_y)
    ax_y.axhline(0, linestyle='--')
    ax_y.set_ylabel("Error Y (m)")
    ax_y.set_xlabel("Sample Index")

    plt.tight_layout()

    # Plot 3: Euclidean Error
    plt.figure(figsize=(12, 5))
    plt.plot(samples, euclidean_diff)
    plt.title("Euclidean Error (LS vs Decawave)")
    plt.xlabel("Sample Index")
    plt.ylabel("Error (m)")
    plt.grid(True, alpha=0.3)

    plt.show()


if __name__ == "__main__":
    main()
