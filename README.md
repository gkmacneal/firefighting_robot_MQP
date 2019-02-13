# Firefighting Robot MQP

This is the overarching repository for all code that goes into this project.
To use the repository, clone it onto any device that will be running software for the project, then copy subdirectories to other locations on the device as necessary.
For example, the "fred" directory should be copied into home/ubuntu/catkin_ws/src on the robot's Raspberry Pi.

ROS topics:

VL53L0X IR Range Finder: "range"

BME680 - Temperature: "intern_temp"

BME680 - Humidity: "intern_humidity"

MLX90640 Thermal Array (x4): "thermal_X" (X is 0-3)
