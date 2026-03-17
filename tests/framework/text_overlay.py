import time
import subprocess
from framework.base_hil_test import BaseHILTest


class TextOverlay(BaseHILTest):
    """
    Управление нодой /visualization/text_overlay.
    """

    NODE_NAME = "/visualization/text_overlay"
    PROCESS_NAME = "text_overlay/lib/text_overlay/overlay"
    EXPECTED_ERRORS = {}

    def __init__(self):
        super().__init__(node_name="text_overlay", timeout=15)
        self.has_auto_restart = False

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive

    def run_docker_command(self, cmd: str) -> subprocess.CompletedProcess:
        docker_cmd = f"docker exec {self.DOCKER_CONTAINER} {cmd}"
        self.logger.info(f"Docker exec: {cmd}")
        return subprocess.run(
            docker_cmd, shell=True, capture_output=True, text=True, timeout=10
        )

    def get_pid(self) -> int | None:
        result = self.run_docker_command(
            f"ps aux | grep '{self.PROCESS_NAME}' | grep -v grep"
        )
        if result.returncode == 0 and result.stdout.strip():
            pid = int(result.stdout.strip().split('\n')[0].split()[1])
            self.logger.info(f"Найден PID: {pid}")
            return pid
        self.logger.warning("Процесс не найден")
        return None

    def kill(self) -> bool:
        self.logger.warning(f"Kill: {self.NODE_NAME}")

        pid = self.get_pid()
        if not pid:
            self.logger.error("Не удалось получить PID")
            return False

        result = self.run_docker_command(f"kill -9 {pid}")
        self.logger.info(f"kill return code: {result.returncode}")

        time.sleep(0.5)
        new_pid = self.get_pid()

        if new_pid and new_pid != pid:
            self.has_auto_restart = True
            self.logger.warning(
                f"Нода перезапущена! "
                f"Старый PID: {pid} → Новый PID: {new_pid}"
            )
        elif not new_pid:
            self.logger.info(f"Нода завершена, PID {pid} больше не существует")

        time.sleep(3)

        if self.is_alive():
            self.has_auto_restart = True
            self.logger.warning("Нода перезапущена после задержки!")
            return False

        self.logger.info("Kill успешен")
        return True

    def wait_for_death(self, timeout: int = 40, interval: int = 5) -> bool:
        self.logger.info(f"Ожидание DDS propagation, timeout={timeout}s")
        for elapsed in range(interval, timeout + 1, interval):
            time.sleep(interval)
            alive = self.is_alive()
            self.logger.info(f"[{elapsed}/{timeout}s] Нода в graph: {alive}")
            if not alive:
                self.logger.info(f"Нода исчезла после {elapsed}s")
                return True
        self.logger.error(f"Нода не исчезла за {timeout} секунд")
        return False

    def check_visualization_degradation(self) -> dict:
        nodes = self.get_node_list()
        viz_nodes = [n for n in nodes if 'visualization' in n.lower()]

        result = {
            "vinx_gone": self.NODE_NAME not in nodes,
            "other_viz_alive": len([n for n in viz_nodes
                                    if n != self.NODE_NAME]) > 0,
            "viz_nodes": viz_nodes,
            "has_auto_restart": self.has_auto_restart,
        }
        self.logger.info(f"Ноды visualization после kill: {viz_nodes}")
        return result