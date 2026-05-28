from framework.base_hil_test import BaseHILTest

class ManeuverPlannerNode(BaseHILTest):
    NODE_NAME = "/planning/maneuver_planner_node"
    PROCESS_NAME = "maneuver_planner/lib/maneuver_planner/maneuver_planner_node"
 
    def __init__(self):
        super().__init__(node_name="maneuver_planner_node", timeout=15)
 
 
class LaneTracerNode(BaseHILTest):
    NODE_NAME = "/planning/lane_tracer_node"
    PROCESS_NAME = "lane_tracer/lib/lane_tracer/lane_tracer_node"
 
    def __init__(self):
        super().__init__(node_name="lane_tracer_node", timeout=15)
 
 
class TrajectoryPlannerNode(BaseHILTest):
    NODE_NAME = "/planning/trajectory_planner_node"
    PROCESS_NAME = "trajectory_planner/lib/trajectory_planner/trajectory_planner_node"
 
    def __init__(self):
        super().__init__(node_name="trajectory_planner_node", timeout=15)
 
 
class PathLoaderNode(BaseHILTest):
    NODE_NAME = "/planning/path_loader_node"
    PROCESS_NAME = "path_loader/lib/path_loader/path_loader_node"
 
    def __init__(self):
        super().__init__(node_name="path_loader_node", timeout=15)
