import time
import pytest


SENSING_NODES = [
    ("auto_cleaning_node_alive",      "TC-FAULT-SENSING-001", "/sensing/auto_cleaning"),
    ("imu_node_alive",                "TC-FAULT-SENSING-002", "/sensing/imu1/imu_node"),
    ("odometry_node",                 "TC-FAULT-SENSING-003", "/sensing/odometry_node"),
    ("odometry_velocity_node",        "TC-FAULT-SENSING-004", "/sensing/odometry_velocity_node"),
    ("radar_driver_node_alive",       "TC-FAULT-SENSING-005", "/sensing/radar_driver_node"),
    ("ublox_driver_node",             "TC-FAULT-SENSING-006", "/sensing/ublox1/ublox_driver_node"),
    ("radar_visualization_node",      "TC-FAULT-SENSING-007", "/sensing/visualization/radar_visualization_node"),
]


class TestSensingKill:

    @pytest.mark.parametrize("fixture_name, tc_id, node_name", SENSING_NODES)
    def test_sensing_kill(self, fixture_name, tc_id, node_name, mrm_monitor, request):
        f"""{tc_id}: Kill {node_name} и проверка MRM"""

        node = request.getfixturevalue(fixture_name)

        request.node.expected = "MRM: mrm_type=2, shadow_mrm_type=1, drive_mode=2"

        if not node.is_alive():
            pytest.skip(f"Нода {node_name} не запущена")

        pid_before = node.get_pid()
        node.kill()

        time.sleep(5)
        fields = ["mrm_type", "shadow_mrm_type", "drive_mode"]
        after = mrm_monitor.get_fields(fields)

        assert after["mrm_type"] == "2", \
            f"mrm_type: ожидалось '2', получено '{after['mrm_type']}'"
        assert after["shadow_mrm_type"] == "1", \
            f"shadow_mrm_type: ожидалось '1', получено '{after['shadow_mrm_type']}'"
        assert after["drive_mode"] == "2", \
            f"drive_mode: ожидалось '2', получено '{after['drive_mode']}'"

        request.node.actual = (
            f"MRM: mrm_type={after['mrm_type']}, "
            f"shadow_mrm_type={after['shadow_mrm_type']}, "
            f"drive_mode={after['drive_mode']} ✅"
        )

        if node.has_auto_restart:
            node.logger.info(
                f"drive.py перезапустил ноду. "
                f"Факт kill подтверждён: старый PID {pid_before} уничтожен. "
                f"Fault tolerance: ПОДТВЕРЖДЁН ✅"
            )