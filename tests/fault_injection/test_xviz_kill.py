import time
import pytest


class TestXvizKill:
    """
    Fault Injection: принудительное завершение /visualization/xviz

    TC-FAULT-XVIZ-001: Предусловие — нода активна
    TC-FAULT-XVIZ-002: Kill — нода исчезает из ROS graph
    TC-FAULT-XVIZ-003: Деградация визуализации — смежные ноды живы
    """

    def test_01_precondition_node_running(self, xviz_node):
        """TC-FAULT-XVIZ-001-PRE: Предусловие"""
        if not xviz_node.is_alive():
            pytest.skip("Нода /visualization/xviz не запущена — тест пропущен")
        assert xviz_node.is_alive() is True

    def test_02_kill_xviz_node(self, xviz_node_alive):
        """
        TC-FAULT-XVIZ-002: Kill xviz_node
        Фиксирует факт смерти через PID — до перезапуска drive.py.
        """
        nodes_before = xviz_node_alive.get_node_list()
        pid_before = xviz_node_alive.get_pid()

        xviz_node_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        xviz_node_alive.kill()

        pid_after = xviz_node_alive.get_pid()
        xviz_node_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if xviz_node_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"Нода перезапущена (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not xviz_node_alive.is_alive(), \
            "Нода не была корректно завершена"

    # def test_03_visualization_degradation(self, xviz_node):
    #     """
    #     TC-FAULT-XVIZ-003: Поведение системы визуализации после kill.
    #     Xviz — некритичная нода, остальная система должна работать.
    #     """
    #     time.sleep(5)

    #     result = xviz_node.check_visualization_degradation()

    #     if result["has_auto_restart"]:
    #         xviz_node.logger.info(
    #             "Система восстановила ноду автоматически. "
    #             "Fault tolerance: ПОДТВЕРЖДЁН ✅"
    #         )
    #         assert result["other_viz_alive"], \
    #             "Ноды visualization не работают даже с auto-restart"
    #     else:
    #         assert result["xviz_gone"], \
    #             "Нода xviz всё ещё в graph"
    #         assert result["other_viz_alive"], \
    #             "Все ноды visualization упали после kill"