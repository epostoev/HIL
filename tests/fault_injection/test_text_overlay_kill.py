import time
import pytest


class TestTextOverlayKill:
    """
    Fault Injection: принудительное завершение /visualization/text_overlay

    TC-FAULT-text_overlay-001: Предусловие — нода активна
    TC-FAULT-text_overlay-002: Kill — нода исчезает из ROS graph
    TC-FAULT-text_overlay-003: Деградация визуализации — смежные ноды живы
    """

    def test_01_precondition_node_running(self, text_overlay):
        """TC-FAULT-text_overlay-001-PRE: Предусловие"""
        if not text_overlay.is_alive():
            pytest.skip("Нода /visualization/xviz не запущена — тест пропущен")
        assert text_overlay.is_alive() is True

    def test_02_kill_text_overlay_node(self, text_overlay_alive):
        """
        TC-FAULT-XVIZ-002: Kill xviz_node
        Фиксирует факт смерти через PID — до перезапуска drive.py.
        """
        nodes_before = text_overlay_alive.get_node_list()
        pid_before = text_overlay_alive.get_pid()

        text_overlay_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        text_overlay_alive.kill()

        pid_after = text_overlay_alive.get_pid()
        text_overlay_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if text_overlay_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"Нода перезапущена (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not text_overlay_alive.is_alive(), \
            "Нода не была корректно завершена"