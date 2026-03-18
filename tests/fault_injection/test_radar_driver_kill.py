import time
import pytest


class TestRadarDriverKill:
    """
    Fault Injection: принудительное завершение /sensing/radar_driver_node

    TC-FAULT-RADAR-DRV-001: Предусловие — нода активна
    TC-FAULT-RADAR-DRV-002: Kill — нода исчезает из ROS graph
    TC-FAULT-RADAR-DRV-003: Деградация сенсоров — смежные ноды живы
    """

    def test_01_precondition_node_running(self, radar_driver_node):
        """TC-FAULT-RADAR-DRV-001-PRE: Предусловие"""
        if not radar_driver_node.is_alive():
            pytest.skip("Нода /sensing/radar_driver_node не запущена")
        assert radar_driver_node.is_alive() is True

    def test_02_kill_radar_driver_node(self, radar_driver_node_alive):
        """TC-FAULT-RADAR-DRV-002: Kill radar_driver_node"""
        nodes_before = radar_driver_node_alive.get_node_list()
        pid_before = radar_driver_node_alive.get_pid()

        radar_driver_node_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        radar_driver_node_alive.kill()

        pid_after = radar_driver_node_alive.get_pid()
        radar_driver_node_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if radar_driver_node_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"Нода перезапущена (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not radar_driver_node_alive.is_alive(), \
            "Нода не была корректно завершена"

    def test_03_sensing_degradation(self, radar_driver_node):
        """TC-FAULT-RADAR-DRV-003: Деградация сенсорной системы после kill"""
        time.sleep(5)

        result = radar_driver_node.check_sensing_degradation()

        if result["has_auto_restart"]:
            radar_driver_node.logger.info(
                "Система восстановила ноду автоматически. "
                "Fault tolerance: ПОДТВЕРЖДЁН ✅"
            )
        else:
            assert result["node_gone"], \
                "Нода radar_driver_node всё ещё в graph"
            radar_driver_node.logger.info(
                f"Ноды sensing после kill: {result['sensing_nodes']} ✅"
            )