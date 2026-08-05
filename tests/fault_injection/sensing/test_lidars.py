"""
Fault Injection: отказ лидара через физическое реле (HW fault injection).

НЕ ЗАПУСКАЛОСЬ на стенде — черновик для ручного прогона (нет доступа к
HIL-стенду с этой машины).

Контекст (со слов инженера стенда, 2026-08-05):
- Реле 192.168.1.120:80 (tests/fault_injection/sensing/control_relay.py)
  отключает питание лидаров. (Более раннее предположение в
  test_camera.py, что это реле камеры, было неверным.)
- Коды ошибок "нет данных от лидара": 131599, 197135, 262671, 328207 —
  по одному на лидар, соответствие код -> конкретный физический лидар
  пока не уточнено.
- Код 263183 — "нет данных о загрязнённости лидаров" (contamination).
- Этот файл проверяет ПЕРВЫЙ шаг: один лидар, код 131599.

ОТКРЫТЫЕ ВОПРОСЫ (см. также PLACEHOLDER-комментарии ниже):
- Верен ли выбор именно 131599 для этого теста, или это код другого
  лидара? Нужно подтверждение.
- Нужен ли precondition "жив ли лидар" перед тестом — в
  framework/sensing_nodes.py нет отдельного класса для лидар-драйвера
  (в отличие от RadarDriverNode/UbloxDriverNode), поэтому такой проверки
  здесь нет.
- Таймаут 10s взят по аналогии с kill-тестами (wait_for_mrm_type_change) —
  для физического HW-отказа реакция может быть другой.
"""
import allure
import pytest

from fault_injection.sensing.control_relay import relay_on, relay_off


LIDAR_NO_DATA_ERROR_CODE = 131599  # PLACEHOLDER: требует подтверждения


@allure.epic("HIL Testing")
@allure.feature("Sensing")
@allure.story("Fault Injection: HW отказ лидара через реле")
@allure.title("Fault Injection: отключение питания лидара через реле")
@allure.description(
    "Тест отключает питание лидара физическим реле (192.168.1.120) и "
    "проверяет, что в /safety/mrm_request появляется error_code "
    f"{LIDAR_NO_DATA_ERROR_CODE} ('нет данных от лидара')."
)
class TestLidarRelay:

    @allure.severity(allure.severity_level.BLOCKER)
    def test_lidar_power_cut_triggers_no_data_error(self, mrm_monitor, request):
        """
        TC-SENSING-RELAY-LIDAR-001 (черновик, не запускался).
        """
        request.node.expected = (
            f"В /safety/mrm_request появляется error_code "
            f"0x{LIDAR_NO_DATA_ERROR_CODE:08X} ({LIDAR_NO_DATA_ERROR_CODE})"
        )

        with allure.step("Снять baseline: mrm_type + активные error_codes"):
            baseline = mrm_monitor.get_fields(
                ["mrm_type", "shadow_mrm_type", "drive_mode"]
            )
            baseline_codes = {e["error_code"] for e in mrm_monitor.get_error_codes()}
            allure.attach(
                f"mrm_type: {baseline['mrm_type']}\n"
                f"Активные error_codes: {sorted(baseline_codes)}",
                name="Baseline",
                attachment_type=allure.attachment_type.TEXT,
            )
            # Защита от "грязного" старта: если этот же код уже активен
            # ДО инъекции (как было с cloud_builder_node 2026-08-05),
            # тест не сможет доказать причинно-следственную связь.
            if LIDAR_NO_DATA_ERROR_CODE in baseline_codes:
                pytest.skip(
                    f"error_code {LIDAR_NO_DATA_ERROR_CODE} уже активен "
                    f"до инъекции отказа — стенд не в чистом состоянии"
                )

        with allure.step("Зафиксировать timestamp ДО отключения реле"):
            before_stamp = mrm_monitor.get_stamp()

        try:
            with allure.step("Отключить питание лидара (relay_off)"):
                response = relay_off()
                allure.attach(
                    f"status_code={response.status_code}",
                    name="Relay OFF response",
                    attachment_type=allure.attachment_type.TEXT,
                )

            with allure.step(
                f"Ожидать появления error_code {LIDAR_NO_DATA_ERROR_CODE} (timeout=10s)"
            ):
                result = mrm_monitor.wait_for_error_code(
                    error_code=LIDAR_NO_DATA_ERROR_CODE,
                    before_stamp=before_stamp,
                    timeout=10.0,
                    poll_interval=0.05,
                )
                allure.attach(
                    f"success:     {result['success']}\n"
                    f"reaction_ms: {result['reaction_ms']}ms\n"
                    f"details:     {result['details']}",
                    name="Результат ожидания error_code",
                    attachment_type=allure.attachment_type.TEXT,
                )

            with allure.step("Assert: error_code появился"):
                assert result["success"], (
                    f"error_code {LIDAR_NO_DATA_ERROR_CODE} не появился "
                    f"в /safety/mrm_request за 10s после отключения питания лидара"
                )

            request.node.actual = (
                f"error_code {result['error_code_hex']} появился, "
                f"reaction={result['reaction_ms']}ms"
            )
            request.node.reaction_ms = f"{result['reaction_ms']}ms"

        finally:
            with allure.step("Восстановить питание лидара (relay_on)"):
                # В finally — чтобы стенд не остался обесточенным даже
                # при падении ассертов выше.
                relay_on()
