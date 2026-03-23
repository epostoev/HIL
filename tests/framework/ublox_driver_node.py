import subprocess
from framework.base_hil_test import BaseHILTest

class UbloxDriverNode(BaseHILTest):
    NODE_NAME = "/sensing/ublox1/ublox_driver_node"
    PROCESS_NAME = "ublox_driver/lib/ublox_driver/ublox_driver_node"

    def __init__(self):
        super().__init__(node_name="ublox_driver_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive