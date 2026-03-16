import time
import pytest


class TestTrajectoryPlannerKill:
    """
    Fault Injection: принудительное завершение
    /planning/trajectory_planner_node

    TC-FAULT-TRAJ-001: Предусловие — нода активна
    TC-FAULT-TRAJ-002: Kill — нода исчезает из ROS graph
    TC-FAULT-TRAJ-003: Деградация планирования — смежные ноды живы
    """

    def test_01_precondition_node_running(self, trajectory_planner):
        """TC-FAULT-TRAJ-001-PRE: Предусловие"""
        if not trajectory_planner.is_alive():
            pytest.skip("Нода не запущена — тест пропущен")
        assert trajectory_planner.is_alive() is True

    def test_02_kill_trajectory_planner(self, trajectory_planner_alive):
        """
        TC-FAULT-TRAJ-002: Kill trajectory_planner_node
        Фиксирует факт смерти через PID — до перезапуска drive.py.
        """
        nodes_before = trajectory_planner_alive.get_node_list()
        pid_before = trajectory_planner_alive.get_pid()

        trajectory_planner_alive.logger.info(
            f"Состояние ДО: нод={len(nodes_before)}, PID={pid_before}"
        )

        trajectory_planner_alive.kill()

        pid_after = trajectory_planner_alive.get_pid()
        trajectory_planner_alive.logger.info(
            f"PID до: {pid_before} → PID после: {pid_after}"
        )

        if trajectory_planner_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал вообще"
            pytest.xfail(
                f"drive.py перезапустил ноду (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not trajectory_planner_alive.is_alive(), \
            "Нода не была корректно завершена"

    # def test_03_planning_degradation(self, trajectory_planner):
    #     """TC-FAULT-TRAJ-003: Поведение системы после kill"""
    #     time.sleep(5)

    #     result = trajectory_planner.check_planning_degradation()

    #     if result["has_auto_restart"]:
    #         trajectory_planner.logger.info(
    #             "Система восстановила ноду автоматически. "
    #             "Fault tolerance: ПОДТВЕРЖДЁН ✅"
    #         )
    #         assert result["other_planning_alive"], \
    #             "Ноды planning не работают даже с auto-restart"
    #     else:
    #         assert result["trajectory_planner_gone"], \
    #             "Нода trajectory_planner всё ещё в graph"
    #         assert result["other_planning_alive"], \
    #             "Все ноды planning упали после kill"

    def test_04_control_system_errors_after_kill(
        self, trajectory_planner, control_monitor  # ← добавить
    ):
        """
        TC-FAULT-TRAJ-004: Мониторинг /control/system после kill

        После гибели trajectory_planner_node в топике /control/system
        должен появиться флаг trajectory_has_error: true.

        Это подтверждает что система корректно детектирует отказ ноды.
        """
        time.sleep(5)

        results = trajectory_planner.check_control_system_errors(
            trajectory_planner.EXPECTED_ERRORS,
            control_monitor  # ← передаём монитор
        )

        trajectory_planner.logger.info(
            f"control_state: {results.get('control_state')}, "
            f"ad_active: {results.get('ad_active')}"
        )

        # Проверяем каждый ожидаемый флаг ошибки
        for field, data in results.items():
            if field in ("control_state", "ad_active"):
                continue
            assert data["ok"], (
                f"Флаг '{field}' не выставился корректно: "
                f"ожидалось='{data['expected']}', "
                f"получено='{data['actual']}'"
            )

        trajectory_planner.logger.info(
            "Все флаги ошибок выставлены корректно ✅"
        )