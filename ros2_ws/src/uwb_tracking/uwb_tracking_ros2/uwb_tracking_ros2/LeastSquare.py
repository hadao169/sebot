import numpy as np
import matplotlib.pyplot as plt
import math


class LeastSquare():
    def __init__(self, num_anchors=4):
        self.num_anchors = num_anchors
        self.measurements = []
        self.original_position = None

    def process_uwb_data(self, uwb_data):       
        self.measurements = []
        self.original_position = None
        if uwb_data is None:
            raise ValueError("UWB data is not provided.")

        for anchor in uwb_data:
            try:
                if anchor.startswith("le_us"):
                    continue
                    
                elif anchor.startswith("est"):
                    position = anchor.split("[")[1].split("]")[0].split(",")
                    self.original_position = (
                        float(position[0]), float(position[1]))
                        
                else:
                    measurement = {}
                    measurement["id"] = anchor[0:4]
                    xyz = anchor.split("[")[1].split("]")[0].split(",")
                    measurement["x"] = float(xyz[0])
                    measurement["y"] = float(xyz[1])
                    measurement["z"] = float(xyz[2])
                    measurement["range"] = float(anchor.split("=")[1])
                    self.measurements.append(measurement)
                    
            except (ValueError, IndexError) as e:
                continue 


    def estimate_position(self, max_iterations=20, tolerance=0.001):  
        if self.original_position is None or not self.measurements:
            return None, None
        x = np.array([[self.original_position[0]],
                     [self.original_position[1]]])

        ranges = np.array([[m["range"]] for m in self.measurements])

        estimated_ranges = np.zeros(ranges.shape)
        H = np.zeros((self.num_anchors, 2))

        ii = 0
        while ii < max_iterations:
            i = 0
            for m in self.measurements:
                # Estimated ranges from current position estimate x to each anchor
                estimated_ranges[i][0] = math.sqrt(
                    (m["x"] - x[0][0])**2 + (m["y"] - x[1][0])**2)

                # Jacobian matrix (H): direction cosine matrix containing unit vectors pointing from the linearization point to the location of the ith base station
                H[i][0] = (m["x"] - x[0][0]) / estimated_ranges[i][0]
                H[i][1] = (m["y"] - x[1][0]) / estimated_ranges[i][0]
                i += 1

            # Observed - Predicted ranges
            delta_roo = ranges - estimated_ranges

            # Least Squares solution
            delta_x = np.linalg.inv(np.transpose(
                H) @ H) @ np.transpose(H) @ delta_roo

            # Update position estimate
            x = x - delta_x

            # Check for convergence
            if np.linalg.norm(delta_x) < tolerance:
                break  

            ii += 1

        return x[0][0], x[1][0]

    def calculate_error(self, calculated_position):
        if self.original_position is None:
            raise ValueError("Original position is not set.")
        error_x = calculated_position[0] - self.original_position[0]
        error_y = calculated_position[1] - self.original_position[1]
        error_magnitude = math.sqrt(error_x**2 + error_y**2)
        return error_magnitude
    
