from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    declared_arguments = []
    declared_arguments.append(
        DeclareLaunchArgument(
            "start_rviz",
            default_value="false",
            description="start RViz automatically with the launch file",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "prefix",
            default_value='""',
            description="Prefix of the joint names, useful for \
        multi-robot setup. If changed than also joint names in the controllers' configuration \
        have to be updated.",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "use_fake_hardware",
            default_value="true",
            description="Start robot with fake hardware mirroring command to its states.",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "fake_sensor_commands",
            default_value="true",
            description="Enable fake command interfaces for sensors used for simple simulations. \
            Used only if 'use_fake_hardware' parameter is true.",
        )
    )

    declared_arguments.append(
        DeclareLaunchArgument(
            "slowdown", default_value="3.0",
            description="Slowdown factor of the TurtleBot3."
        )
    )

    # Get URDF via xacro
    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            PathJoinSubstitution(
                [
                    FindPackageShare("turtlebot3_description"),
                    "urdf",
                    "turtlebot3_burger.urdf.xacro",
                ]
            ),
            " prefix:=",
            LaunchConfiguration("prefix"),
            " use_fake_hardware:=",
            LaunchConfiguration("use_fake_hardware"),
            " fake_sensor_commands:=",
            LaunchConfiguration("fake_sensor_commands"),
            " slowdown:=",
            LaunchConfiguration("slowdown"),
        ]
    )
    robot_description = {"robot_description": robot_description_content}

    tb3_controllers = PathJoinSubstitution(
        [
            FindPackageShare("turtlebot3_bringup"),
            "config",
            "tb3_controller.yaml",
        ]
    )

    node_robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[robot_description],
    )

    controller_manager_node = Node(
        package="controller_manager",
        executable="ros2_control_node",
        parameters=[robot_description, tb3_controllers],
        output={
            "stdout": "screen",
            "stderr": "screen",
        },
    )

    spawn_jsb_controller = Node(
        package="controller_manager",
        executable="spawner.py",
        arguments=["joint_state_broadcaster"],
        output="screen",
    )

    rviz_config_file = PathJoinSubstitution(
        [FindPackageShare("turtlebot3_description"), "config", "model.rviz"]
    )
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        arguments=["-d", rviz_config_file],
        condition=IfCondition(LaunchConfiguration("start_rviz")),
    )

    nodes = [
        controller_manager_node,
        node_robot_state_publisher,
        spawn_jsb_controller,
        rviz_node,
    ]
    return LaunchDescription(declared_arguments + nodes)
