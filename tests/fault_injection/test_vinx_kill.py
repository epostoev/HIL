import time
import pytest


class TestVinxKill:
    """
    Fault Injection: принудительное завершение /visualization/vinx

    TC-FAULT-VINX-001: Предусловие — нода активна
    TC-FAULT-VINX-002: Kill — нода исчезает из ROS graph
    TC-FAULT-VINX-003: Деградация визуализации — смежные ноды живы
    """

    def test_01_precondition_node_running(self, vinx_node):
        """TC-FAULT-VINX-001-PRE: Предусловие"""
        if not vinx_node.is_alive():
            pytest.skip("Нода /visualization/vinx не запущена — тест пропущен")
        assert vinx_node.is_alive() is True

    def test_02_kill_vinx_node(self, vinx_node_alive):
        """TC-FAULT-VINX-002: Kill vinx_node"""
        nodes_before = vinx_node_alive.get_node_list()
        pid_before = vinx_node_alive.get_pid()

        vinx_node_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        vinx_node_alive.kill()

        pid_after = vinx_node_alive.get_pid()
        vinx_node_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if vinx_node_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"Нода перезапущена (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not vinx_node_alive.is_alive(), \
            "Нода не была корректно завершена"

    def test_03_visualization_degradation(self, vinx_node):
        """
        TC-FAULT-VINX-003: Поведение системы визуализации после kill.
        Vinx — некритичная нода, остальная система должна работать.
        """
        time.sleep(5)

        result = vinx_node.check_visualization_degradation()

        if result["has_auto_restart"]:
            vinx_node.logger.info(
                "Система восстановила ноду автоматически. "
                "Fault tolerance: ПОДТВЕРЖДЁН ✅"
            )
            assert result["other_viz_alive"], \
                "Ноды visualization не работают даже с auto-restart"
        else:
            assert result["vinx_gone"], \
                "Нода vinx всё ещё в graph"
            assert result["other_viz_alive"], \
                "Все ноды visualization упали после kill"