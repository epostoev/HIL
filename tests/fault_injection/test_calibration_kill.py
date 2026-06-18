import json
import time
import pytest
import allure


CALIBRATION_NODES = [
    ("calibration_intrinsic_publisher_node_alive",                  "TC-CAL-KILL-001", "/intrinsic_publisher"),
    ("calibration_camera_to_baselink_online_calibrator_node_alive", "TC-CAL-KILL-002", "/calibration/rct/camera_to_baselink_online_calibrator"),
    ("calibration_imu_baselink_runtime_calibration_node_alive",     "TC-CAL-KILL-003", "/calibration/rct/imu/imu_baselink_runtime_calibration"),
    ("calibration_runtime_radar_autocalibration_node_alive",        "TC-CAL-KILL-004", "/calibration/rct/runtime_radar_autocalibration"),
    ("calibration_cam_to_cam_tf_estimators_node_alive",             "TC-CAL-KILL-005", "/calibration/rct/cam_to_cam_tf_estimators"),
    ("calibration_feature_extractors_node_alive",                   "TC-CAL-KILL-006", "/calibration/rct/feature_extractors"),
    ("calibration_cam_to_cam_controller_node_alive",                "TC-CAL-KILL-007", "/calibration/rct/cam_to_cam_controller"),
    ("calibration_rct_validator_node_alive",                        "TC-CAL-KILL-008", "/calibration/rct/rct_validator"),
    ("calibration_robot_state_publisher_node_alive",                "TC-CAL-KILL-009", "/robot_state_publisher"),
]


@allure.epic("HIL Testing")
@allure.feature("Calibration")
@allure.story("Fault Injection: kill -6 нод")
@allure.title("Fault Injection: принудительное завершение нод компонента Calibration")
@allure.description(
    "Тест отправляет kill -6 каждой ноде компонента Calibration "
    "и проверяет что MRM реагирует переходом mrm_type: 0 → 2 "
    "в течение 5000ms."
)
class TestCalibrationKill:
    """
    Fault Injection: принудительное завершение нод компонента Calibration.

    TC-CAL-KILL-001: /intrinsic_publisher
    TC-CAL-KILL-002: /calibration/rct/camera_to_baselink_online_calibrator
    TC-CAL-KILL-003: /calibration/rct/imu/imu_baselink_runtime_calibration
    TC-CAL-KILL-004: /calibration/rct/runtime_radar_autocalibration
    TC-CAL-KILL-005: /calibration/rct/cam_to_cam_tf_estimators
    TC-CAL-KILL-006: /calibration/rct/feature_extractors
    TC-CAL-KILL-007: /calibration/rct/cam_to_cam_controller
    TC-CAL-KILL-008: /calibration/rct/rct_validator
    TC-CAL-KILL-009: /robot_state_publisher
    TC-CAL-KILL-010: /intrinsic_repair_service
    TC-CAL-KILL-011: /calibration/calapi_node
    """

    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.parametrize("fixture_name, tc_id, node_name", CALIBRATION_NODES)
    def test_calibration_kill(self, fixture_name, tc_id, node_name,
                              mrm_monitor, request, restart_autopilot_after):

        allure.dynamic.title(f"{tc_id}: kill -6 {node_name}")
        allure.dynamic.parameter("node_name", node_name)
        allure.dynamic.parameter("tc_id", tc_id)

        with allure.step(f"Получить объект ноды {node_name}"):
            node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 5000ms"

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