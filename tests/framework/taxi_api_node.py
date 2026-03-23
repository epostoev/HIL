from framework.base_hil_test import BaseHILTest

class TaxiApiNode(BaseHILTest):
    NODE_NAME = "/taxi/api_node"
    PROCESS_NAME = "taxi_api_node"

    def __init__(self):
        super().__init__(node_name="taxi_api_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive