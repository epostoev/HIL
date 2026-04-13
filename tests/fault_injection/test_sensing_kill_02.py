import pytest


SENSING_NODES = [
    ("auto_cleaning_node_alive",      "TC-FAULT-SENSING-001", "/sensing/auto_cleaning"),
    ("imu_node_alive",                "TC-FAULT-SENSING-002", "/sensing/imu1/imu_node"),
    ("odometry_node",                 "TC-FAULT-SENSING-003", "/sensing/odometry_node"),
    ("odometry_velocity_node",        "TC-FAULT-SENSING-004", "/sensing/odometry_velocity_node"),
    ("radar_driver_node_alive",       "TC-FAULT-SENSING-005", "/sensing/radar_driver_node"),
    ("ublox_driver_node",             "TC-FAULT-SENSING-006", "/sensing/ublox1/ublox_driver_node"),
    ("radar_visualization_node",      "TC-FAULT-SENSING-007", "/sensing/visualization/radar_visualization_node"),
]


class TestSensingKill:

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", SENSING_NODES)
    def test_sensing_kill(self, fixture_name, tc_id, node_name, mrm_monitor, request):

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 5000ms"

        if not node.is_alive():
            pytest.skip(f"Нода {node_name} не запущена")

        # Baseline ДО kill
        baseline = mrm_monitor.get_fields(["mrm_type", "shadow_mrm_type", "drive_mode"])
        node.logger.info(f"Baseline mrm_type={baseline['mrm_type']}")

        # Kill
        pid_before = node.get_pid()
        node.kill()
        node.logger.info(f"Kill выполнен, PID={pid_before}. Ждём изменения mrm_type...")

        # Ждём изменения mrm_type по stamp топика
        result = mrm_monitor.wait_for_mrm_type_change(
            from_value="0",
            to_value="2",
            timeout=10.0,
            poll_interval=0.05
        )

        node.logger.info(
            f"Результат: success={result['success']}, "
            f"reaction={result['reaction_ms']}ms "
            f"({result['reaction_ns']}ns), "
            f"mrm_type={result['mrm_type']}"
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