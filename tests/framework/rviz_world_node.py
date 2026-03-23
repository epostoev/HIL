from framework.base_hil_test import BaseHILTest

class RvizWorldNode(BaseHILTest):
    NODE_NAME = "/visualization/rviz_world_node"
    PROCESS_NAME = "rviz_world/lib/rviz_world/rviz_world_node"

    def __init__(self):
        super().__init__(node_name="rviz_world_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive