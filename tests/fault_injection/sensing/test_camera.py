"""
Fault Injection: отказ камеры через физическое реле (HW fault injection).

ВАЖНО: этот файл — черновик, подготовленный статическим анализом.
Тесты НЕ были запущены (нет доступа к HIL-стенду с этой машины).
Требуется ручной прогон и проверка перед включением в регресс.

Ссылки на референс:
- tests/fault_injection/test_sensing_kill.py — стиль ассертов через
  MrmRequestMonitor (SW fault injection через kill, не HW-реле).
- tests/fault_injection/sensing/control_relay.py — HTTP API управления
  физическим реле (единственное реле в проекте на данный момент,
  привязано к IP 192.168.1.120, назначение — предположительно камера,
  не подтверждено документацией стенда).
"""
import allure
import pytest

from fault_injection.sensing.control_relay import relay_on, relay_off


# TC-SENSING-RELAY-CAM-001
@allure.epic("HIL Testing")
@allure.feature("Sensing")
@allure.story("Fault Injection: HW отказ через реле (камера)")
@allure.title("Fault Injection: отключение питания камеры через реле")
@allure.description(
    "Тест отключает питание камеры физическим реле (control_relay.relay_off) "
    "и проверяет, что MRM реагирует переходом mrm_type: 0 -> 2 в течение "
    "заданного таймаута. Питание восстанавливается в finally независимо "
    "от результата ассертов."
)
class TestCameraRelay:

    @allure.severity(allure.severity_level.BLOCKER)
    def test_camera_power_cut_triggers_mrm(
        self, mrm_monitor, camera_decoder_node_alive, request
    ):
        """
        TC-SENSING-RELAY-CAM-001.

        Предусловия:
        - camera_decoder_node_alive пропускает тест (pytest.skip), если
          нода /sensing/camera_decoder не в ROS graph — см.
          tests/conftest.py fixture camera_decoder_node_alive.
        - mrm_monitor — session-scoped autouse fixture (tests/conftest.py,
          строки ~1676-1683), общий на весь сьют, отдельный instance
          НЕ создаётся.

        НЕ ПРОВЕРЕНО (открытые вопросы, см. отчёт):
        - Реле по IP 192.168.1.120 действительно управляет питанием именно
          камеры (не подтверждено документацией/схемой стенда).
        - Подстрока "camera" в поле details ошибки MRM — предположение,
          нужно сверить с реальным выводом `ros2 topic echo` на стенде.
        """
        node = camera_decoder_node_alive
        request.node.expected = (
            "mrm_type: 0 -> 2 после отключения питания камеры (< 10000ms)"
        )

        with allure.step("Снять baseline: mrm_type, shadow_mrm_type, drive_mode"):
            baseline = mrm_monitor.get_fields(
                ["mrm_type", "shadow_mrm_type", "drive_mode"]
            )
            node.logger.info(f"Baseline mrm_type={baseline['mrm_type']}")
            allure.attach(
                f"mrm_type:        {baseline['mrm_type']}\n"
                f"shadow_mrm_type: {baseline['shadow_mrm_type']}\n"
                f"drive_mode:      {baseline['drive_mode']}",
                name="Baseline",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Зафиксировать timestamp ДО отключения реле"):
            # Критично: сравниваем новое сообщение именно с этим stamp,
            # а не с "текущим на момент проверки" — иначе можно словить
            # ложный pass на сообщении, оставшемся от предыдущего теста
            # (mrm_monitor -- один persistent инстанс на весь сьют).
            before_stamp = mrm_monitor.get_stamp()
            node.logger.info(f"Stamp ДО relay_off: {before_stamp}")

        try:
            with allure.step("Отключить питание камеры (relay_off)"):
                response = relay_off()
                node.logger.info(
                    f"relay_off() HTTP status: {response.status_code}"
                )
                allure.attach(
                    f"status_code={response.status_code}",
                    name="Relay OFF response",
                    attachment_type=allure.attachment_type.TEXT,
                )

            with allure.step("Ожидать mrm_type: 0 -> 2 (timeout=10s)"):
                result = mrm_monitor.wait_for_mrm_type_change(
                    from_value="0",
                    to_value="2",
                    before_stamp=before_stamp,
                    timeout=10.0,
                    poll_interval=0.05,
                )
                node.logger.info(
                    f"success={result['success']}, "
                    f"reaction={result['reaction_ms']}ms "
                    f"({result['reaction_ns']}ns), "
                    f"mrm_type={result['mrm_type']}"
                )
                allure.attach(
                    f"success:      {result['success']}\n"
                    f"mrm_type:     {result['mrm_type']}\n"
                    f"reaction_ms:  {result['reaction_ms']}ms",
                    name="Результат ожидания MRM",
                    attachment_type=allure.attachment_type.TEXT,
                )

            with allure.step("Собрать error_codes после отказа"):
                error_codes = mrm_monitor.get_error_codes()
                triggered = [
                    e for e in error_codes if e["details"] not in ("{}", "")
                ]
                # ОТКРЫТЫЙ ВОПРОС: подтверждённого поля sensor_id/severity
                # в схеме /safety/mrm_request не найдено нигде в кодовой базе
                # (см. отчёт, п. Step 1.3) -- матчим по подстроке в details.
                camera_errors = [
                    e for e in triggered if "camera" in e["details"].lower()
                ]
                allure.attach(
                    "\n".join(
                        f"{e['error_code_hex']} ({e['error_code']}): "
                        f"{e['details'][:80]}"
                        for e in triggered
                    ) or "нет",
                    name=f"Triggered errors ({len(triggered)})",
                    attachment_type=allure.attachment_type.TEXT,
                )

            with allure.step("Assert: mrm_type изменился на '2'"):
                assert result["success"], (
                    f"mrm_type не изменился на '2' после отключения питания "
                    f"камеры. Текущее значение: {result['mrm_type']}"
                )

            with allure.step(
                "Assert: в error_codes присутствует запись, связанная с камерой"
            ):
                assert camera_errors, (
                    f"Ожидалась запись об ошибке камеры в error_codes, "
                    f"получено: {triggered}"
                )

            request.node.actual = (
                f"mrm_type: {baseline['mrm_type']} -> {result['mrm_type']}. "
                f"error_codes: "
                + (", ".join(e["error_code_hex"] for e in camera_errors) or "нет")
            )
            request.node.reaction_ms = f"{result['reaction_ms']}ms"

        finally:
            with allure.step("Восстановить питание камеры (relay_on)"):
                # В finally -- чтобы стенд не остался обесточенным даже
                # при падении ассертов выше.
                relay_on()
                node.logger.info("relay_on() отправлен, ждём восстановления...")

            with allure.step("Дождаться возврата mrm_type к исходному значению"):
                recovery = mrm_monitor.wait_for_mrm_type_change(
                    from_value="2",
                    to_value=baseline["mrm_type"] or "0",
                    timeout=30.0,
                    poll_interval=0.5,
                )
                if not recovery["success"]:
                    node.logger.warning(
                        "Восстановление mrm_type после relay_on не "
                        "подтверждено за 30s. ТРЕБУЕТСЯ РУЧНАЯ ПРОВЕРКА "
                        "стенда перед следующим тестом сьюта -- иначе "
                        "следующий тест может стартовать со stale "
                        "состоянием mrm_type=2."
                    )


# TC-SENSING-RELAY-CAM-002
@allure.epic("HIL Testing")
@allure.feature("Sensing")
@allure.story("Fault Injection: HW отказ через реле (камера)")
@allure.title("Диагностика: поведение монитора при отсутствии реакции MRM")
class TestCameraRelayMonitorSelfCheck:

    @allure.severity(allure.severity_level.NORMAL)
    def test_wait_for_mrm_type_change_returns_false_on_timeout(
        self, mrm_monitor, request
    ):
        """
        TC-SENSING-RELAY-CAM-002.

        Не инжектит отказ физически -- проверяет только то, что
        wait_for_mrm_type_change() корректно возвращает success=False
        (а не зависает / не кидает исключение), если ожидаемого перехода
        mrm_type не происходит за таймаут. Полезен как smoke-тест самого
        монитора перед реальным relay-прогоном на новом стенде/контейнере.

        ПРИМЕЧАНИЕ: from_value/to_value подобраны заведомо маловероятными
        (переход "3 -> 4"), чтобы не словить случайное совпадение с
        реальным состоянием MRM на стенде.
        """
        before_stamp = mrm_monitor.get_stamp()

        result = mrm_monitor.wait_for_mrm_type_change(
            from_value="3",
            to_value="4",
            before_stamp=before_stamp,
            timeout=2.0,
            poll_interval=0.05,
        )

        request.node.expected = "success=False, без исключений и зависаний"
        request.node.actual = f"success={result['success']}"

        allure.attach(
            str(result),
            name="wait_for_mrm_type_change result",
            attachment_type=allure.attachment_type.TEXT,
        )

        assert result["success"] is False, (
            "Ожидался timeout (success=False) для заведомо невозможного "
            f"перехода mrm_type, получено: {result}"
        )
