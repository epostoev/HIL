import pytest
from framework.carapi_node import CarapiNode


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


@pytest.fixture(scope="module")
def carapi_alive(carapi):
    """
    Фикстура с предусловием: пропускает тесты если нода не запущена.
    Используй вместо carapi когда нода обязана быть активна.
    """
    if not carapi.is_alive():
        pytest.skip("Нода /carapi_node не запущена — тест пропущен")
    return carapi

from framework.trajectory_planner_node import TrajectoryPlannerNode

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