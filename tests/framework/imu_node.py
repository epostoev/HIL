import time
import subprocess
from framework.base_hil_test import BaseHILTest
from framework.base_hil_test import DOCKER_CONTAINER


class ImuNode(BaseHILTest):

    NODE_NAME = "/sensing/imu1/imu_node"
    PROCESS_NAME = "imu_node"
    # DOCKER_CONTAINER = "sda-f898b5d"  # ← уточни после docker ps

    def __init__(self):
        super().__init__(node_name="imu_node", timeout=15)
        self.has_auto_restart = False

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive

    def run_docker_command(self, cmd: str) -> subprocess.CompletedProcess:
        """Выполнить команду внутри Docker контейнера"""
        docker_cmd = f"docker exec {self.DOCKER_CONTAINER} {cmd}"
        self.logger.info(f"Docker exec: {cmd}")
        return subprocess.run(
            docker_cmd, shell=True, capture_output=True, text=True, timeout=10
        )

    def get_pid(self) -> int | None:
        """
        Получить PID процесса внутри Docker контейнера.
        Используем docker exec — процесс не виден снаружи контейнера.
        """
        result = self.run_docker_command(
            f"ps aux | grep {self.PROCESS_NAME} | grep -v grep | grep -v pkill"
        )

        if result.returncode == 0 and result.stdout.strip():
            pid = int(result.stdout.strip().split('\n')[0].split()[1])
            self.logger.info(f"Найден PID внутри контейнера: {pid}")
            return pid

        self.logger.warning("Процесс не найден внутри контейнера")
        return None

    def kill(self) -> bool:
        self.logger.warning(f"Kill: {self.NODE_NAME}")

        pid = self.get_pid()
        if not pid:
            self.logger.error("Не удалось получить PID")
            return False

        self.logger.info(f"Выполняем: docker exec kill -9 {pid}")
        result = self.run_docker_command(f"kill -9 {pid}")
        self.logger.info(f"kill return code: {result.returncode}")

        # Проверка сразу — процесс мёртв?
        time.sleep(0.5)
        new_pid = self.get_pid()

        if new_pid and new_pid != pid:
            self.has_auto_restart = True
            self.logger.warning(
                f"drive.py перезапустил ноду! "
                f"Старый PID: {pid} → Новый PID: {new_pid}"
            )
        elif not new_pid:
            self.logger.info(f"Нода завершена, PID {pid} больше не существует")

        # Ждём дольше — drive.py может поднять ноду за 2-3 секунды
        time.sleep(3)

        if self.is_alive():
            # ← ВОТ ФИКС: выставляем флаг здесь тоже
            self.has_auto_restart = True
            self.logger.warning(
                "drive.py перезапустил ноду после задержки! "
                f"has_auto_restart = True"
            )
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
    
    def check_sensing_degradation(self) -> dict:
        """
        Проверить что сенсорная система деградировала корректно —
        смежные ноды sensing живы, imu_node отсутствует.
        """
        nodes = self.get_node_list()
        sensing_nodes = [n for n in nodes if 'sensing' in n.lower()]

        result = {
            "imu_node_gone": self.NODE_NAME not in nodes,
            "other_sensing_alive": len(sensing_nodes) > 0,
            "sensing_nodes": sensing_nodes,
            "has_auto_restart": self.has_auto_restart,
        }
        self.logger.info(f"Ноды sensing после kill: {sensing_nodes}")
        return result

    def check_planning_degradation(self) -> dict:
        nodes = self.get_node_list()
        planning_nodes = [n for n in nodes if 'planning' in n.lower()]
        result = {
            "trajectory_planner_gone": self.NODE_NAME not in nodes,
            "other_planning_alive": len(planning_nodes) > 0,
            "planning_nodes": planning_nodes,
            "has_auto_restart": self.has_auto_restart,
        }
        self.logger.info(f"Ноды planning: {planning_nodes}")
        return result