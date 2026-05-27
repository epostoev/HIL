import pytest
from framework.control_system_monitor import ControlSystemMonitor
from framework.sensing_nodes import AutoCleaningNode, OdometryNode, OdometryVelocityNode, ImuNode, RadarDriverNode, UbloxDriverNode, RadarVisualizationNode
from framework.localization_nodes import (LocalizationOutputGatewayNode, LocalizationNodeContainerNode)
from framework.general_intregation_nodes import (CanTelemetryNode, CarapiNode, CloudTelemetryNode, HardwareMetricsNode, MetricsAggregatorNode, HalNode, CrashDetectorNode, SdaProcessMonitorNode, V2xPublisherNode, Rosbag2RecorderNode, MrmArbiterNode)
from framework.perception_nodes import (BoomBarrierDetectorNode, BoxSegmentationFusionNode, CameraDetectsFusingNode, СameraMapDetectorNode, CameraTrackerCppNode, СameraTracksMergerNode, CloudMotionDetectorNode, Detector3dNode, FrontBackboneNode, ImageSegmenterNode, LidarBlindZonesNode, LidarNoiseDetectorNode, StaticObstaclesTrackerNode, PointCloudClusterizerNode, PollutionDetectorNode, RadarStaticObstaclesDetectorNode, RoadLines3dNode, RoadLinesTrackerNode, RoadSurfaceConditionDetectorNode, RoadworksFusionNode, SegmentationHdmapFusionNode, SignalsСlassifierNode, SpeedLimitClassifierNode, TrafficLightDetectsNode, TrafficSignDetectsNode, TrafficSignLocalizationNode, VehicleDetectsNode, LidarStaticObstaclesDetectorNode, CloudClustersVisualizationNode, PerceptionLanesVisualizationPyNode, PerceptionVisualization2dNode, TrafficLightPipelineNode, ObjectsVisualizationNode)
from framework.mrm_request_monitor import MrmRequestMonitor
from framework.base_hil_test import DOCKER_CONTAINER

@pytest.fixture(scope="session", autouse=True)  # ← добавить autouse=True
def control_monitor():
    """
    Запускается автоматически в начале сессии — ДО любых тестов.
    Один persistent мониторинг /control/system на весь сьют.
    """
    monitor = ControlSystemMonitor()
    monitor.start()

    if not monitor.wait_ready(timeout=15):
        pytest.fail("Топик /control/system не публикует сообщения")

    yield monitor
    monitor.stop()

@pytest.fixture(scope="module")
def carapi_alive(carapi):
    """
    Фикстура с предусловием: пропускает тесты если нода не запущена.
    Используй вместо carapi когда нода обязана быть активна.
    """
    if not carapi.is_alive():
        pytest.skip("Нода /carapi_node не запущена — тест пропущен")
    return carapi


######
@pytest.fixture(scope="module")
def trajectory_planner():
    """Создаёт объект TrajectoryPlannerNode"""
    node = TrajectoryPlannerNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def trajectory_planner_alive(trajectory_planner):
    """С предусловием: пропускает тест если нода не запущена"""
    if not trajectory_planner.is_alive():
        pytest.skip("Нода /planning/trajectory_planner_node не запущена")
    return trajectory_planner


@pytest.fixture(scope="module")
def imu_node_alive(imu_node):
    """С предусловием: пропускает тест если нода не запущена"""
    if not imu_node.is_alive():
        pytest.skip("Нода /sensing/imu1/imu_node не запущена")
    return imu_node

@pytest.fixture(scope="module")
def xviz_node():
    node = XvizNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def xviz_node_alive(xviz_node):
    if not xviz_node.is_alive():
        pytest.skip("Нода /visualization/xviz не запущена")
    return xviz_node


@pytest.fixture(scope="module")
def vinx_node():
    node = VinxNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def vinx_node_alive(vinx_node):
    if not vinx_node.is_alive():
        pytest.skip("Нода /visualization/vinx не запущена")
    return vinx_node

@pytest.fixture(scope="module")
def text_overlay():
    node = TextOverlay()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def text_overlay_alive(text_overlay):
    if not text_overlay.is_alive():
        pytest.skip("Нода visualization/text_overlay не запущена")
    return text_overlay

# Sensing

@pytest.fixture(scope="module")
def auto_cleaning_node():
    print("\n\n 1 шаг - Выполнить node = AutoCleaningNode() - создал объект класса\n")
    node = AutoCleaningNode()
    print(f"\nID = {id(node)}\n")
    print(f"\nnode.__dict__ {node.__dict__}\n")
    print("\n3 шаг - Вызов node.setup()\n")
    node.setup() 
    print("\n4 шаг - Перешли в yeld, тест получил готовый обьект auto_cleaning_node\n")
    yield node 
    node.teardown()

@pytest.fixture(scope="module")
def imu_node():
    """Создаёт объект ImuNode"""
    node = ImuNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def odometry_node():
    node = OdometryNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def odometry_velocity_node():
    node = OdometryVelocityNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def radar_driver_node():
    node = RadarDriverNode()
    node.setup()
    yield node
    node.teardown()

@pytest.fixture(scope="module")
def ublox_driver_node():
    node = UbloxDriverNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def radar_visualization_node():
    node = RadarVisualizationNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def radar_driver_node_alive(radar_driver_node):
    if not radar_driver_node.is_alive():
        pytest.skip("Нода /sensing/radar_driver_node не запущена")
    return radar_driver_node


# =============================================================================
# Localization

@pytest.fixture(scope="module")
def localization_output_gateway_node():
    node = LocalizationOutputGatewayNode(); node.setup(); yield node; node.teardown()


@pytest.fixture(scope="module")
def localization_output_gateway_node_alive(localization_output_gateway_node):
    if not localization_output_gateway_node.is_alive():
        pytest.skip("Нода /localization_output_gateway_node не запущена")
    return localization_output_gateway_node

@pytest.fixture(scope="module")
def localization_node_container_node():
    node = LocalizationNodeContainerNode(); node.setup(); yield node; node.teardown()


@pytest.fixture(scope="module")
def localization_node_container_node_alive(localization_node_container_node):
    if not localization_node_container_node.is_alive():
        pytest.skip("Нода /localization/node_container не запущена")
    return localization_node_container_node

# Localization
# =============================================================================


# =============================================================================
# General_Intregation

@pytest.fixture(scope="module")
def can_telemetry_node():
    node = CanTelemetryNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def carapi_integration_node():
    node = CarapiNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def cloud_telemetry_node():
    node = CloudTelemetryNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def hardware_metrics_node():
    node = HardwareMetricsNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def metrics_aggregator_node():
    node = MetricsAggregatorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def can_telemetry_node_alive(can_telemetry_node):
    if not can_telemetry_node.is_alive():
        pytest.skip("Нода /can_telemetry не запущена")
    return can_telemetry_node

@pytest.fixture(scope="module")
def carapi_integration_node_alive(carapi_integration_node):
    if not carapi_integration_node.is_alive():
        pytest.skip("Нода /carapi_node не запущена")
    return carapi_integration_node

@pytest.fixture(scope="module")
def cloud_telemetry_node_alive(cloud_telemetry_node):
    if not cloud_telemetry_node.is_alive():
        pytest.skip("Нода /infra/cloud_telemetry_node не запущена")
    return cloud_telemetry_node

@pytest.fixture(scope="module")
def hardware_metrics_node_alive(hardware_metrics_node):
    if not hardware_metrics_node.is_alive():
        pytest.skip("Нода /hardware_metrics не запущена")
    return hardware_metrics_node

@pytest.fixture(scope="module")
def metrics_aggregator_node_alive(metrics_aggregator_node):
    if not metrics_aggregator_node.is_alive():
        pytest.skip("Нода /metrics_aggregator не запущена")
    return metrics_aggregator_node

@pytest.fixture(scope="module")
def hal_node():
    node = HalNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def can_hal_node_alive(hal_node):
    if not hal_node.is_alive():
        pytest.skip("Нода /generic/hal не запущена")
    return hal_node

@pytest.fixture(scope="module")
def crash_detector_node():
    node = CrashDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def can_hal_node_alive(hal_node):
    if not crash_detector_node.is_alive():
        pytest.skip("Нода /safety/crash_detector не запущена")
    return crash_detector_node

@pytest.fixture(scope="module")
def sda_process_monitor_node():
    node = SdaProcessMonitorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def sda_process_monitor_node_alive(hal_node):
    if not sda_process_monitor_node.is_alive():
        pytest.skip("Нода /sda_process_monitor/sda_process_monitor не запущена")
    return sda_process_monitor_node

@pytest.fixture(scope="module")
def v2x_publisher_node():
    node = V2xPublisherNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def v2x_publisher_node_alive(hal_node):
    if not v2x_publisher_node.is_alive():
        pytest.skip("Нода /v2x_publisher_node не запущена")
    return v2x_publisher_node

@pytest.fixture(scope="module")
def rosbag2_recorder_node():
    node = Rosbag2RecorderNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def rosbag2_recorder_node_alive(hal_node):
    if not rosbag2_recorder_node.is_alive():
        pytest.skip("Нода /data_logging/rosbag2_recorder не запущена")
    return rosbag2_recorder_node

@pytest.fixture(scope="module")
def mrm_arbiter_node():
    node = MrmArbiterNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def mrm_arbiter_node_alive(hal_node):
    if not mrm_arbiter_node.is_alive():
        pytest.skip("Нода /mrm_arbiter не запущена")
    return mrm_arbiter_node

# General_Intregation
# =============================================================================


# =============================================================================
# Perception

#"TC-PER-PRE-001"
@pytest.fixture(scope="module")
def perception_boom_barrier_detector_node():
    node = BoomBarrierDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_boom_barrier_detector_node_alive(perception_boom_barrier_detector_node):
    if not perception_boom_barrier_detector_node.is_alive():
        pytest.skip("Нода /perception/boom_barrier_detector не запущена")
    return perception_boom_barrier_detector_node

# "TC-PER-PRE-002"
@pytest.fixture(scope="module")
def perception_box_segmentation_fusion_node():
    node = BoxSegmentationFusionNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_box_segmentation_fusion_node_alive(perception_box_segmentation_fusion_node):
    if not perception_boom_barrier_detector_node.is_alive():
        pytest.skip("Нода /perception/box_segmentation_fusion не запущена")
    return perception_box_segmentation_fusion_node

# "TC-PER-PRE-003"
@pytest.fixture(scope="module")
def perception_camera_detects_fusing_node():
    node = CameraDetectsFusingNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_camera_detects_fusing_node_alive(perception_camera_detects_fusing_node):
    if not perception_camera_detects_fusing_node.is_alive():
        pytest.skip("Нода /perception/camera_detects_fusing не запущена")
    return perception_camera_detects_fusing_node

# "TC-PER-PRE-004"
@pytest.fixture(scope="module")
def perception_camera_map_detector_node():
    node = СameraMapDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_camera_map_detector_node_alive(perception_camera_map_detector_node):
    if not perception_camera_map_detector_node.is_alive():
        pytest.skip("Нода /perception/camera_map_detector не запущена")
    return perception_camera_map_detector_node

# "TC-PER-PRE-005"
@pytest.fixture(scope="module")
def perception_camera_tracker_cpp_node():
    node = CameraTrackerCppNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_camera_tracker_cpp_node_alive(perception_camera_tracker_cpp_node):
    if not perception_camera_tracker_cpp_node.is_alive():
        pytest.skip("Нода /perception/camera_tracker_cpp не запущена")
    return perception_camera_tracker_cpp_node

# "TC-PER-PRE-006"
@pytest.fixture(scope="module")
def perception_camera_tracks_merger_node():
    node = СameraTracksMergerNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_camera_tracks_merger_node_alive(perception_camera_tracks_merger_node):
    if not perception_camera_tracks_merger_node.is_alive():
        pytest.skip("Нода /perception/camera_tracks_merger не запущена")
    return perception_camera_tracks_merger_node

# "TC-PER-PRE-007"
@pytest.fixture(scope="module")
def perception_cloud_motion_detector_node():
    node = CloudMotionDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_cloud_motion_detector_node_alive(perception_cloud_motion_detector_node):
    if not perception_cloud_motion_detector_node.is_alive():
        pytest.skip("Нода /perception/cloud_motion_detector не запущена")
    return perception_cloud_motion_detector_node


# "TC-PER-PRE-008"
@pytest.fixture(scope="module")
def perception_detector_3d_node():
    node = Detector3dNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def erception_detector_3d_node_alive(perception_detector_3d_node):
    if not perception_detector_3d_node.is_alive():
        pytest.skip("Нода /perception/detector_3d не запущена")
    return perception_detector_3d_node


# "TC-PER-PRE-009"
@pytest.fixture(scope="module")
def perception_front_backbone_node():
    node = FrontBackboneNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_front_backbone_node_alive(perception_front_backbone_node):
    if not perception_front_backbone_node.is_alive():
        pytest.skip("Нода /perception/front_backbone не запущена")
    return perception_front_backbone_node

# "TC-PER-PRE-010"
@pytest.fixture(scope="module")
def perception_image_segmenter_cpp_node():
    node = ImageSegmenterNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_image_segmenter_cpp_node_alive(perception_image_segmenter_cpp_node):
    if not perception_image_segmenter_cpp_node.is_alive():
        pytest.skip("Нода /perception/image_segmenter_cpp не запущена")
    return perception_image_segmenter_cpp_node

# "TC-PER-PRE-011"
@pytest.fixture(scope="module")
def perception_lidar_blind_zones_node():
    node = LidarBlindZonesNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_lidar_blind_zones_node_alive(perception_lidar_blind_zones_node):
    if not perception_lidar_blind_zones_node.is_alive():
        pytest.skip("Нода /perception/lidar_blind_zones не запущена")
    return perception_lidar_blind_zones_node

# "TC-PER-PRE-012"
@pytest.fixture(scope="module")
def perception_lidar_noise_detector_node():
    node = LidarNoiseDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_lidar_noise_detector_node_alive(perception_lidar_noise_detector_node):
    if not perception_lidar_noise_detector_node.is_alive():
        pytest.skip("Нода /perception/lidar_noise_detector не запущена")
    return perception_lidar_noise_detector_node

# "TC-PER-PRE-013"
@pytest.fixture(scope="module")
def perception_static_obstacles_tracker_node():
    node = StaticObstaclesTrackerNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_static_obstacles_tracker_node_alive(perception_static_obstacles_tracker_node):
    if not perception_static_obstacles_tracker_node.is_alive():
        pytest.skip("Нода /perception/static_obstacles_tracker не запущена")
    return perception_static_obstacles_tracker_node

# "TC-PER-PRE-014"
@pytest.fixture(scope="module")
def perception_point_cloud_clusterizer_node():
    node = PointCloudClusterizerNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_point_cloud_clusterizer_node_alive(perception_point_cloud_clusterizer_node):
    if not perception_point_cloud_clusterizer_node.is_alive():
        pytest.skip("Нода /perception/point_cloud_clusterizer не запущена")
    return perception_point_cloud_clusterizer_node

# "TC-PER-PRE-015"
@pytest.fixture(scope="module")
def perception_pollution_detector_node():
    node = PollutionDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_pollution_detector_node_alive(perception_pollution_detector_node):
    if not perception_pollution_detector_node.is_alive():
        pytest.skip("Нода /perception/pollution_detector не запущена")
    return perception_pollution_detector_node

# "TC-PER-PRE-016"
@pytest.fixture(scope="module")
def perception_radar_static_obstacles_detector_node():
    node = RadarStaticObstaclesDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_radar_static_obstacles_detector_node_alive(perception_radar_static_obstacles_detector_node):
    if not perception_radar_static_obstacles_detector_node.is_alive():
        pytest.skip("Нода /perception/radar_static_obstacles_detector не запущена")
    return perception_radar_static_obstacles_detector_node

# "TC-PER-PRE-017"
@pytest.fixture(scope="module")
def perception_road_lines_3d_node():
    node = RoadLines3dNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_road_lines_3d_node_alive(perception_road_lines_3d_node):
    if not perception_road_lines_3d_node.is_alive():
        pytest.skip("Нода /perception/road_lines_3d не запущена")
    return perception_road_lines_3d_node

# "TC-PER-PRE-018"
@pytest.fixture(scope="module")
def perception_road_lines_tracker_node():
    node = RoadLinesTrackerNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_road_lines_tracker_node_alive(perception_road_lines_tracker_node):
    if not perception_road_lines_tracker_node.is_alive():
        pytest.skip("Нода /perception/road_lines_tracker не запущена")
    return perception_road_lines_tracker_node

# "TC-PER-PRE-019"
@pytest.fixture(scope="module")
def perception_road_surface_condition_detector_node():
    node = RoadSurfaceConditionDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_road_surface_condition_detector_node_alive(perception_road_surface_condition_detector_node):
    if not perception_road_surface_condition_detector_node.is_alive():
        pytest.skip("Нода /perception/road_surface_condition_detector не запущена")
    return perception_road_surface_condition_detector_node

# "TC-PER-PRE-020"
@pytest.fixture(scope="module")
def perception_roadworks_fusion_node():
    node = RoadworksFusionNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_roadworks_fusion_node_alive(perception_roadworks_fusion_node):
    if not perception_roadworks_fusion_node.is_alive():
        pytest.skip("Нода /perception/roadworks_fusion не запущена")
    return perception_roadworks_fusion_node

# "TC-PER-PRE-021"
@pytest.fixture(scope="module")
def perception_segmentation_hdmap_fusion_node():
    node = SegmentationHdmapFusionNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_segmentation_hdmap_fusion_node_alive(perception_segmentation_hdmap_fusion_node):
    if not perception_segmentation_hdmap_fusion_node.is_alive():
        pytest.skip("Нода /perception/perception_segmentation_hdmap_fusion_node не запущена")
    return perception_segmentation_hdmap_fusion_node

# "TC-PER-PRE-022"
@pytest.fixture(scope="module")
def perception_signals_classifier_node():
    node = SignalsСlassifierNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_perception_signals_classifier_node_alive(perception_signals_classifier_node):
    if not perception_signals_classifier_node.is_alive():
        pytest.skip("Нода /perception/signals_classifier не запущена")
    return perception_signals_classifier_node

# "TC-PER-PRE-023"
@pytest.fixture(scope="module")
def perception_speed_limit_classifier_node():
    node = SpeedLimitClassifierNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_speed_limit_classifier_node_alive(perception_speed_limit_classifier_node):
    if not perception_speed_limit_classifier_node.is_alive():
        pytest.skip("Нода /perception/speed_limit_classifier не запущена")
    return perception_speed_limit_classifier_node


# "TC-PER-PRE-024"
@pytest.fixture(scope="module")
def perception_traffic_light_detects_node():
    node = TrafficLightDetectsNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_traffic_light_detects_node_alive(perception_traffic_light_detects_node):
    if not perception_traffic_light_detects_node.is_alive():
        pytest.skip("Нода /perception/traffic_light_detects не запущена")
    return perception_traffic_light_detects_node

# "TC-PER-PRE-025"
@pytest.fixture(scope="module")
def perception_traffic_sign_detects_node():
    node = TrafficSignDetectsNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_traffic_sign_detects_node_alive(perception_traffic_sign_detects_node):
    if not perception_traffic_sign_detects_node.is_alive():
        pytest.skip("Нода /perception/traffic_sign_detects не запущена")
    return perception_traffic_sign_detects_node

# "TC-PER-PRE-026"
@pytest.fixture(scope="module")
def perception_traffic_sign_localization_node():
    node = TrafficSignLocalizationNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_perception_traffic_sign_localization_node_alive(perception_traffic_sign_localization_node):
    if not perception_traffic_sign_localization_node.is_alive():
        pytest.skip("Нода /perception/traffic_sign_localization не запущена")
    return perception_traffic_sign_localization_node

# "TC-PER-PRE-027"
@pytest.fixture(scope="module")
def perception_vehicle_detects_node():
    node = VehicleDetectsNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_vehicle_detects_node_alive(perception_vehicle_detects_node):
    if not perception_vehicle_detects_node.is_alive():
        pytest.skip("Нода /perception/vehicle_detects не запущена")
    return perception_vehicle_detects_node

# "TC-PER-PRE-028"
@pytest.fixture(scope="module")
def perception_lidar_static_obstacles_detector_node():
    node = LidarStaticObstaclesDetectorNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_lidar_static_obstacles_detector_node_alive(perception_lidar_static_obstacles_detector_node):
    if not perception_lidar_static_obstacles_detector_node.is_alive():
        pytest.skip("Нода /lidar_static_obstacles_detector не запущена")
    return perception_lidar_static_obstacles_detector_node

# "TC-PER-PRE-029"
@pytest.fixture(scope="module")
def perception_visualization_cloud_clusters_visualization_node():
    node = CloudClustersVisualizationNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_visualization_cloud_clusters_visualization_node_alive(perception_visualization_cloud_clusters_visualization_node):
    if not perception_visualization_cloud_clusters_visualization_node.is_alive():
        pytest.skip("Нода /cloud_clusters_visualization не запущена")
    return perception_visualization_cloud_clusters_visualization_node

# "TC-PER-PRE-030"
@pytest.fixture(scope="module")
def perception_visualization_perception_lanes_visualization_py_node():
    node = PerceptionLanesVisualizationPyNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_visualization_perception_lanes_visualization_py_node_alive(perception_visualization_perception_lanes_visualization_py_node):
    if not perception_visualization_perception_lanes_visualization_py_node.is_alive():
        pytest.skip("Нода /perception_lanes_visualization_py не запущена")
    return perception_visualization_perception_lanes_visualization_py_node

# "TC-PER-PRE-031"
@pytest.fixture(scope="module")
def perception_visualization_perception_visualization_2d_node():
    node = PerceptionVisualization2dNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_visualization_perception_visualization_2d_node_alive(perception_visualization_perception_visualization_2d_node):
    if not perception_visualization_perception_visualization_2d_node.is_alive():
        pytest.skip("Нода /perception_visualization_2d не запущена")
    return perception_visualization_perception_visualization_2d_node

# "TC-PER-PRE-032"
@pytest.fixture(scope="module")
def perception_traffic_light_pipeline_node():
    node = TrafficLightPipelineNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_traffic_light_pipeline_node_alive(perception_traffic_light_pipeline_node):
    if not perception_traffic_light_pipeline_node.is_alive():
        pytest.skip("Нода /traffic_light_pipeline_node не запущена")
    return perception_traffic_light_pipeline_node

# "TC-PER-PRE-033"
@pytest.fixture(scope="module")
def perception_visualization_objects_visualization_node():
    node = ObjectsVisualizationNode(); node.setup(); yield node; node.teardown()

@pytest.fixture(scope="module")
def perception_visualization_objects_visualization_node_alive(perception_visualization_objects_visualization_node):
    if not perception_visualization_objects_visualization_node.is_alive():
        pytest.skip("Нода /objects_visualization_node не запущена")
    return perception_visualization_objects_visualization_node

# Perception
# =============================================================================

@pytest.fixture(scope="session", autouse=True)
def mrm_monitor():
    monitor = MrmRequestMonitor(container=DOCKER_CONTAINER)
    monitor.start()
    if not monitor.wait_ready(timeout=15):
        pytest.fail("Топик /safety/mrm_request не публикует сообщения")
    yield monitor
    monitor.stop()

@pytest.fixture(scope="module")
def auto_cleaning_node_alive(auto_cleaning_node):
    if not auto_cleaning_node.is_alive():
        pytest.skip("Нода /sensing/auto_cleaning не запущена")
    return auto_cleaning_node




def pytest_html_report_title(report):
    report.title = "HIL Fault Injection — Sensing Component"

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # Добавляем дополнительные колонки
    report.expected = getattr(item, 'expected', '—')
    report.actual = getattr(item, 'actual', '—')
    report.reaction_ms = getattr(item, 'reaction_ms', '—')  # ← добавить

def pytest_html_results_table_header(cells):
    cells.insert(2, '<th>Ожидаемый результат</th>')
    cells.insert(3, '<th>Фактический результат</th>')
    cells.insert(4, '<th>Время реакции</th>')

def pytest_html_results_table_row(report, cells):
    cells.insert(2, f'<td>{getattr(report, "expected", "—")}</td>')
    cells.insert(3, f'<td>{getattr(report, "actual", "—")}</td>')
    cells.insert(4, f'<td>{getattr(report, "reaction_ms", "—")}</td>')

import subprocess
import time

@pytest.fixture()
def restart_autopilot_after(mrm_monitor):
    """
    Перезапускает автопилот после теста.
    Использовать только в kill тестах.
    """
    yield

    subprocess.run(
        ["docker", "exec", DOCKER_CONTAINER,
         "bash", "-c", "pkill -2 -f 'drive'"],
        capture_output=True
    )
    print(f"\nАвтопилот остановлен. Перезапускаем...")
    time.sleep(60)

    subprocess.Popen(
        ["docker", "exec", "-d", DOCKER_CONTAINER,
         "bash", "-c",
         "cd /rep && "
         "source /opt/ros/humble/setup.bash && "
         "source /rep/ros2/install/setup.bash && "
         "drive classic-planner -u postoev --no-ecu-update"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    result = mrm_monitor.wait_for_mrm_type_change(
        from_value="2",
        to_value="0",
        timeout=120.0,
        poll_interval=0.5
    )

    if result["success"]:
        print(f"Автопилот готов. mrm_type=0 ✅")
        time.sleep(30)  # ← ждём пока все ноды поднимутся
        print(f"Автопилот готов. Следующий тест можно запускать ✅")
    else:
        pytest.fail("Автопилот не перезапустился за 60 секунд")