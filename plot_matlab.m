filename = 'sebot_multi_column.txt';
data = load(filename);

% 2. Extract Data Columns
% Column 1: ROS Timestamp (nanoseconds)
raw_time = data(:, 1);
% Convert timestamp to seconds and offset to start at 0
t = (raw_time - raw_time(1)) / 1e9;

% /wheel/odom (Columns 2, 3) - Only wheel encoders
odom_x = data(:, 2); odom_y = data(:, 3);

% /odometry/uwb_data (Columns 4, 5) - UWB data after transform
uwb_x  = data(:, 4); uwb_y  = data(:, 5);

% /odometry/filter (Columns 6, 7) - Loosely coupled
final_x = data(:, 6); final_y = data(:, 7);

% /odometry/filtered/local (Columns 8, 9) - ROS2 EKF local
local_x = data(:, 8); local_y = data(:, 9);

% /odometry/filtered/global (Columns 10, 11) - ROS2 EKF global
global_x = data(:, 10); global_y = data(:, 11);

% 3. Trajectory Plot
%% Figure 1: ROS 2 Dual EKF architecture
figure(1);
set(gcf, 'Units', 'pixels', 'Position', [100, 100, 900, 900]);
hold on;
plot(uwb_x, uwb_y, 'r-', 'LineWidth', 2, 'DisplayName', 'UWB (Transformed)');
plot(odom_x, odom_y, 'k-', 'LineWidth', 2, 'DisplayName', 'Wheel Odom');
plot(local_x, local_y, 'b-', 'LineWidth', 2, 'DisplayName', 'EKF Local');
plot(global_x, global_y, 'g-', 'LineWidth', 2, 'DisplayName', 'EKF Global (Final)');
title('Trajectory Analysis: Dual-Stage EKF Fusion (IMU/Odom + UWB)', 'FontSize', 16);xlabel('X Position (m)', 'FontSize', 18);
ylabel('Y Position (m)', 'FontSize', 18);
grid_step = 0.5;
ax1 = gca();
x_lims = [floor(min([uwb_x; odom_x])), ceil(max([uwb_x; odom_x]))];
y_lims = [floor(min([uwb_y; odom_y])), ceil(max([uwb_y; odom_y]))];
set(ax1, 'XTick', x_lims(1):grid_step:x_lims(2));
set(ax1, 'YTick', y_lims(1):grid_step:y_lims(2));
set(ax1, 'FontSize', 16);
set(ax1, 'Position', [0.12, 0.12, 0.60, 0.75]);
legend('location', 'northeastoutside', 'FontSize', 18);
axis square;
grid on;
hold off;

%% Figure 2: Loosely Coupled
figure(2);
set(gcf, 'Units', 'pixels', 'Position', [150, 150, 900, 900]);
hold on;
plot(uwb_x, uwb_y, 'r-', 'LineWidth', 2, 'DisplayName', 'UWB (Transformed)');
plot(odom_x, odom_y, 'k-', 'LineWidth', 2, 'DisplayName', 'Wheel Odom');
plot(final_x, final_y, 'y-', 'LineWidth', 2, 'DisplayName', 'EKF loosely couple (Final)');
title('Trajectory Analysis: Loosely Coupled Sensor Fusion', 'FontSize', 16);
xlabel('X Position (m)', 'FontSize', 18);
ylabel('Y Position (m)', 'FontSize', 18);
ax2 = gca();
set(ax2, 'XTick', x_lims(1):grid_step:x_lims(2));
set(ax2, 'YTick', y_lims(1):grid_step:y_lims(2));
set(ax2, 'FontSize', 16);
set(ax2, 'Position', [0.12, 0.12, 0.60, 0.75]);
legend('location', 'northeastoutside', 'FontSize', 18);
grid on;
axis square;
hold off;

