from framework.base_hil_test import BaseHILTest

class WebrtcPrimaryNode(BaseHILTest):
    NODE_NAME = "/teleops/webrtc_primary"
    PROCESS_NAME = "teleops_webrtc_streamer/lib/teleops_webrtc_streamer/webrtc_streamer"

    def __init__(self):
        super().__init__(node_name="webrtc_primary", timeout=15)

    def is_alive(self) -> bool:
        alive = self.NODE_NAME in self.get_node_list()
        self.logger.info(f"Нода {self.NODE_NAME} жива: {alive}")
        return alive