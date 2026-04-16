from __future__ import annotations

import datetime
import logging

from picamera2 import Picamera2
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour

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

    class IRSensorReader(PeriodicBehaviour):
        agent: RobotAgent

        async def on_start(self):
            self.bot: AlphaBot2 = self.agent.bot

        async def run(self):
            logger.debug("[Behaviour] Reading IR sensor")
            right: bool = self.bot.getIRSensorRight()
            left: bool = self.bot.getIRSensorLeft()
            logger.info(f"[Behaviour] RIR {right=} {left=}")

            if right and left:
                logger.debug("[Agent] Stopping")
                self.bot.stop()
            elif not right and left:
                logger.debug("[Agent] Turning left")
                self.bot.left()
            elif right and not left:
                logger.debug("[Agent] Turning right")
                self.bot.right()
            elif not right and not left:
                logger.debug("[Agent] Moving forward")
                self.bot.forward()

    async def setup(self):
        self.bot = AlphaBot2()
        cam = Picamera2()

        config = cam.create_preview_configuration(
            main={"format": "RGB888", "size": (2592, 1944)}
        )
        cam.configure(config)
        cam.start()

        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        sensor_behavior = self.IRSensorReader(period=1, start_at=start_at)

        self.add_behaviour(sensor_behavior)

    async def stop(self) -> None:
        self.cam.stop()
        return await super().stop()
