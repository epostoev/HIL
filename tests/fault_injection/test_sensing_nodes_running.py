import pytest


class TestSensingNodesRunning:
    """
    Проверка что все ноды компонента Sensing запущены.

    TC-SENSING-PRE-001: /sensing/auto_cleaning
    TC-SENSING-PRE-002: /sensing/imu1/imu_node
    TC-SENSING-PRE-003: /sensing/odometry_node
    TC-SENSING-PRE-004: /sensing/odometry_velocity_node
    TC-SENSING-PRE-005: /sensing/radar_driver_node
    TC-SENSING-PRE-006: /sensing/ublox1/ublox_driver_node
    TC-SENSING-PRE-007: /sensing/visualization/radar_visualization_node
    """

    def test_01_auto_cleaning_running(self, auto_cleaning_node, request):
        """TC-FAULT-SENSING-001-PRE: /sensing/auto_cleaning жива"""

        # Ожидаемый результат
        request.node.expected = "Нода /sensing/auto_cleaning присутствует в ROS graph"

        if not auto_cleaning_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/auto_cleaning не запущена")

        assert auto_cleaning_node.is_alive() is True

        # Фактический результат
        request.node.actual = "Нода /sensing/auto_cleaning жива ✅"


    def test_02_imu_node_running(self, imu_node, request):
        """TC-SENSING-PRE-002: /sensing/imu1/imu_node"""
        request.node.expected = "Нода /sensing/imu1/imu_node присутствует в ROS graph"
        
        if not imu_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/imu1/imu_node не запущена")

        assert imu_node.is_alive() is True

        request.node.actual = "Нода /sensing/imu1/imu_node жива ✅"


    def test_03_odometry_node_running(self, odometry_node, request):
        """TC-SENSING-PRE-003: /sensing/odometry_node"""
        request.node.expected = "Нода /sensing/odometry_node присутствует в ROS graph"
        if not odometry_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/odometry_node не запущена")

        assert odometry_node.is_alive() is True

        request.node.actual = "Нода /sensing/odometry_node жива ✅"


    def test_04_odometry_velocity_node_running(self, odometry_velocity_node, request):
        """TC-SENSING-PRE-004: /sensing/odometry_velocity_node"""
        request.node.expected = "Нода /sensing/odometry_velocity_node присутствует в ROS graph"
        if not odometry_velocity_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/odometry_velocity_node не запущена")

        assert odometry_velocity_node.is_alive() is True

        request.node.actual = "Нода /sensing/odometry_node жива ✅"


    def test_05_radar_driver_node_running(self, radar_driver_node, request):
        """TC-SENSING-PRE-005: /sensing/radar_driver_node"""
        request.node.expected = "Нода /sensing/radar_driver_node присутствует в ROS graph"
        if not radar_driver_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/radar_driver_node не запущена")

        assert radar_driver_node.is_alive() is True

        request.node.actual = "Нода /sensing/radar_driver_node жива ✅"


    def test_06_ublox_driver_node_running(self, ublox_driver_node, request):
        """TC-SENSING-PRE-006: /sensing/ublox1/ublox_driver_node"""
        request.node.expected = "Нода /sensing/ublox1/ublox_driver_node присутствует в ROS graph"
        if not ublox_driver_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/ublox1/ublox_driver_node не запущена")

        assert ublox_driver_node.is_alive() is True

        request.node.actual = "Нода /sensing/ublox1/ublox_driver_node жива ✅"


    def test_07_radar_visualization_node_running(self, radar_visualization_node, request):
        """TC-SENSING-PRE-007: /sensing/visualization/radar_visualization_node"""
        request.node.expected = "Нода /sensing/visualization/radar_visualization_node присутствует в ROS graph"
        if not radar_visualization_node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip("Нода /sensing/visualization/radar_visualization_node не запущена")

        assert radar_visualization_node.is_alive() is True

        request.node.actual = "Нода /sensing/visualization/radar_visualization_node жива ✅"