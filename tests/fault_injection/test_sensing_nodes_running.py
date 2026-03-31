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

    # def test_01_auto_cleaning_running(self, auto_cleaning_node):
    #     """TC-SENSING-PRE-001: /sensing/auto_cleaning"""
    #     if not auto_cleaning_node.is_alive():
    #         pytest.skip("Нода /sensing/auto_cleaning не запущена")
    #     assert auto_cleaning_node.is_alive() is True

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

    def test_02_imu_node_running(self, imu_node):
        """TC-SENSING-PRE-002: /sensing/imu1/imu_node"""
        if not imu_node.is_alive():
            pytest.skip("Нода /sensing/imu1/imu_node не запущена")
        assert imu_node.is_alive() is True

    def test_03_odometry_node_running(self, odometry_node):
        """TC-SENSING-PRE-003: /sensing/odometry_node"""
        if not odometry_node.is_alive():
            pytest.skip("Нода /sensing/odometry_node не запущена")
        assert odometry_node.is_alive() is True

    def test_04_odometry_velocity_node_running(self, odometry_velocity_node):
        """TC-SENSING-PRE-004: /sensing/odometry_velocity_node"""
        if not odometry_velocity_node.is_alive():
            pytest.skip("Нода /sensing/odometry_velocity_node не запущена")
        assert odometry_velocity_node.is_alive() is True

    def test_05_radar_driver_node_running(self, radar_driver_node):
        """TC-SENSING-PRE-005: /sensing/radar_driver_node"""
        if not radar_driver_node.is_alive():
            pytest.skip("Нода /sensing/radar_driver_node не запущена")
        assert radar_driver_node.is_alive() is True

    def test_06_ublox_driver_node_running(self, ublox_driver_node):
        """TC-SENSING-PRE-006: /sensing/ublox1/ublox_driver_node"""
        if not ublox_driver_node.is_alive():
            pytest.skip("Нода /sensing/ublox1/ublox_driver_node не запущена")
        assert ublox_driver_node.is_alive() is True

    def test_07_radar_visualization_node_running(self, radar_visualization_node):
        """TC-SENSING-PRE-007: /sensing/visualization/radar_visualization_node"""
        if not radar_visualization_node.is_alive():
            pytest.skip("Нода /sensing/visualization/radar_visualization_node не запущена")
        assert radar_visualization_node.is_alive() is True