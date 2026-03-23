from framework.base_hil_test import BaseHILTest

class TeleopsManagerNode(BaseHILTest):
    NODE_NAME = "/teleops/manager"
    PROCESS_NAME = "teleops/lib/teleops/manager"

    def __init__(self):
        super().__init__(node_name="teleops_manager", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive