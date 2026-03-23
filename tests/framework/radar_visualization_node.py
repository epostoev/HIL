import subprocess
from framework.base_hil_test import BaseHILTest

class RadarVisualizationNode(BaseHILTest):
    NODE_NAME = "/sensing/visualization/radar_visualization_node"
    PROCESS_NAME = "radar_visualization/lib/radar_visualization/radar_visualization_node"

    def __init__(self):
        super().__init__(node_name="radar_visualization_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive