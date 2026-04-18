from __future__ import annotations

import logging

from picamera2 import Picamera2
from spade.agent import Agent

from agent.camera import CameraBehaviour

from .AlphaBot2 import AlphaBot2

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("AlphaBotAgent")

# Enable SPADE and XMPP specific logging
for log_name in ["spade", "aioxmpp", "xmpp"]:
    log = logging.getLogger(log_name)
    log.setLevel(logging.DEBUG)
    log.propagate = True


class RobotAgent(Agent):
    bot: AlphaBot2
    cam: Picamera2

    async def setup(self):
        self.bot = AlphaBot2()
        cam = Picamera2()

        config = cam.create_preview_configuration(
            main={"format": "RGB888", "size": (2592, 1944)}
        )
        cam.configure(config)
        cam.start()

        self.add_behaviour(CameraBehaviour("logger@isc-coordinator.lan"))

    async def stop(self) -> None:
        self.cam.stop()
        return await super().stop()
