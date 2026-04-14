import asyncio
import logging
import datetime
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
    
    class IRSensorReader(PeriodicBehaviour):
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
        start_at = datetime.datetime.now() + datetime.timedelta(seconds=5)
        sensor_behavior = self.IRSensorReader(period=1, start_at=start_at)
        
        self.add_behaviour(sensor_behavior)
