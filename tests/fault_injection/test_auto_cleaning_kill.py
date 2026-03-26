import time
import pytest


class TestAutoCleaningKill:
    """
    Fault Injection: принудительное завершение /sensing/auto_cleaning

    TC-FAULT-AUTO-CLEAN-001: Предусловие — нода активна
    TC-FAULT-AUTO-CLEAN-002: Kill — нода исчезает, MRM топик фиксируется
    """

    def test_01_precondition_node_running(self, auto_cleaning_node):
        """TC-FAULT-AUTO-CLEAN-001: Предусловие"""
        if not auto_cleaning_node.is_alive():
            pytest.skip("Нода /sensing/auto_cleaning не запущена")
        assert auto_cleaning_node.is_alive() is True

    def test_02_kill_and_check_mrm(self, auto_cleaning_node_alive, mrm_monitor):
        """
        TC-FAULT-AUTO-CLEAN-002: Kill ноды и проверка MRM топика.

        Шаги:
        1. Считать baseline из /safety/mrm_request ДО kill
        2. Убить ноду
        3. Проверить что нода умерла (или перезапустилась)
        4. Считать значения из /safety/mrm_request ПОСЛЕ kill
        5. Зафиксировать mrm_type, shadow_mrm_type, drive_mode
        """
        fields = ["mrm_type", "shadow_mrm_type", "drive_mode"]

        # Baseline ДО kill
        baseline = mrm_monitor.get_fields(fields)
        auto_cleaning_node_alive.logger.info(
            f"Baseline ДО kill: "
            f"mrm_type={baseline['mrm_type']}, "
            f"shadow_mrm_type={baseline['shadow_mrm_type']}, "
            f"drive_mode={baseline['drive_mode']}"
        )

        # Получаем PID и убиваем ноду
        pid_before = auto_cleaning_node_alive.get_pid()
        auto_cleaning_node_alive.logger.info(f"PID до kill: {pid_before}")

        auto_cleaning_node_alive.kill()

        pid_after = auto_cleaning_node_alive.get_pid()
        auto_cleaning_node_alive.logger.info(f"PID после kill: {pid_after}")

        # Ждём propagation
        time.sleep(5)

        # Читаем топик ПОСЛЕ kill
        after = mrm_monitor.get_fields(fields)
        auto_cleaning_node_alive.logger.info(
            f"ПОСЛЕ kill: "
            f"mrm_type={after['mrm_type']}, "
            f"shadow_mrm_type={after['shadow_mrm_type']}, "
            f"drive_mode={after['drive_mode']}"
        )

        # Фиксируем ожидаемые значения
        assert after["mrm_type"] == "2", \
            f"mrm_type: ожидалось '2', получено '{after['mrm_type']}'"
        assert after["shadow_mrm_type"] == "1", \
            f"shadow_mrm_type: ожидалось '1', получено '{after['shadow_mrm_type']}'"
        assert after["drive_mode"] == "2", \
            f"drive_mode: ожидалось '2', получено '{after['drive_mode']}'"

        auto_cleaning_node_alive.logger.info(
            "MRM топик зафиксирован корректно ✅"
        )

        # Фиксируем факт kill
        if auto_cleaning_node_alive.has_auto_restart:
            assert pid_after != pid_before, \
                "PID не изменился — kill не сработал"
            pytest.xfail(
                f"Нода перезапущена drive.py (новый PID: {pid_after}). "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен."
            )

        assert not auto_cleaning_node_alive.is_alive(), \
            "Нода не была корректно завершена"