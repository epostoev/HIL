from framework.base_hil_test import BaseHILTest

class AutoCleaningNode(BaseHILTest):
    NODE_NAME = "/sensing/auto_cleaning"

    def __init__(self):
        super().__init__(node_name="auto_cleaning", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive


class OdometryNode(BaseHILTest):
    NODE_NAME = "/sensing/odometry_node"

    def __init__(self):
        super().__init__(node_name="odometry_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive


class OdometryVelocityNode(BaseHILTest):
    NODE_NAME = "/sensing/odometry_velocity_node"

    def __init__(self):
        super().__init__(node_name="odometry_velocity_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive