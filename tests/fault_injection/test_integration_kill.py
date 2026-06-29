import json
import time
import pytest
import allure


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
    # ("rosbag2_recorder_node",    "TC-INT-PRE-010", "/data_logging/rosbag2_recorder"),
    # ("mrm_arbiter_node",         "TC-INT-PRE-011", "/mrm_arbiter"),
]


class TestIntegrationKill:

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", INTEGRATION_NODES)
    def test_integration_kill(self, fixture_name, tc_id, node_name,
                              mrm_monitor, request, restart_autopilot_after):

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 500ms"

        if not node.is_alive():
            pytest.skip(f"Нода {node_name} не запущена")

        with allure.step("Снять baseline: mrm_type, shadow_mrm_type, drive_mode"):
            baseline = mrm_monitor.get_fields(["mrm_type", "shadow_mrm_type", "drive_mode"])
            node.logger.info(f"Baseline mrm_type={baseline['mrm_type']}")
            allure.attach(
                f"mrm_type:        {baseline['mrm_type']}\n"
                f"shadow_mrm_type: {baseline['shadow_mrm_type']}\n"
                f"drive_mode:      {baseline['drive_mode']}",
                name="Baseline",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Получить PID ноды {node_name}"):
            pid_before = node.get_pid()
            node.logger.info(f"PID={pid_before}")
            allure.attach(
                str(pid_before),
                name="PID до kill",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Зафиксировать timestamp перед kill"):
            before_stamp = mrm_monitor.get_stamp()
            node.logger.info(f"Stamp ДО kill: {before_stamp}")

        with allure.step(f"Отправить kill -6 PID={pid_before}"):
            node.run_docker_command(f"kill -6 {pid_before}")
            node.logger.info(
                f"kill -6 отправлен PID={pid_before}. "
                f"Ждём изменения mrm_type..."
            )

        with allure.step("Ожидать mrm_type: 0 → 2 (timeout=10s)"):
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
            allure.attach(
                f"success:      {result['success']}\n"
                f"mrm_type:     {result['mrm_type']}\n"
                f"reaction_ms:  {result['reaction_ms']}ms\n"
                f"reaction_ns:  {result['reaction_ns']}ns",
                name="Результат ожидания MRM",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Собрать error_codes после kill"):
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
            errors_text = "\n".join([
                f"{e['error_code_hex']} ({e['error_code']}): {e['details'][:80]}"
                for e in triggered_errors
            ]) or "нет"
            allure.attach(
                errors_text,
                name=f"Triggered errors ({len(triggered_errors)})",
                attachment_type=allure.attachment_type.TEXT,
            )
            # Сохраняем error_codes в файл и прикрепляем к отчёту
            log_path = f"/tmp/error_codes_{node_name.replace('/', '_')}.json"
            with open(log_path, "w") as f:
                json.dump(triggered_errors, f, indent=2, ensure_ascii=False)
            allure.attach.file(
                log_path,
                name=f"error_codes_{node_name}",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Проверить наличие авторестарта ноды (fault tolerance)"):
            time.sleep(3)
            if node.is_alive():
                node.has_auto_restart = True
                node.logger.info(
                    "drive.py перезапустил ноду. "
                    "Fault tolerance: ПОДТВЕРЖДЁН ✅"
                )
                allure.attach(
                    f"Нода {node_name} перезапущена автоматически\n"
                    "Fault Tolerance: ПОДТВЕРЖДЁН ✅",
                    name="Fault Tolerance",
                    attachment_type=allure.attachment_type.TEXT,
                )
            else:
                allure.attach(
                    f"Авторестарт {node_name} не обнаружен за 3 секунды",
                    name="Fault Tolerance",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step("Проверить assert: mrm_type изменился на '2'"):
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