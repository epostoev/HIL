import json
import time
import pytest
import allure


PERCEPTION_NODES = [
        ("perception_boom_barrier_detector_node",                               "TC-PER-PRE-001", "/perception/boom_barrier_detector"),
        ("perception_box_segmentation_fusion_node",                             "TC-PER-PRE-002", "/perception/box_segmentation_fusion"),
        # ("perception_camera_detects_fusing_node",                               "TC-PER-PRE-003", "/perception/camera_detects_fusing"),
        ("perception_camera_map_detector_node",                                 "TC-PER-PRE-004", "/perception/camera_map_detector"),
        ("perception_camera_tracker_cpp_node",                                  "TC-PER-PRE-005", "/perception/camera_tracker_cpp"),
        ("perception_camera_tracks_merger_node",                                "TC-PER-PRE-006", "/perception/camera_tracks_merger"),
        ("perception_cloud_motion_detector_node",                               "TC-PER-PRE-007", "/perception/cloud_motion_detector"),
        ("perception_detector_3d_node",                                         "TC-PER-PRE-008", "/perception/detector_3d"),
        # ("perception_front_backbone_node",                                      "TC-PER-PRE-009", "/perception/front_backbone"),
        ("perception_image_segmenter_cpp_node",                                 "TC-PER-PRE-010", "/perception/image_segmenter_cpp"),
        ("perception_lidar_blind_zones_node",                                   "TC-PER-PRE-011", "/perception/lidar_blind_zones"),
        ("perception_lidar_noise_detector_node",                                "TC-PER-PRE-012", "/perception/lidar_noise_detector"),
        # ("perception_static_obstacles_tracker_node",                            "TC-PER-PRE-013", "/perception/static_obstacles_tracker"),
        ("perception_point_cloud_clusterizer_node",                             "TC-PER-PRE-014", "/perception/point_cloud_clusterizer"),
        ("perception_pollution_detector_node",                                  "TC-PER-PRE-015", "/perception/pollution_detector"),
        ("perception_radar_static_obstacles_detector_node",                     "TC-PER-PRE-016", "/perception/radar_static_obstacles_detector"),
        ("perception_road_lines_3d_node",                                       "TC-PER-PRE-017", "/perception/road_lines_3d"),
        ("perception_road_lines_tracker_node",                                  "TC-PER-PRE-018", "/perception/road_lines_tracker"),
        ("perception_road_surface_condition_detector_node",                     "TC-PER-PRE-019", "/perception/road_surface_condition_detector"),
        ("perception_roadworks_fusion_node",                                    "TC-PER-PRE-020", "/perception/roadworks_fusion"),
        # ("perception_segmentation_hdmap_fusion_node",                           "TC-PER-PRE-021", "/perception/segmentation_hdmap_fusion_node"),
        ("perception_signals_classifier_node",                                  "TC-PER-PRE-022", "/perception/signals_classifier"),
        ("perception_speed_limit_classifier_node",                              "TC-PER-PRE-023", "/perception/speed_limit_classifier"),
        # ("perception_traffic_light_detects_node",                               "TC-PER-PRE-024", "/perception/traffic_light_detects"),
        # ("perception_traffic_sign_detects_node",                                "TC-PER-PRE-025", "/perception/traffic_sign_detects"),
        ("perception_traffic_sign_localization_node",                           "TC-PER-PRE-026", "/perception/traffic_sign_localization"),
        # ("perception_vehicle_detects_node",                                     "TC-PER-PRE-027", "/perception/vehicle_detects"),
        ("perception_lidar_static_obstacles_detector_node",                     "TC-PER-PRE-028", "/perception/lidar_static_obstacles_detector"),
        ("perception_visualization_cloud_clusters_visualization_node",          "TC-PER-PRE-029", "/perception/visualization/cloud_clusters_visualization"),
        ("perception_visualization_perception_lanes_visualization_py_node",     "TC-PER-PRE-030", "/perception/visualization/perception_lanes_visualization_py"),
        ("perception_visualization_perception_visualization_2d_node",           "TC-PER-PRE-031", "/perception/visualization/perception_visualization_2d"),
        # ("perception_traffic_light_pipeline_node",                              "TC-PER-PRE-032", "/perception/traffic_light_pipeline"),
        ("perception_visualization_objects_visualization_node",                 "TC-PER-PRE-033", "/visualization/objects_visualization")
]

class TestIPerceptionKill:

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", PERCEPTION_NODES)
    def test_integration_kill(self, fixture_name, tc_id, node_name,
                              mrm_monitor, request, restart_autopilot_after):

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "mrm_type: 0 → 2. Время реакции < 5000ms"

        if not node.is_alive():
            pytest.skip(f"Нода {node_name} не запущена")

        with allure.step("Снять baseline: mrm_type, shadow_mrm_type, drive_mode"):
            baseline = mrm_monitor.get_fields(["mrm_type", "shadow_mrm_type", "drive_mode"])
            node.logger.info(f"Baseline mrm_type={baseline['mrm_type']}")
            allure.attach(
                f"mrm_type:        {baseline['mrm_type']}\n"
                f"shadow_mrm_type: {baseline['shadow_mrm_type']}\n"
                f"drive_mode:      {baseline['drive_mode']}",
                name="Baseline",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step(f"Получить PID ноды {node_name}"):
            pid_before = node.get_pid()
            node.logger.info(f"PID={pid_before}")
            allure.attach(
                str(pid_before),
                name="PID до kill",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Зафиксировать timestamp перед kill"):
            before_stamp = mrm_monitor.get_stamp()
            node.logger.info(f"Stamp ДО kill: {before_stamp}")

        with allure.step(f"Отправить kill -6 PID={pid_before}"):
            node.run_docker_command(f"kill -6 {pid_before}")
            node.logger.info(
                f"kill -6 отправлен PID={pid_before}. "
                f"Ждём изменения mrm_type..."
            )

        with allure.step("Ожидать mrm_type: 0 → 2 (timeout=10s)"):
            result = mrm_monitor.wait_for_mrm_type_change(
                from_value="0",
                to_value="2",
                before_stamp=before_stamp,
                timeout=10.0,
                poll_interval=0.01
            )
            node.logger.info(
                f"Результат: success={result['success']}, "
                f"reaction={result['reaction_ms']}ms "
                f"({result['reaction_ns']}ns), "
                f"mrm_type={result['mrm_type']}"
            )
            allure.attach(
                f"success:      {result['success']}\n"
                f"mrm_type:     {result['mrm_type']}\n"
                f"reaction_ms:  {result['reaction_ms']}ms\n"
                f"reaction_ns:  {result['reaction_ns']}ns",
                name="Результат ожидания MRM",
                attachment_type=allure.attachment_type.TEXT,
            )

        with allure.step("Собрать error_codes после kill"):
            error_codes = mrm_monitor.get_error_codes()
            triggered_errors = [
                e for e in error_codes
                if e["details"] != "{}"
            ]
            node.logger.info(f"Triggered errors: {len(triggered_errors)}")
            for e in triggered_errors:
                node.logger.info(
                    f"  {e['error_code_hex']} ({e['error_code']}): "
                    f"{e['details'][:80]}"
                )
            errors_text = "\n".join([
                f"{e['error_code_hex']} ({e['error_code']}): {e['details'][:80]}"
                for e in triggered_errors
            ]) or "нет"
            allure.attach(
                errors_text,
                name=f"Triggered errors ({len(triggered_errors)})",
                attachment_type=allure.attachment_type.TEXT,
            )
            # Сохраняем error_codes в файл и прикрепляем к отчёту
            log_path = f"/tmp/error_codes_{node_name.replace('/', '_')}.json"
            with open(log_path, "w") as f:
                json.dump(triggered_errors, f, indent=2, ensure_ascii=False)
            allure.attach.file(
                log_path,
                name=f"error_codes_{node_name}",
                attachment_type=allure.attachment_type.JSON,
            )

        with allure.step("Проверить наличие авторестарта ноды (fault tolerance)"):
            time.sleep(3)
            if node.is_alive():
                node.has_auto_restart = True
                node.logger.info(
                    "drive.py перезапустил ноду. "
                    "Fault tolerance: ПОДТВЕРЖДЁН ✅"
                )
                allure.attach(
                    f"Нода {node_name} перезапущена автоматически\n"
                    "Fault Tolerance: ПОДТВЕРЖДЁН ✅",
                    name="Fault Tolerance",
                    attachment_type=allure.attachment_type.TEXT,
                )
            else:
                allure.attach(
                    f"Авторестарт {node_name} не обнаружен за 3 секунды",
                    name="Fault Tolerance",
                    attachment_type=allure.attachment_type.TEXT,
                )

        with allure.step("Проверить assert: mrm_type изменился на '2'"):
            assert result["success"], (
                f"mrm_type не изменился на '2'. "
                f"Текущее значение: {result['mrm_type']}"
            )

        with allure.step("Проверить SLA: время реакции < 5000ms"):
            assert result["reaction_ms"] < 5000, (
                f"Время реакции {result['reaction_ms']}ms превышает "
                f"заявленный SLA 5000ms"
            )

        errors_str = " | ".join([
            f"{e['error_code_hex']}: {e['details'][:50]}"
            for e in triggered_errors
        ]) or "нет"

        request.node.actual = (
            f"mrm_type: {baseline['mrm_type']} → {result['mrm_type']}. "
            f"Ошибки: {errors_str} ✅"
        )
        request.node.reaction_ms = f"{result['reaction_ms']}ms"

        if node.has_auto_restart:
            node.logger.info(
                f"Fault tolerance: ПОДТВЕРЖДЁН ✅ "
                f"Время реакции MRM: {result['reaction_ms']}ms"
            )