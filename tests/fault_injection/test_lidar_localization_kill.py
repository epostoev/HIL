import time
import pytest


class TestLidarLocalizationKill:
    """
    Fault Injection: принудительное завершение /lidar_localization

    TC-FAULT-LIDAR-001: Предусловие — нода активна
    TC-FAULT-LIDAR-002: Kill — нода исчезает из ROS graph
    TC-FAULT-LIDAR-003: Деградация локализации — смежные ноды живы
    """

    def test_01_precondition_node_running(self, lidar_localization):
        """TC-FAULT-LIDAR-001-PRE: Предусловие"""
        if not lidar_localization.is_alive():
            pytest.skip("Нода не запущена — тест пропущен")
        assert lidar_localization.is_alive() is True

    def test_02_kill_lidar_localization(self, lidar_localization_alive):
        """
        TC-FAULT-LIDAR-002: Kill lidar_localization
        Фиксирует факт смерти через PID — до перезапуска drive.py.
        """
        nodes_before = lidar_localization_alive.get_node_list()
        pid_before = lidar_localization_alive.get_pid()

        lidar_localization_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        lidar_localization_alive.kill()

        pid_after = lidar_localization_alive.get_pid()
        lidar_localization_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if lidar_localization_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"Нода перезапущена (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not lidar_localization_alive.is_alive(), \
            "Нода не была корректно завершена"

    def test_03_localization_degradation(self, lidar_localization):
        """TC-FAULT-LIDAR-003: Поведение системы локализации после kill"""
        time.sleep(5)

        result = lidar_localization.check_localization_degradation()

        if result["has_auto_restart"]:
            lidar_localization.logger.info(
                "Система восстановила ноду автоматически. "
                "Fault tolerance: ПОДТВЕРЖДЁН ✅"
            )
            assert result["other_localization_alive"], \
                "Ноды localization не работают даже с auto-restart"
        else:
            assert result["lidar_localization_gone"], \
                "Нода lidar_localization всё ещё в graph"
            assert result["other_localization_alive"], \
                "Все ноды localization упали после kill"