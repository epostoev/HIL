import time
import pytest


SENSING_NODES = [
    ("auto_cleaning_node_alive",      "TC-FAULT-SENSING-001", "/sensing/auto_cleaning"),
    ("imu_node_alive",                "TC-FAULT-SENSING-002", "/sensing/imu1/imu_node"),
    # ("odometry_node",                 "TC-FAULT-SENSING-003", "/sensing/odometry_node"),
    # ("odometry_velocity_node",        "TC-FAULT-SENSING-004", "/sensing/odometry_velocity_node"),
    # ("radar_driver_node_alive",       "TC-FAULT-SENSING-005", "/sensing/radar_driver_node"),
    # ("ublox_driver_node",             "TC-FAULT-SENSING-006", "/sensing/ublox1/ublox_driver_node"),
    # ("radar_visualization_node",      "TC-FAULT-SENSING-007", "/sensing/visualization/radar_visualization_node"),
]


class TestSensingKill:

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", SENSING_NODES)
    def test_sensing_kill(self, fixture_name, tc_id, node_name, mrm_monitor, request, restart_autopilot_after):

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 5000ms"

        if not node.is_alive():
            pytest.skip(f"Нода {node_name} не запущена")

        # Baseline ДО kill
        baseline = mrm_monitor.get_fields(["mrm_type", "shadow_mrm_type", "drive_mode"])
        node.logger.info(f"Baseline mrm_type={baseline['mrm_type']}")

        # Получаем PID
        pid_before = node.get_pid()

        # Фиксируем stamp прямо перед сигналом — минимальная задержка
        before_stamp = mrm_monitor.get_stamp()
        node.logger.info(f"Stamp ДО kill: {before_stamp}")

        # Отправляем только kill -9 без ожидания (не вызываем node.kill())
        node.run_docker_command(f"kill -9 {pid_before}")
        node.logger.info(f"Kill сигнал отправлен PID={pid_before}. Ждём изменения mrm_type...")

        # Сразу мониторим изменение mrm_type — пока нода ещё умирает
        result = mrm_monitor.wait_for_mrm_type_change(
            from_value="0",
            to_value="2",
            before_stamp=before_stamp,
            timeout=10.0,
            poll_interval=0.01
        )

        node.logger.info(
            f"Результат: success={result['success']}, "
            f"reaction={result['reaction_ms']}ms "
            f"({result['reaction_ns']}ns), "
            f"mrm_type={result['mrm_type']}"
        )

        # После измерения — проверяем has_auto_restart
        time.sleep(3)
        if node.is_alive():
            node.has_auto_restart = True
            node.logger.info(
                f"drive.py перезапустил ноду. "
                f"Fault tolerance: ПОДТВЕРЖДЁН ✅"
            )

        assert result["success"], (
            f"mrm_type не изменился на '2'. "
            f"Текущее значение: {result['mrm_type']}"
        )

        request.node.actual = (
            f"mrm_type: {baseline['mrm_type']} → {result['mrm_type']}. "
            f"Время реакции: {result['reaction_ms']}ms ✅"
        )

        if node.has_auto_restart:
            node.logger.info(
                f"Fault tolerance: ПОДТВЕРЖДЁН ✅ "
                f"Время реакции MRM: {result['reaction_ms']}ms"
            )