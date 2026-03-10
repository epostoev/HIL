import subprocess
import time
from framework.base_hil_test import BaseHILTest


class CarapiNode(BaseHILTest):
    """
    Управление нодой /carapi_node.
    Поддерживает проверку состояния, kill и мониторинг восстановления.
    """

    NODE_NAME = "/carapi_node"
    DOCKER_CONTAINER = "sda-f898b5d"

    def __init__(self):
        super().__init__(node_name="carapi_node", timeout=15)

    # ── Переопределяем базовый метод ──────────────────────────────────────

    def is_alive(self) -> bool:
        """Проверить что /carapi_node присутствует в ROS graph"""
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive

    # ── Специфичные методы CarapiNode ─────────────────────────────────────

    def run_docker_command(self, cmd: str) -> subprocess.CompletedProcess:
        """Выполнить команду внутри Docker контейнера"""
        docker_cmd = f"docker exec {self.DOCKER_CONTAINER} {cmd}"
        return subprocess.run(
            docker_cmd, shell=True, capture_output=True, text=True, timeout=10
        )

    def kill(self) -> bool:
        """Принудительное завершение ноды через pkill -9"""
        self.logger.warning(f"Принудительное завершение: {self.NODE_NAME}")

        result = self.run_docker_command("pkill -9 -f carapi_node")
        self.logger.info(f"pkill return code: {result.returncode}")

        if result.returncode != 0:
            self.logger.warning("pkill не сработал, пробуем killall")
            self.run_docker_command("killall -9 carapi_node")

        time.sleep(1)
        success = not self.is_alive()

        if success:
            self.logger.info("Нода успешно завершена")
        else:
            self.logger.error("Нода не завершилась после kill!")

        return success

    def wait_for_death(self, timeout: int = 40, interval: int = 5) -> bool:
        """
        Ждать исчезновения ноды из ROS graph с мониторингом.
        Проверяет каждые interval секунд в пределах timeout.
        """
        self.logger.info(f"Ожидание DDS propagation, timeout={timeout}s")

        for elapsed in range(interval, timeout + 1, interval):
            time.sleep(interval)
            alive = self.is_alive()
            self.logger.info(f"[{elapsed}/{timeout}s] Нода в graph: {alive}")

            if not alive:
                self.logger.info(f"Нода исчезла из graph после {elapsed}s")
                return True

        self.logger.error(f"Нода не исчезла за {timeout} секунд")
        return False

    def check_graceful_degradation(self, min_nodes: int = 5) -> dict:
        """
        Проверить стабильность системы после kill.
        Возвращает словарь с результатами по каждому компоненту.
        """
        nodes = self.get_node_list()

        critical_components = {
            'perception': 1,
            'control': 1,
            'planning': 1,
            'watchdog': 1,
        }

        results = {}
        for comp, min_count in critical_components.items():
            count = len([n for n in nodes if comp in n.lower()])
            results[comp] = {
                "count": count,
                "required": min_count,
                "ok": count >= min_count,
            }
            self.logger.info(
                f"{comp}: {count} нод (требуется ≥{min_count}) "
                f"{'✅' if results[comp]['ok'] else '❌'}"
            )

        results["total_nodes"] = len(nodes)
        results["system_alive"] = len(nodes) > min_nodes
        return results