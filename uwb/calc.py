import numpy as np
import matplotlib.pyplot as plt
import math

x_calculated = []
y_calculated = []

x_original = []
y_original = []

# The difference (error) between calculated position and Decawave estimated position
error_magnitude = []

file = open("decawavedatafloor.txt", "r")

for row in file:
    row = row.rstrip()
    pieces = row.split()

    measurements = []
    original_position = None 
        
    for p in pieces:
        if (p[:5] == "le_us"):
            continue
        elif p[:3] == "est": 
            # Decawave estimated position
            try:
                xyz_est = p[p.find('[')+1 : p.find(']')]
                xyza_est = xyz_est.split(',')
                original_position = (float(xyza_est[0]), float(xyza_est[1]))
            except ValueError:
                continue
        else:  
            # Extract anchor measurement data     
            measurement = {}
            measurement["id"] = p[:p.find('[')]
            xyz = p[p.find('[')+1 : p.find(']')]
            xyza = xyz.split(',')
            measurement["x"] = float(xyza[0])
            measurement["y"] = float(xyza[1])
            measurement["z"] = float(xyza[2])
            measurement["range"] = float(p[p.find('=')+1 : ])
            measurements.append(measurement)

    if len(measurements) >= 2 and original_position is not None:
        
        x_original.append(original_position[0])
        y_original.append(original_position[1])

        #Starting point for Least Squares is the Decawave estimated position
        x = np.array([[original_position[0]], [original_position[1]]])

        ranges = np.zeros((len(measurements), 1))
        i = 0
        for m in measurements:
            ranges[i][0] = m["range"]   
            i += 1     
            
        estimated_ranges = np.zeros((len(measurements), 1))
        H = np.zeros((len(measurements), 2))

        ii = 0
        while ii < 20:

            i = 0
            for m in measurements:
                # Calculate estimated ranges based on current position estimate x
                estimated_ranges[i][0] = math.sqrt((m["x"] - x[0][0])**2 + (m["y"] - x[1][0])**2) 
                # Calculate Jacobian matrix H
                H[i][0] = (m["x"] - x[0][0]) / estimated_ranges[i][0]
                H[i][1] = (m["y"] - x[1][0]) / estimated_ranges[i][0]
                i += 1

            # Observed minus Predicted ranges
            delta_roo = ranges - estimated_ranges
            # Least Squares
            delta_x = np.linalg.inv(np.transpose(H) @ H) @ np.transpose(H) @ delta_roo
            # Update position estimate
            x = x + delta_x
            
            # Stop if change is smaller than threshold, alnost converged
            if np.linalg.norm(delta_x) < 0.001:
                break
            ii+=1
        
        # Store calculated positions
        x_calculated.append(x[0][0])
        y_calculated.append(x[1][0])

        # Calculate error magnitude
        calc_x = x[0][0]
        calc_y = x[1][0]
        orig_x = original_position[0]
        orig_y = original_position[1]
        
        error = math.sqrt((calc_x - orig_x)**2 + (calc_y - orig_y)**2)
        error_magnitude.append(error)
        
file.close()


if len(x_calculated) > 0:

    print(f"Last Calculated Position: X={x_calculated[-1]:.3f}m, Y={y_calculated[-1]:.3f}")
    # Error Analysis and Visualization using epochs
    plt.figure(figsize=(12, 6))
    
    epochs = np.arange(len(error_magnitude))
    mean_error = np.mean(error_magnitude)
    
    plt.plot(epochs, error_magnitude, 'b-', alpha=0.7, label='Least Squares Correction') 
    plt.scatter(epochs, error_magnitude, color='r', s=10)
    
    plt.axhline(mean_error, color='k', linestyle='--', label=f'Mean of errors: {mean_error:.3f}m')
    
    plt.title('Error magnitude over each measurement')
    plt.xlabel('Index of measurements')
    plt.ylabel('Error Magnitude (m)')
    plt.legend()
    plt.grid(True)
    plt.show()
else:
    print("No measurements found.")