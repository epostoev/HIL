from framework.base_hil_test import BaseHILTest

class CanTelemetryNode(BaseHILTest):
    NODE_NAME = "/can_telemetry"
    PROCESS_NAME = "can_telemetry/lib/can_telemetry/can_telemetry_node"

    def __init__(self):
        super().__init__(node_name="can_telemetry", timeout=15)


class CarapiNode(BaseHILTest):
    NODE_NAME = "/carapi_node"
    PROCESS_NAME = "carapi_node"

    def __init__(self):
        super().__init__(node_name="carapi_node", timeout=15)


class CloudTelemetryNode(BaseHILTest):
    NODE_NAME = "/infra/cloud_telemetry_node"
    PROCESS_NAME = "cloud_telemetry/lib/cloud_telemetry/cloud_telemetry_node"

    def __init__(self):
        super().__init__(node_name="cloud_telemetry_node", timeout=15)


class HardwareMetricsNode(BaseHILTest):
    NODE_NAME = "/hardware_metrics"
    PROCESS_NAME = "hardware_metrics/lib/hardware_metrics/hardware_metrics_node"

    def __init__(self):
        super().__init__(node_name="hardware_metrics", timeout=15)


class MetricsAggregatorNode(BaseHILTest):
    NODE_NAME = "/metrics_aggregator"
    PROCESS_NAME = "metrics_aggregator/lib/metrics_aggregator/metrics_aggregator_node"

    def __init__(self):
        super().__init__(node_name="metrics_aggregator", timeout=15)