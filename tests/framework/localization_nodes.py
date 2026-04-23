from framework.base_hil_test import BaseHILTest

class LidarLocalizationNode(BaseHILTest):
    NODE_NAME = "/lidar_localization"
    PROCESS_NAME = "localization/lib/localization/lidar_localization_node"

    def __init__(self):
        super().__init__(node_name="lidar_localization", timeout=15)

class LocalizationLocalizationNode(BaseHILTest):
    NODE_NAME = "/localization/localization"
    PROCESS_NAME = "localization/lib/localization/localization_node"

    def __init__(self):
        super().__init__(node_name="localization", timeout=15)

class LocalizationInitializationNode(BaseHILTest):
    NODE_NAME = "/localization_initialization_node"
    PROCESS_NAME = "localization/lib/localization/localization_initialization_node"

    def __init__(self):
        super().__init__(node_name="localization_initialization_node", timeout=15)