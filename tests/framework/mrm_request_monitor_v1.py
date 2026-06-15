import subprocess
import threading


class MrmRequestMonitor:
    """
    Читает /safety/mrm_request непрерывно в фоновом треде.
    Один docker exec на весь сьют — нет SHM исчерпания.
    """

    def __init__(self, container: str):
        self.container = container
        self._latest_raw: str = ""
        self._lock = threading.Lock()
        self._proc = None
        self._thread = None
        self._running = False
        self._first_message = threading.Event()

    def start(self):
        cmd = [
            "docker", "exec", self.container,
            "bash", "-c",
            "source /rep/ros2/install/setup.bash && "
            "export ROS_DOMAIN_ID=1 && "
            "ros2 topic echo /safety/mrm_request 2>/dev/null"
        ]
        self._proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1
        )
        self._running = True
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()

    def _read_loop(self):
        buffer = []
        for line in self._proc.stdout:
            if not self._running:
                break
            if line.strip() == "---":
                raw = "\n".join(buffer)
                buffer = []
                if raw.strip():
                    with self._lock:
                        self._latest_raw = raw
                    self._first_message.set()
            else:
                buffer.append(line.rstrip())

    def wait_ready(self, timeout: int = 15) -> bool:
        return self._first_message.wait(timeout=timeout)

    def get_fields(self, fields: list[str]) -> dict:
        with self._lock:
            raw = self._latest_raw
        result = {f: None for f in fields}
        for line in raw.split("\n"):
            stripped = line.strip()
            for field in fields:
                if stripped.startswith(f"{field}:"):
                    try:
                        result[field] = stripped.split(":", 1)[1].strip()
                    except IndexError:
                        pass
        return result

    def stop(self):
        self._running = False
        if self._proc:
            self._proc.kill()
            self._proc.communicate()
