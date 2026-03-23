from framework.base_hil_test import BaseHILTest

class V2xPublisherNode(BaseHILTest):
    NODE_NAME = "/v2x_publisher_node"
    PROCESS_NAME = "v2x_publisher/lib/v2x_publisher/v2x_publisher"

    def __init__(self):
        super().__init__(node_name="v2x_publisher_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive