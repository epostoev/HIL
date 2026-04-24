import pytest


INTEGRATION_NODES = [
    ("can_telemetry_node",       "TC-INT-PRE-001", "/can_telemetry"),
    ("carapi_integration_node",  "TC-INT-PRE-002", "/carapi_node"),
    ("cloud_telemetry_node",     "TC-INT-PRE-003", "/infra/cloud_telemetry_node"),
    ("hardware_metrics_node",    "TC-INT-PRE-004", "/hardware_metrics"),
    ("metrics_aggregator_node",  "TC-INT-PRE-005", "/metrics_aggregator"),
]


class TestIntegrationNodesRunning:
    """
    Проверка что все ноды компонента General Integration запущены.

    TC-INT-PRE-001: /can_telemetry
    TC-INT-PRE-002: /carapi_node
    TC-INT-PRE-003: /infra/cloud_telemetry_node
    TC-INT-PRE-004: /hardware_metrics
    TC-INT-PRE-005: /metrics_aggregator
    """

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", INTEGRATION_NODES)
    def test_node_running(self, fixture_name, tc_id, node_name, request):
        f"""{tc_id}: {node_name} присутствует в ROS graph"""

        node = request.getfixturevalue(fixture_name)

        request.node.expected = f"Нода {node_name} присутствует в ROS graph"

        if not node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip(f"Нода {node_name} не запущена")

        assert node.is_alive() is True

        request.node.actual = f"Нода {node_name} жива ✅"