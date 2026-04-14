import pytest
from framework.control_system_monitor import ControlSystemMonitor
from framework.carapi_node import CarapiNode
from framework.trajectory_planner_node import TrajectoryPlannerNode
from framework.lidar_localization_node import LidarLocalizationNode
from framework.xviz_node import XvizNode
from framework.vinx_node import VinxNode
from framework.text_overlay import TextOverlay
from framework.sensing_nodes import AutoCleaningNode, OdometryNode, OdometryVelocityNode, ImuNode, RadarDriverNode, UbloxDriverNode, RadarVisualizationNode
from framework.mrm_request_monitor import MrmRequestMonitor
from framework.base_hil_test import DOCKER_CONTAINER

@pytest.fixture(scope="module")
def carapi():
    """
    Фикстура: создаёт объект CarapiNode.
    scope=module — один объект на весь тест-файл.
    """
    node = CarapiNode()
    node.setup()
    yield node
    node.teardown()


@pytest.fixture(scope="session", autouse=True)  # ← добавить autouse=True
def control_monitor():
    """
    Запускается автоматически в начале сессии — ДО любых тестов.
    Один persistent мониторинг /control/system на весь сьют.
    """
    monitor = ControlSystemMonitor()
    monitor.start()

    if not monitor.wait_ready(timeout=15):
        pytest.fail("Топик /control/system не публикует сообщения")

    yield monitor
    monitor.stop()

@pytest.fixture(scope="module")
def carapi_alive(carapi):
    """
    Фикстура с предусловием: пропускает тесты если нода не запущена.
    Используй вместо carapi когда нода обязана быть активна.
    """
    if not carapi.is_alive():
        pytest.skip("Нода /carapi_node не запущена — тест пропущен")
    return carapi


######
@pytest.fixture(scope="module")
def trajectory_planner():
    """Создаёт объект TrajectoryPlannerNode"""
    node = TrajectoryPlannerNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def trajectory_planner_alive(trajectory_planner):
    """С предусловием: пропускает тест если нода не запущена"""
    if not trajectory_planner.is_alive():
        pytest.skip("Нода /planning/trajectory_planner_node не запущена")
    return trajectory_planner


######
@pytest.fixture(scope="module")
def imu_node():
    """Создаёт объект ImuNode"""
    node = ImuNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def imu_node_alive(imu_node):
    """С предусловием: пропускает тест если нода не запущена"""
    if not imu_node.is_alive():
        pytest.skip("Нода /sensing/imu1/imu_node не запущена")
    return imu_node


######
@pytest.fixture(scope="module")
def lidar_localization():
    """Создаёт объект LidarLocalizationNode"""
    node = LidarLocalizationNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def lidar_localization_alive(lidar_localization):
    """С предусловием: пропускает тест если нода не запущена"""
    if not lidar_localization.is_alive():
        pytest.skip("Нода /lidar_localization не запущена")
    return lidar_localization

@pytest.fixture(scope="module")
def xviz_node():
    node = XvizNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def xviz_node_alive(xviz_node):
    if not xviz_node.is_alive():
        pytest.skip("Нода /visualization/xviz не запущена")
    return xviz_node


@pytest.fixture(scope="module")
def vinx_node():
    node = VinxNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def vinx_node_alive(vinx_node):
    if not vinx_node.is_alive():
        pytest.skip("Нода /visualization/vinx не запущена")
    return vinx_node

@pytest.fixture(scope="module")
def text_overlay():
    node = TextOverlay()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def text_overlay_alive(text_overlay):
    if not text_overlay.is_alive():
        pytest.skip("Нода visualization/text_overlay не запущена")
    return text_overlay


@pytest.fixture(scope="module")
def radar_driver_node():
    node = RadarDriverNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def auto_cleaning_node():
    print("\n\n 1 шаг - Выполнить node = AutoCleaningNode() - создал объект класса\n")
    node = AutoCleaningNode()
    print(f"\nID = {id(node)}\n")
    print(f"\nnode.__dict__ {node.__dict__}\n")
    print("\n3 шаг - Вызов node.setup()\n")
    node.setup() 
    print("\n4 шаг - Перешли в yeld, тест получил готовый обьект auto_cleaning_node\n")
    yield node 
    node.teardown()

@pytest.fixture(scope="module")
def odometry_node():
    node = OdometryNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def odometry_velocity_node():
    node = OdometryVelocityNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def ublox_driver_node():
    node = UbloxDriverNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def radar_visualization_node():
    node = RadarVisualizationNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def radar_driver_node_alive(radar_driver_node):
    if not radar_driver_node.is_alive():
        pytest.skip("Нода /sensing/radar_driver_node не запущена")
    return radar_driver_node

@pytest.fixture(scope="session", autouse=True)
def mrm_monitor():
    monitor = MrmRequestMonitor(container=DOCKER_CONTAINER)
    monitor.start()
    if not monitor.wait_ready(timeout=15):
        pytest.fail("Топик /safety/mrm_request не публикует сообщения")
    yield monitor
    monitor.stop()

@pytest.fixture(scope="module")
def auto_cleaning_node_alive(auto_cleaning_node):
    if not auto_cleaning_node.is_alive():
        pytest.skip("Нода /sensing/auto_cleaning не запущена")
    return auto_cleaning_node




def pytest_html_report_title(report):
    report.title = "HIL Fault Injection — Sensing Component"

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Добавляем дополнительные колонки
    report.expected = getattr(item, 'expected', '—')
    report.actual = getattr(item, 'actual', '—')

def pytest_html_results_table_header(cells):
    cells.insert(2, '<th>Ожидаемый результат</th>')
    cells.insert(3, '<th>Фактический результат</th>')

def pytest_html_results_table_row(report, cells):
    cells.insert(2, f'<td>{getattr(report, "expected", "—")}</td>')
    cells.insert(3, f'<td>{getattr(report, "actual", "—")}</td>')

import subprocess
import time

@pytest.fixture()
def restart_autopilot_after(mrm_monitor):
    """
    Перезапускает автопилот после теста.
    Использовать только в kill тестах.
    """
    yield

    subprocess.run(
        ["docker", "exec", DOCKER_CONTAINER,
         "bash", "-c", "pkill -2 -f 'python3.*drive'"],
        capture_output=True
    )
    print(f"\nАвтопилот остановлен. Перезапускаем...")
    time.sleep(60)

    subprocess.Popen(
        ["docker", "exec", "-d", DOCKER_CONTAINER,
         "bash", "-c",
         "cd /rep && "
         "source /opt/ros/humble/setup.bash && "
         "source /rep/ros2/install/setup.bash && "
         "drive -u postoev"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    result = mrm_monitor.wait_for_mrm_type_change(
        from_value="2",
        to_value="0",
        timeout=60.0,
        poll_interval=0.5
    )

    if result["success"]:
        print(f"Автопилот готов. mrm_type=0 ✅")
    else:
        pytest.fail("Автопилот не перезапустился за 60 секунд")