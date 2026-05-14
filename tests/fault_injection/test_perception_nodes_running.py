import pytest

PERCEPTION_NODES = [
        ("perception_boom_barrier_detector_node",          "TC-PER-PRE-001", "/perception/boom_barrier_detector"),
        ("perception_box_segmentation_fusion_node",        "TC-PER-PRE-002", "/perception/box_segmentation_fusion"),
        ("perception_camera_detects_fusing_node",          "TC-PER-PRE-003", "/perception/camera_detects_fusing"),
        ("perception_camera_map_detector_node",            "TC-PER-PRE-004", "/perception/camera_map_detector"),
        ("perception_camera_tracker_cpp_node",             "TC-PER-PRE-005", "/perception/camera_tracker_cpp"),
]

class TestPerceptionNodesRunning:
    @pytest.mark.parametrize("fixture_name, tc_id, node_name", PERCEPTION_NODES)
    def test_node_running(self, fixture_name, tc_id, node_name, request):
        f"""{tc_id}: {node_name} присутствует в ROS graph"""

        node = request.getfixturevalue(fixture_name)

        request.node.expected = f"Нода {node_name} присутствует в ROS graph"

        if not node.is_alive():
            request.node.actual = "Нода не запущена — SKIPPED"
            pytest.skip(f"Нода {node_name} не запущена")

        assert node.is_alive() is True

        request.node.actual = f"Нода {node_name} жива ✅"