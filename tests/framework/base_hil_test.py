import logging
import subprocess
import os

os.environ['RMW_IMPLEMENTATION'] = 'rmw_cyclonedds_cpp'
os.environ['ROS_DOMAIN_ID'] = '1'


class BaseHILTest:
    """Базовый класс для всех HIL тестов"""

    def __init__(self, node_name: str, timeout: int = 15):
        self.node_name = node_name
        self.timeout = timeout
        self.logger = self._setup_logger()

    def _setup_logger(self):
        logger = logging.getLogger(self.node_name)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(
            "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
        ))
        logger.addHandler(handler)
        return logger

    def run_ros(self, cmd: str, timeout: int = None) -> subprocess.CompletedProcess:
        """Выполнить команду в ROS 2 окружении"""
        _timeout = timeout or self.timeout
        full = (
            f"bash -c 'source /opt/ros/humble/setup.bash && "
            f"export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp && "
            f"export ROS_DOMAIN_ID=1 && {cmd}'"
        )
        return subprocess.run(
            full, shell=True, capture_output=True, text=True, timeout=_timeout
        )

    def get_node_list(self) -> list[str]:
        """Получить список активных нод из ROS graph"""
        result = self.run_ros("ros2 node list 2>/dev/null")
        return [n.strip() for n in result.stdout.split('\n') if n.strip()]

    def is_alive(self) -> bool:
        """Проверить что нода присутствует в ROS graph — переопределяется в дочернем классе"""
        raise NotImplementedError("Дочерний класс обязан реализовать is_alive()")

    def setup(self):
        self.logger.info(f"=== Начало теста для {self.node_name} ===")

    def teardown(self):
        self.logger.info(f"=== Завершение теста для {self.node_name} ===")