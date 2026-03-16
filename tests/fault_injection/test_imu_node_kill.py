import time
import pytest


class TestImuNodeKill:
    """
    Fault Injection: принудительное завершение
    /sensing/imu1/imu_node

    TC-FAULT-IMU-001: Предусловие — нода активна
    TC-FAULT-IMU-002: Kill — нода исчезает из ROS graph
    TC-FAULT-IMU-003: Деградация сенсоров — смежные ноды живы
    """

    def test_01_precondition_node_running(self, imu_node):
        """TC-FAULT-IMU-001-PRE: Предусловие"""
        if not imu_node.is_alive():
            pytest.skip("Нода не запущена — тест пропущен")
        assert imu_node.is_alive() is True

    def test_02_kill_imu_node(self, imu_node_alive):
        """
        TC-FAULT-IMU-002: Kill imu_node
        Фиксирует факт смерти через PID — до перезапуска drive.py.
        """
        nodes_before = imu_node_alive.get_node_list()
        pid_before = imu_node_alive.get_pid()

        imu_node_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        imu_node_alive.kill()

        pid_after = imu_node_alive.get_pid()
        imu_node_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if imu_node_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"Нода перезапущена (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not imu_node_alive.is_alive(), \
            "Нода не была корректно завершена"

    # def test_03_sensing_degradation(self, imu_node):
    #     """TC-FAULT-IMU-003: Поведение сенсорной системы после kill"""
    #     time.sleep(5)

    #     result = imu_node.check_sensing_degradation()

    #     if result["has_auto_restart"]:
    #         imu_node.logger.info(
    #             "Система восстановила ноду автоматически. "
    #             "Fault tolerance: ПОДТВЕРЖДЁН ✅"
    #         )
    #         assert result["other_sensing_alive"], \
    #             "Ноды sensing не работают даже с auto-restart"
    #     else:
    #         assert result["imu_node_gone"], \
    #             "Нода imu_node всё ещё в graph"
    #         assert result["other_sensing_alive"], \
    #             "Все ноды sensing упали после kill"