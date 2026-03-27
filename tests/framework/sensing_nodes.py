from framework.base_hil_test import BaseHILTest

class AutoCleaningNode(BaseHILTest):
    NODE_NAME = "/sensing/auto_cleaning"
    PROCESS_NAME = "auto_cleaning/lib/auto_cleaning/auto_cleaning_node"

    def __init__(self):
        print(f"\nI in self = {id(self)}\n")
        print(f"\nsuper = {super()}\n")
        super().__init__(node_name="auto_cleaning", timeout=15)
        print("\n2 шаг - Вызвал super().__init__() из BaseHILTest. \n {type(self).__name__}",{type(self).__name__})

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        print(f"\nSELF in class AutoCleaningNode {id(self)}\n")
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive


class OdometryNode(BaseHILTest):
    NODE_NAME = "/sensing/odometry_node"
    PROCESS_NAME = "odometry_driver/lib/odometry_driver/odometry_node"

    def __init__(self):
        super().__init__(node_name="odometry_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive


class OdometryVelocityNode(BaseHILTest):
    NODE_NAME = "/sensing/odometry_velocity_node"
    PROCESS_NAME = "odometry_velocity/lib/odometry_velocity/odometry_velocity_node"

    def __init__(self):
        super().__init__(node_name="odometry_velocity_node", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive