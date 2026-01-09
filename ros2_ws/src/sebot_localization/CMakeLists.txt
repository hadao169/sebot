cmake_minimum_required(VERSION 3.8)
project(sebot_localization)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

include_directories(include)

add_executable(ekf_node src/ekf_node.cpp)
target_include_directories(ekf_node PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${Eigen3_INCLUDE_DIRS}
)
ament_target_dependencies(ekf_node
  rclcpp sensor_msgs nav_msgs geometry_msgs std_msgs tf2 tf2_ros tf2_geometry_msgs
)
target_link_libraries(ekf_node Eigen3::Eigen)

add_executable(uwb_transform_node src/uwb_transform.cpp)
target_include_directories(uwb_transform_node PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${Eigen3_INCLUDE_DIRS}
)
ament_target_dependencies(uwb_transform_node
  rclcpp sensor_msgs nav_msgs geometry_msgs std_msgs tf2 tf2_ros tf2_geometry_msgs
)
target_link_libraries(uwb_transform_node Eigen3::Eigen)

add_executable(uwb_transform_dual_ekf_node src/uwb_transform_dual_ekf.cpp)
target_include_directories(uwb_transform_dual_ekf_node PRIVATE
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  ${Eigen3_INCLUDE_DIRS}
)
ament_target_dependencies(uwb_transform_dual_ekf_node
  rclcpp sensor_msgs nav_msgs geometry_msgs std_msgs tf2 tf2_ros tf2_geometry_msgs
)
target_link_libraries(uwb_transform_dual_ekf_node Eigen3::Eigen)


install(TARGETS 
  ekf_node
  uwb_transform_node
  uwb_transform_dual_ekf_node
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch config 
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()