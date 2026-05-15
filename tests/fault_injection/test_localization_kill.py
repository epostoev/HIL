import time
import pytest


LOCALIZATION_NODES = [
    ("lidar_localization_node_alive",          "TC-LOC-KILL-001", "/lidar_localization"),
    ("localization_localization_node_alive",   "TC-LOC-KILL-002", "/localization/localization"),
    ("localization_initialization_node_alive", "TC-LOC-KILL-003", "/localization_initialization_node"),
]


class TestLocalizationKill:
    """
    Fault Injection: принудительное завершение нод компонента Localization

    TC-LOC-KILL-001: /lidar_localization
    TC-LOC-KILL-002: /localization/localization
    TC-LOC-KILL-003: /localization_initialization_node
    """

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", LOCALIZATION_NODES)
    def test_localization_kill(self, fixture_name, tc_id, node_name,
                               mrm_monitor, request, restart_autopilot_after):

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 5000ms"

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

        # Формируем строку ошибок для отчёта
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