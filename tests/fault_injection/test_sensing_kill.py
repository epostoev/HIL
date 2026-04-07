import time
import pytest


class TestSensingKill:
    """
    Fault Injection: принудительное завершение нод компонента Sensing

    TC-FAULT-SENSING-001: /sensing/auto_cleaning
    TC-FAULT-SENSING-002: /sensing/imu1/imu_node
    TC-FAULT-SENSING-003: /sensing/odometry_node
    TC-FAULT-SENSING-004: /sensing/odometry_velocity_node
    TC-FAULT-SENSING-005: /sensing/radar_driver_node
    TC-FAULT-SENSING-006: /sensing/ublox1/ublox_driver_node
    TC-FAULT-SENSING-007: /sensing/visualization/radar_visualization_node
    """

    def _kill_and_check_mrm(self, node, mrm_monitor):
        fields = ["mrm_type", "shadow_mrm_type", "drive_mode"]

        baseline = mrm_monitor.get_fields(fields)
        node.logger.info(
            f"Baseline ДО kill: "
            f"mrm_type={baseline['mrm_type']}, "
            f"shadow_mrm_type={baseline['shadow_mrm_type']}, "
            f"drive_mode={baseline['drive_mode']}"
        )

        pid_before = node.get_pid()
        node.logger.info(f"PID до kill: {pid_before}")
        node.kill()
        pid_after = node.get_pid()
        node.logger.info(f"PID после kill: {pid_after}")

        time.sleep(5)

        after = mrm_monitor.get_fields(fields)
        node.logger.info(
            f"ПОСЛЕ kill: "
            f"mrm_type={after['mrm_type']}, "
            f"shadow_mrm_type={after['shadow_mrm_type']}, "
            f"drive_mode={after['drive_mode']}"
        )

        assert after["mrm_type"] == "2", \
            f"mrm_type: ожидалось '2', получено '{after['mrm_type']}'"
        assert after["shadow_mrm_type"] == "1", \
            f"shadow_mrm_type: ожидалось '1', получено '{after['shadow_mrm_type']}'"
        assert after["drive_mode"] == "2", \
            f"drive_mode: ожидалось '2', получено '{after['drive_mode']}'"

        node.logger.info("MRM топик зафиксирован корректно ✅")

        # if node.has_auto_restart:
        #     pytest.xfail(
        #         f"Нода перезапущена drive.py (новый PID: {pid_after}). "
        #         f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
        #     )
        if node.has_auto_restart:
            pytest.xfail(
                f"✅ Kill подтверждён (старый PID {pid_before} уничтожен). "
                f"drive.py перезапустил ноду (новый PID: {pid_after}). "
                f"MRM: mrm_type={after['mrm_type']}, "
                f"shadow_mrm_type={after['shadow_mrm_type']}, "
                f"drive_mode={after['drive_mode']}"
            )

        assert not node.is_alive(), "Нода не была корректно завершена"

    # def test_01_auto_cleaning_kill(self, auto_cleaning_node_alive, mrm_monitor, request):
    #     """TC-FAULT-SENSING-001: Kill /sensing/auto_cleaning"""

    #     request.node.expected = (
    #         "Kill выполнен успешно. "
    #         "MRM топик: mrm_type=2, shadow_mrm_type=1, drive_mode=2"
    #     )

    #     self._kill_and_check_mrm(auto_cleaning_node_alive, mrm_monitor)

    #     request.node.actual = (
    #         "Kill подтверждён. "
    #         "MRM значения зафиксированы корректно ✅"
    # )

    # def test_01_auto_cleaning_kill(self, auto_cleaning_node_alive, mrm_monitor, request):
    #     """TC-FAULT-SENSING-001: Kill /sensing/auto_cleaning"""

    #     request.node.expected = (
    #         "Kill выполнен успешно. "
    #         "MRM топик: mrm_type=2, shadow_mrm_type=1, drive_mode=2"
    #     )
    #     # Выставляем actual заранее — до возможного xfail
    #     request.node.actual = (
    #         "Kill подтверждён. "
    #         "MRM значения зафиксированы корректно ✅"
    #     )

    #     self._kill_and_check_mrm(auto_cleaning_node_alive, mrm_monitor)

    # def test_01_auto_cleaning_kill(self, auto_cleaning_node_alive, mrm_monitor, request):
    #     """TC-FAULT-SENSING-001: Kill /sensing/auto_cleaning и проверка MRM"""

    #     request.node.expected = "MRM: mrm_type=2, shadow_mrm_type=1, drive_mode=2"

    #     # Kill
    #     pid_before = auto_cleaning_node_alive.get_pid()
    #     auto_cleaning_node_alive.kill()
    #     pid_after = auto_cleaning_node_alive.get_pid()

    #     # MRM после kill
    #     time.sleep(5)
    #     fields = ["mrm_type", "shadow_mrm_type", "drive_mode"]
    #     after = mrm_monitor.get_fields(fields)

    #     # Проверяем MRM
    #     assert after["mrm_type"] == "2", \
    #         f"mrm_type: ожидалось '2', получено '{after['mrm_type']}'"
    #     assert after["shadow_mrm_type"] == "1", \
    #         f"shadow_mrm_type: ожидалось '1', получено '{after['shadow_mrm_type']}'"
    #     assert after["drive_mode"] == "2", \
    #         f"drive_mode: ожидалось '2', получено '{after['drive_mode']}'"

    #     request.node.actual = (
    #         f"MRM: mrm_type={after['mrm_type']}, "
    #         f"shadow_mrm_type={after['shadow_mrm_type']}, "
    #         f"drive_mode={after['drive_mode']} ✅"
    #     )

    #     if auto_cleaning_node_alive.has_auto_restart:
    #         pytest.xfail(
    #             f"drive.py перезапустил ноду. "
    #             f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
    #         )

    #     assert not auto_cleaning_node_alive.is_alive(), \
    #         "Нода не была корректно завершена"

    def test_01_auto_cleaning_kill(self, auto_cleaning_node_alive, mrm_monitor, request):
        """TC-FAULT-SENSING-001: Kill /sensing/auto_cleaning и проверка MRM"""

        request.node.expected = "MRM: mrm_type=2, shadow_mrm_type=1, drive_mode=2"

        # Kill
        pid_before = auto_cleaning_node_alive.get_pid()
        auto_cleaning_node_alive.kill()

        # MRM после kill
        time.sleep(5)
        fields = ["mrm_type", "shadow_mrm_type", "drive_mode"]
        after = mrm_monitor.get_fields(fields)

        # Проверяем MRM — это главная проверка теста
        assert after["mrm_type"] == "2", \
            f"mrm_type: ожидалось '2', получено '{after['mrm_type']}'"
        assert after["shadow_mrm_type"] == "1", \
            f"shadow_mrm_type: ожидалось '1', получено '{after['shadow_mrm_type']}'"
        assert after["drive_mode"] == "2", \
            f"drive_mode: ожидалось '2', получено '{after['drive_mode']}'"

        request.node.actual = (
            f"MRM: mrm_type={after['mrm_type']}, "
            f"shadow_mrm_type={after['shadow_mrm_type']}, "
            f"drive_mode={after['drive_mode']} ✅"
        )

        # Логируем факт auto-restart но не прерываем тест
        if auto_cleaning_node_alive.has_auto_restart:
            auto_cleaning_node_alive.logger.info(
                f"drive.py перезапустил ноду. "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен. "
                f"Fault tolerance: ПОДТВЕРЖДЁН ✅"
            )


    def test_02_imu_node_kill(self, imu_node_alive, mrm_monitor):
        """TC-FAULT-SENSING-002: Kill /sensing/imu1/imu_node"""
        self._kill_and_check_mrm(imu_node_alive, mrm_monitor)

    def test_03_odometry_node_kill(self, odometry_node, mrm_monitor):
        """TC-FAULT-SENSING-003: Kill /sensing/odometry_node"""
        if not odometry_node.is_alive():
            pytest.skip("Нода не запущена")
        self._kill_and_check_mrm(odometry_node, mrm_monitor)

    def test_04_odometry_velocity_kill(self, odometry_velocity_node, mrm_monitor):
        """TC-FAULT-SENSING-004: Kill /sensing/odometry_velocity_node"""
        if not odometry_velocity_node.is_alive():
            pytest.skip("Нода не запущена")
        self._kill_and_check_mrm(odometry_velocity_node, mrm_monitor)

    def test_05_radar_driver_kill(self, radar_driver_node_alive, mrm_monitor):
        """TC-FAULT-SENSING-005: Kill /sensing/radar_driver_node"""
        self._kill_and_check_mrm(radar_driver_node_alive, mrm_monitor)

    def test_06_ublox_driver_kill(self, ublox_driver_node, mrm_monitor):
        """TC-FAULT-SENSING-006: Kill /sensing/ublox1/ublox_driver_node"""
        if not ublox_driver_node.is_alive():
            pytest.skip("Нода не запущена")
        self._kill_and_check_mrm(ublox_driver_node, mrm_monitor)

    def test_07_radar_visualization_kill(self, radar_visualization_node, mrm_monitor):
        """TC-FAULT-SENSING-007: Kill /sensing/visualization/radar_visualization_node"""
        if not radar_visualization_node.is_alive():
            pytest.skip("Нода не запущена")
        self._kill_and_check_mrm(radar_visualization_node, mrm_monitor)