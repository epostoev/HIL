import time
import pytest


class TestCarapiKill:
    """
    Fault Injection: принудительное завершение /carapi_node
    
    TC-FAULT-CARAPI-001: Предусловие — нода активна
    TC-FAULT-CARAPI-002: Kill — нода исчезает из ROS graph
    TC-FAULT-CARAPI-003: Graceful degradation — система стабильна
    """

    def test_01_precondition_carapi_running(self, carapi):
        """
        TC-FAULT-CARAPI-001-PRE: Предусловие
        Нода /carapi_node присутствует в ROS graph перед тестом.
        """
        if not carapi.is_alive():
            pytest.skip("Нода /carapi_node не запущена — тест пропущен")

        assert carapi.is_alive() is True

    def test_02_kill_carapi_node(self, carapi_alive):
        """
        TC-FAULT-CARAPI-002: Kill carapi_node
        
        Шаги:
        1. Зафиксировать состояние ДО
        2. Выполнить kill
        3. Ожидать DDS propagation (40 сек)
        4. Проверить что нода исчезла из ROS graph
        """
        nodes_before = carapi_alive.get_node_list()
        carapi_alive.logger.info(f"Нод до kill: {len(nodes_before)}")

        # Kill
        carapi_alive.kill()

        # Ожидание DDS propagation
        dead = carapi_alive.wait_for_death(timeout=40, interval=5)

        # Дополнительное ожидание если не исчезла
        if not dead:
            carapi_alive.logger.warning("Дополнительное ожидание 20 сек...")
            time.sleep(20)
            dead = not carapi_alive.is_alive()

        nodes_after = carapi_alive.get_node_list()
        carapi_alive.logger.info(
            f"Нод после kill: {len(nodes_after)} "
            f"(изменение: {len(nodes_before) - len(nodes_after)})"
        )

        if not dead:
            pytest.fail(
                "Нода carapi_node имеет auto-restart механизм. "
                "Отключите systemd/supervisor restart policy для этого теста."
            )

        assert not carapi_alive.is_alive(), "Нода не была корректно завершена"

    def test_03_system_stability_after_kill(self, carapi):
        """
        TC-FAULT-CARAPI-003: Graceful degradation
        Критичные компоненты продолжают работать без carapi_node.
        """
        time.sleep(5)  # стабилизация

        results = carapi.check_graceful_degradation(min_nodes=5)

        # Проверяем каждый критичный компонент
        for comp, data in results.items():
            if comp in ("total_nodes", "system_alive"):
                continue
            assert data["ok"], (
                f"Критичный компонент '{comp}' не работает: "
                f"найдено {data['count']} нод, требуется ≥{data['required']}"
            )

        assert results["system_alive"], (
            f"Система критически деградировала: "
            f"осталось {results['total_nodes']} нод"
        )


# Параметризованный тест — дополнительно к основным
@pytest.mark.parametrize("wait_timeout, expect_dead", [
    (40,  True),   # штатное ожидание
    (60,  True),   # расширенное ожидание
])
def test_carapi_dies_within_timeout(carapi_alive, wait_timeout, expect_dead):
    """
    Параметризованная проверка: нода завершается в пределах таймаута.
    """
    carapi_alive.kill()
    result = carapi_alive.wait_for_death(timeout=wait_timeout)
    assert result is expect_dead