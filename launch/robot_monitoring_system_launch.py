from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os

def generate_launch_description():
    state_monitor_params = os.path.join(get_package_share_directory('lab5'), 'config', 'state_monitor_params.yaml')
    error_handler_params = os.path.join(get_package_share_directory('lab5'), 'config', 'error_handler_params.yaml')
    camera_params = os.path.join(get_package_share_directory('lab5'), 'config', 'camera_params.yaml')
    lidar_params = os.path.join(get_package_share_directory('lab5'), 'config', 'lidar_params.yaml')

    return LaunchDescription([
        Node(
            package='lab5',
            executable='state_monitor',
            parameters=[state_monitor_params]
        ),
        Node(
            package='lab5',
            executable='error_handler',
            parameters=[error_handler_params]
        ),
        Node(
            package='lab5',
            executable='sensor',
            name='camera',
            parameters=[camera_params]
        ),
        Node(
            package='lab5',
            executable='sensor',
            name='lidar',
            parameters=[lidar_params]
        )
    ])