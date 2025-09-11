import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable, LogInfo
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, PathJoinSubstitution

def generate_launch_description():
    pkg_share = get_package_share_directory('auv_description')
    
    # Paths
    urdf_file_path = os.path.join(pkg_share, 'urdf', 'auv','auv.urdf.xacro')
    world_path = os.path.join(pkg_share, 'worlds', 'sauvc_world.sdf')
    rviz_config_path = os.path.join(pkg_share, 'rviz', 'default.rviz')
    models_path = os.path.join(pkg_share, 'models')

    # Debug output
    debug_info = LogInfo(msg=f"Models path: {models_path}")
    
    # # Check if models exist
    # pool_ground_path = os.path.join(models_path, 'pool_ground')
    # wall_path = os.path.join(models_path, 'wall')
    
    # if not os.path.exists(pool_ground_path):
    #     debug_info = LogInfo(msg=f"WARNING: pool_ground model not found at {pool_ground_path}")
    # if not os.path.exists(wall_path):
    #     debug_info = LogInfo(msg=f"WARNING: wall model not found at {wall_path}")

    robot_description = ParameterValue(Command(['xacro ', urdf_file_path]), value_type=str)

    # Set GAZEBO_MODEL_PATH with multiple possible locations
    gazebo_model_path = SetEnvironmentVariable(
        name='GAZEBO_MODEL_PATH',
        value=models_path + ':' + os.environ.get('GAZEBO_MODEL_PATH', '')
    )

    # Also set GZ_SIM_RESOURCE_PATH for Ignition Gazebo
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=models_path + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
    )

    start_gazebo_cmd = ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-v', '4', world_path],
        output='screen',
        additional_env={
            'GAZEBO_MODEL_PATH': models_path + ':' + os.environ.get('GAZEBO_MODEL_PATH', ''),
            'GZ_SIM_RESOURCE_PATH': models_path + ':' + os.environ.get('GZ_SIM_RESOURCE_PATH', '')
        }
    )

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': True}]
    )

    spawn_robot_node = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'fathom_auv',
            '-x', '8.42',
            '-y', '-13.66',
            '-z', '0.15',
            '-R', '0',
            '-P', '-0.10',
            '-Y', '1.61'
        ],
        output='screen'
    )

    start_rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config_path],
        parameters=[{'use_sim_time': True}]
    )

    return LaunchDescription([
        debug_info,
        gazebo_model_path,
        gz_resource_path,
        start_gazebo_cmd,
        robot_state_publisher_node,
        spawn_robot_node,
        start_rviz_node
    ])