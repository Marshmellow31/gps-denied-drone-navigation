cmake_minimum_required(VERSION 3.0.2)
project(livox_ros_driver)

# FAST-LIO requires these message definitions at compile time even for
# Velodyne-only playback. This package intentionally contains no device driver.
find_package(catkin REQUIRED COMPONENTS message_generation std_msgs)
add_message_files(FILES CustomPoint.msg CustomMsg.msg)
generate_messages(DEPENDENCIES std_msgs)
catkin_package(CATKIN_DEPENDS message_runtime std_msgs)
