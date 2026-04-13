import pytest


SENSING_NODES = [
    ("auto_cleaning_node",       "TC-SENSING-PRE-001", "/sensing/auto_cleaning"),
    ("imu_node",                 "TC-SENSING-PRE-002", "/sensing/imu1/imu_node"),
    ("odometry_node",            "TC-SENSING-PRE-003", "/sensing/odometry_node"),
    ("odometry_velocity_node",   "TC-SENSING-PRE-004", "/sensing/odometry_velocity_node"),
    ("radar_driver_node",        "TC-SENSING-PRE-005", "/sensing/radar_driver_node"),
    ("ublox_driver_node",        "TC-SENSING-PRE-006", "/sensing/ublox1/ublox_driver_node"),
    ("radar_visualization_node", "TC-SENSING-PRE-007", "/sensing/visualization/radar_visualization_node"),
]


class TestSensingNodesRunning:
    """
    Проверка что все ноды компонента Sensing запущены.
    """

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", SENSING_NODES)
    def test_node_running(self, fixture_name, tc_id, node_name, request):
        f"""{tc_id}: {node_name} присутствует в ROS graph"""

        node = request.getfixturevalue(fixture_name)

        request.node.expected = f"Нода {node_name} присутствует в ROS graph"

        if not node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip(f"Нода {node_name} не запущена")

        assert node.is_alive() is True

        request.node.actual = f"Нода {node_name} присутствует в ROS graph ✅"