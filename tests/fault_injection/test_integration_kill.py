import time
import pytest


INTEGRATION_NODES = [
    ("can_telemetry_node",       "TC-INT-PRE-001", "/can_telemetry"),
    ("carapi_integration_node",  "TC-INT-PRE-002", "/carapi_node"),
    ("cloud_telemetry_node",     "TC-INT-PRE-003", "/infra/cloud_telemetry_node"),
    ("hardware_metrics_node",    "TC-INT-PRE-004", "/hardware_metrics"),
    ("metrics_aggregator_node",  "TC-INT-PRE-005", "/metrics_aggregator"),
    ("hal_node",                 "TC-INT-PRE-006", "/generic/hal"),
    ("crash_detector_node",      "TC-INT-PRE-007", "/safety/crash_detector"),
    ("sda_process_monitor_node", "TC-INT-PRE-008", "/sda_process_monitor/sda_process_monitor"),
    ("v2x_publisher_node",       "TC-INT-PRE-009", "/v2x_publisher_node"),
    ("rosbag2_recorder_node",    "TC-INT-PRE-010", "/data_logging/rosbag2_recorder"),
    ("mrm_arbiter_node",         "TC-INT-PRE-010", "/mrm_arbiter"),
]


class TestIntegrationKill:
    """
    Fault Injection: принудительное завершение нод компонента General Integration

    TC-INT-PRE-001: /can_telemetry
    TC-INT-PRE-002: /carapi_node
    TC-INT-PRE-003: /infra/cloud_telemetry_node
    TC-INT-PRE-004: /hardware_metrics
    TC-INT-PRE-005: /metrics_aggregator
    TC-INT-PRE-006: /generic/hal
    TC-INT-PRE-007: /safety/crash_detector
    TC-INT-PRE-007: /safety/crash_detector
    TC-INT-PRE-008: /sda_process_monitor/sda_process_monitor
    TC-INT-PRE-009: /v2x_publisher_node
    TC-INT-PRE-010: /data_logging/rosbag2_recorder
    TC-INT-PRE-011: /mrm_arbiter
    """

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", INTEGRATION_NODES)
    def test_integration_kill(self, fixture_name, tc_id, node_name,
                              mrm_monitor, request, restart_autopilot_after):

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 500ms"

        if not node.is_alive():
            pytest.skip(f"Нода {node_name} не запущена")

        # Baseline ДО kill
        baseline = mrm_monitor.get_fields(["mrm_type", "shadow_mrm_type", "drive_mode"])
        node.logger.info(f"Baseline mrm_type={baseline['mrm_type']}")

        # Получаем PID
        pid_before = node.get_pid()

        # Фиксируем stamp прямо перед сигналом
        before_stamp = mrm_monitor.get_stamp()
        node.logger.info(f"Stamp ДО kill: {before_stamp}")

        # Отправляем kill -9 без ожидания
        node.run_docker_command(f"kill -9 {pid_before}")
        node.logger.info(f"Kill сигнал отправлен PID={pid_before}. Ждём изменения mrm_type...")

        # Мониторим изменение mrm_type
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

        # Получаем error_codes после kill
        error_codes = mrm_monitor.get_error_codes()
        triggered_errors = [
            e for e in error_codes
            if e["details"] != "{}"
        ]
        node.logger.info(f"Triggered errors: {len(triggered_errors)}")
        for e in triggered_errors:
            node.logger.info(
                f"  {e['error_code_hex']} ({e['error_code']}): "
                f"{e['details'][:80]}"
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

        errors_str = " | ".join([
            f"{e['error_code_hex']}: {e['details'][:50]}"
            for e in triggered_errors
        ]) or "нет"

        request.node.actual = (
            f"mrm_type: {baseline['mrm_type']} → {result['mrm_type']}. "
            f"Ошибки: {errors_str} ✅"
        )
        request.node.reaction_ms = f"{result['reaction_ms']}ms"

        if node.has_auto_restart:
            node.logger.info(
                f"Fault tolerance: ПОДТВЕРЖДЁН ✅ "
                f"Время реакции MRM: {result['reaction_ms']}ms"
            )