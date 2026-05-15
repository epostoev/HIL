from framework.base_hil_test import BaseHILTest

# "TC-PER-PRE-001"
class BoomBarrierDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/boom_barrier_detector"
    PROCESS_NAME = "boom_barrier_detector/lib/boom_barrier_detector/boom_barrier_detector"
    def __init__(self):
        super().__init__(node_name="boom_barrier_detector", timeout=15)
        
# "TC-PER-PRE-002"
class BoxSegmentationFusionNode(BaseHILTest):
    NODE_NAME = "/perception/box_segmentation_fusion"
    PROCESS_NAME = "sat_perception_box_segmentation_fusion/lib/sat_perception_box_segmentation_fusion/box_segmentation_fusion_node"
    def __init__(self):
        super().__init__(node_name="box_segmentation_fusion", timeout=15)

# "TC-PER-PRE-003"
class CameraDetectsFusingNode(BaseHILTest):
    NODE_NAME = "/perception/camera_detects_fusing"
    PROCESS_NAME = "camera_detects_fusing/lib/camera_detects_fusing/camera_detects_fusing"
    def __init__(self):
        super().__init__(node_name="camera_detects_fusing", timeout=15)

# "TC-PER-PRE-004"
class СameraMapDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/camera_map_detector"
    PROCESS_NAME = "camera_map_detector/lib/camera_map_detector/camera_map_detector"
    def __init__(self):
        super().__init__(node_name="camera_map_detector", timeout=15)

# "TC-PER-PRE-005"
class CameraTrackerCppNode(BaseHILTest):
    NODE_NAME = "/perception/camera_tracker_cpp"
    PROCESS_NAME = "camera_tracker_cpp/lib/camera_tracker_cpp/camera_tracker_cpp"
    def __init__(self):
        super().__init__(node_name="camera_tracker_cpp", timeout=15)

# "TC-PER-PRE-006"
class СameraTracksMergerNode(BaseHILTest):
    NODE_NAME = "/perception/camera_tracks_merger"
    PROCESS_NAME = "camera_tracks_merger/lib/camera_tracks_merger/camera_tracks_merger"
    def __init__(self):
        super().__init__(node_name="camera_tracks_merger", timeout=15)

# "TC-PER-PRE-007"
class CloudMotionDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/cloud_motion_detector"
    PROCESS_NAME = "cloud_motion_detector/lib/cloud_motion_detector/cloud_motion_detector"
    def __init__(self):
        super().__init__(node_name="cloud_motion_detector", timeout=15)

# "TC-PER-PRE-008"
class Detections2ClustersFusionNode(BaseHILTest):
    NODE_NAME = "/perception/detections2clusters_fusion"
    PROCESS_NAME = "detections2clusters_fusion/lib/detections2clusters_fusion/detections2clusters_fusion"
    def __init__(self):
        super().__init__(node_name="detections2clusters_fusion", timeout=15)

# "TC-PER-PRE-009"
class Detector3dNode(BaseHILTest):
    NODE_NAME = "/perception/detector_3d"
    PROCESS_NAME = "detector_3d/lib/detector_3d/detector_3d"
    def __init__(self):
        super().__init__(node_name="detector_3d", timeout=15)

# "TC-PER-PRE-010"
class FilterTciIdNode(BaseHILTest):
    NODE_NAME = "/perception/filter_tci_id"
    PROCESS_NAME = "filter_tci_id/lib/filter_tci_id/filter_tci_id"
    def __init__(self):
        super().__init__(node_name="filter_tci_id", timeout=15)

# "TC-PER-PRE-011"
class FrontBackboneNode(BaseHILTest):
    NODE_NAME = "/perception/front_backbone"
    PROCESS_NAME = "front_backbone/lib/front_backbone/front_backbone"
    def __init__(self):
        super().__init__(node_name="front_backbone", timeout=15)

# "TC-PER-PRE-012"
class GroundSegmentatorGpNode(BaseHILTest):
    NODE_NAME = "/perception/ground_segmentator_gp"
    PROCESS_NAME = "ground_segmentator_gp/lib/ground_segmentator_gp/ground_segmentator_gp"
    def __init__(self):
        super().__init__(node_name="ground_segmentator_gp", timeout=15)

# "TC-PER-PRE-013"
class ImageSegmenterNode(BaseHILTest):
    NODE_NAME = "/perception/image_segmenter"
    PROCESS_NAME = "image_segmenter/lib/image_segmenter/image_segmenter"
    def __init__(self):
        super().__init__(node_name="image_segmenter", timeout=15)

# "TC-PER-PRE-014"
class LaneletsDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/lanelets_detector"
    PROCESS_NAME = "lanelets_detector/lib/lanelets_detector/lanelets_detector"
    def __init__(self):
        super().__init__(node_name="lanelets_detector", timeout=15)

# "TC-PER-PRE-015"
class LidarBlindZonesNode(BaseHILTest):
    NODE_NAME = "/perception/lidar_blind_zones"
    PROCESS_NAME = "lidar_blind_zones/lib/lidar_blind_zones/lidar_blind_zones"
    def __init__(self):
        super().__init__(node_name="lidar_blind_zones", timeout=15)

# "TC-PER-PRE-016"
class LidarNoiseDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/lidar_noise_detector"
    PROCESS_NAME = "lidar_noise_detector/lib/lidar_noise_detector/lidar_noise_detector"
    def __init__(self):
        super().__init__(node_name="lidar_noise_detector", timeout=15)

# "TC-PER-PRE-017"
class ObstaclesTrackerNode(BaseHILTest):
    NODE_NAME = "/perception/obstacles_tracker"
    PROCESS_NAME = "obstacles_tracker/lib/obstacles_tracker/obstacles_tracker"
    def __init__(self):
        super().__init__(node_name="obstacles_tracker", timeout=15)

# "TC-PER-PRE-018"
class PointCloudClusterizerNode(BaseHILTest):
    NODE_NAME = "/perception/point_cloud_clusterizer"
    PROCESS_NAME = "point_cloud_clusterizer/lib/point_cloud_clusterizer/point_cloud_clusterizer"
    def __init__(self):
        super().__init__(node_name="point_cloud_clusterizer", timeout=15)

# "TC-PER-PRE-019"
class PollutionDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/pollution_detector"
    PROCESS_NAME = "pollution_detector/lib/pollution_detector/pollution_detector"
    def __init__(self):
        super().__init__(node_name="pollution_detector", timeout=15)

# "TC-PER-PRE-020"
class RadarCameraFusionNode(BaseHILTest):
    NODE_NAME = "/perception/radar_camera_fusion"
    PROCESS_NAME = "radar_camera_fusion/lib/radar_camera_fusion/radar_camera_fusion"
    def __init__(self):
        super().__init__(node_name="radar_camera_fusion", timeout=15)

# "TC-PER-PRE-021"
class RadarStaticObstaclesDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/radar_static_obstacles_detector"
    PROCESS_NAME = "radar_static_obstacles_detector/lib/radar_static_obstacles_detector/radar_static_obstacles_detector"
    def __init__(self):
        super().__init__(node_name="radar_static_obstacles_detector", timeout=15)

# "TC-PER-PRE-022"
class RoadLines3dNode(BaseHILTest):
    NODE_NAME = "/perception/road_lines_3d"
    PROCESS_NAME = "road_lines_3d/lib/road_lines_3d/road_lines_3d"
    def __init__(self):
        super().__init__(node_name="road_lines_3d", timeout=15)

# "TC-PER-PRE-023"
class RoadLinesTrackerNode(BaseHILTest):
    NODE_NAME = "/perception/road_lines_tracker"
    PROCESS_NAME = "road_lines_tracker/lib/road_lines_tracker/road_lines_tracker"
    def __init__(self):
        super().__init__(node_name="road_lines_tracker", timeout=15)

# "TC-PER-PRE-024"
class RoadSurfaceConditionDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/road_surface_condition_detector"
    PROCESS_NAME = "road_surface_condition_detector/lib/road_surface_condition_detector/road_surface_condition_detector"
    def __init__(self):
        super().__init__(node_name="road_surface_condition_detector", timeout=15)

# "TC-PER-PRE-025"
class RoadworksFusionNode(BaseHILTest):
    NODE_NAME = "/perception/roadworks_fusion"
    PROCESS_NAME = "roadworks_fusion/lib/roadworks_fusion/roadworks_fusion"
    def __init__(self):
        super().__init__(node_name="roadworks_fusion", timeout=15)

# "TC-PER-PRE-026"
class RoiSelectorNode(BaseHILTest):
    NODE_NAME = "/perception/roi_selector"
    PROCESS_NAME = "roi_selector/lib/roi_selector/roi_selector"
    def __init__(self):
        super().__init__(node_name="roi_selector", timeout=15)

# "TC-PER-PRE-027"
class SegmentationHdmapFusionNode(BaseHILTest):
    NODE_NAME = "/perception/segmentation_hdmap_fusion"
    PROCESS_NAME = "segmentation_hdmap_fusion/lib/segmentation_hdmap_fusion/segmentation_hdmap_fusion"
    def __init__(self):
        super().__init__(node_name="segmentation_hdmap_fusion", timeout=15)

# "TC-PER-PRE-028"
class SignalsСlassifierNode(BaseHILTest):
    NODE_NAME = "/perception/signals_classifier"
    PROCESS_NAME = "signals_classifier/lib/signals_classifier/signals_classifier"
    def __init__(self):
        super().__init__(node_name="signals_classifier", timeout=15)

# "TC-PER-PRE-029"
class SpeedLimitClassifierNode(BaseHILTest):
    NODE_NAME = "/perception/speed_limit_classifier"
    PROCESS_NAME = "speed_limit_classifier/lib/speed_limit_classifier/speed_limit_classifier"
    def __init__(self):
        super().__init__(node_name="speed_limit_classifier", timeout=15)

# "TC-PER-PRE-030"
class StaticObstaclesDetectorNode(BaseHILTest):
    NODE_NAME = "/perception/static_obstacles_detector"
    PROCESS_NAME = "static_obstacles_detector/lib/static_obstacles_detector/static_obstacles_detector"
    def __init__(self):
        super().__init__(node_name="static_obstacles_detector", timeout=15)

# "TC-PER-PRE-031"
class TrafficLightDetectsNode(BaseHILTest):
    NODE_NAME = "/perception/traffic_light_detects"
    PROCESS_NAME = "traffic_light_detects/lib/traffic_light_detects/traffic_light_detects"
    def __init__(self):
        super().__init__(node_name="traffic_light_detects", timeout=15)

# "TC-PER-PRE-032"
class TrafficLightGroupperNode(BaseHILTest):
    NODE_NAME = "/perception/traffic_light_groupper"
    PROCESS_NAME = "traffic_light_groupper/lib/traffic_light_groupper/traffic_light_groupper"
    def __init__(self):
        super().__init__(node_name="traffic_light_groupper", timeout=15)

# "TC-PER-PRE-033"
class TrafficLightLocalizationNode(BaseHILTest):
    NODE_NAME = "/perception/traffic_light_localization"
    PROCESS_NAME = "traffic_light_localization/lib/traffic_light_localization/traffic_light_localization"
    def __init__(self):
        super().__init__(node_name="traffic_light_localization", timeout=15)

# "TC-PER-PRE-034"
class TrafficSignDetectsNode(BaseHILTest):
    NODE_NAME = "/perception/traffic_sign_detects"
    PROCESS_NAME = "traffic_sign_detects/lib/traffic_sign_detects/traffic_sign_detects"
    def __init__(self):
        super().__init__(node_name="traffic_sign_detects", timeout=15)

# "TC-PER-PRE-035"
class TrafficSignLocalizationNode(BaseHILTest):
    NODE_NAME = "/perception/traffic_sign_localization"
    PROCESS_NAME = "traffic_sign_localization/lib/traffic_sign_localization/traffic_sign_localization"
    def __init__(self):
        super().__init__(node_name="traffic_sign_localization", timeout=15)

# "TC-PER-PRE-036"
class VehicleDetectsNode(BaseHILTest):
    NODE_NAME = "/perception/vehicle_detects"
    PROCESS_NAME = "vehicle_detects/lib/vehicle_detects/vehicle_detects"
    def __init__(self):
        super().__init__(node_name="vehicle_detects", timeout=15)