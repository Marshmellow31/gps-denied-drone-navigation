# Point-LIO Livox message shim

This small catkin package contains only the two message definitions Point-LIO
includes at compile time. The definitions are from Livox's official
`livox_ros_driver` v2.6.0 source commit
`fb5669b90af07915c1870d106cc1e4e1ef1f5a15` and retain their MIT attribution.
They are checked against the upstream [`CustomMsg.msg`](https://github.com/Livox-SDK/livox_ros_driver/blob/v2.6.0/livox_ros_driver/msg/CustomMsg.msg)
and [`CustomPoint.msg`](https://github.com/Livox-SDK/livox_ros_driver/blob/v2.6.0/livox_ros_driver/msg/CustomPoint.msg).

This is **not** the Livox hardware driver. It provides no node, SDK, launch
files, or sensor access. The accepted Point-LIO study configuration uses the
simulated Velodyne-style `PointCloud2` input; the shim exists only because the
pinned Point-LIO source lists the optional Livox message package as a build
dependency. Do not use it to claim support for or validate a Livox sensor.
