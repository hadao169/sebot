cmake_minimum_required(VERSION 3.8)
project(diffdrivec)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(motordriver_msgs REQUIRED)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

# Add the Encoder library
add_library(encoder src/encoder.cpp)
target_include_directories(encoder PUBLIC include)
ament_target_dependencies(encoder rclcpp)

add_executable(cmd_vel_node src/cmd_vel.cpp)
ament_target_dependencies(cmd_vel_node rclcpp geometry_msgs std_msgs)

install(TARGETS
  cmd_vel_node
  DESTINATION lib/${PROJECT_NAME})

# Add the odom_node executable
add_executable(odom_node src/odom.cpp)
ament_target_dependencies(odom_node rclcpp nav_msgs geometry_msgs tf2_ros motordriver_msgs)
target_link_libraries(odom_node encoder)

# Install the encoder library
install(TARGETS
  encoder
  DESTINATION lib/${PROJECT_NAME})

# Install the odom_node executable
install(TARGETS
  odom_node
  DESTINATION lib/${PROJECT_NAME})

ament_package()
