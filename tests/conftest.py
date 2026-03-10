import pytest
from framework.carapi_node import CarapiNode
from framework.trajectory_planner_node import TrajectoryPlannerNode
from framework.imu_node import ImuNode
from framework.lidar_localization_node import LidarLocalizationNode


@pytest.fixture(scope="module")
def carapi():
    """
    Фикстура: создаёт объект CarapiNode.
    scope=module — один объект на весь тест-файл.
    """
    input(f"\n1 . WE are fixture carapi  | for continue, to click ENTER")
    node = CarapiNode()
    node.setup()
    yield node
    node.teardown()


@pytest.fixture(scope="module")
def carapi_alive(carapi):
    """
    Фикстура с предусловием: пропускает тесты если нода не запущена.
    Используй вместо carapi когда нода обязана быть активна.
    """
    input(f"WE ARE in FIXTURE \"CARAPI_ALIVE\" | for continue, to click ENTER") #TODO delete
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