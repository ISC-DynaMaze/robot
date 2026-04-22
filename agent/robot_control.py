from __future__ import annotations
import asyncio
import logging
import json
import numpy as np
from pathlib import Path
import datetime
from math import pi as PI
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, OneShotBehaviour
from spade.message import Message
from .AlphaBot2 import AlphaBot2

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

    def __init__(
        self,
        *args,
        logger_jid: str = "logger@isc-coordinator.lan",
        camera_res: tuple[int, int] = (720, 540),
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.logger_jid: str = logger_jid
        self.camera_res: tuple[int, int] = camera_res

    async def setup(self):
        self.bot = AlphaBot2()
        self.cam = Picamera2()

        config = self.cam.create_preview_configuration(
            main={"format": "RGB888", "size": self.camera_res}
        )
        self.cam.configure(config)
        self.cam.start()

        self.add_behaviour(CameraBehaviour(self.logger_jid))

    async def stop(self) -> None:
        self.cam.stop()
        return await super().stop()
    class TargetAngleCalibrationBehaviour(OneShotBehaviour):
        def __init__(self, time, speed=20, delta_t = 0.05):
            super().__init__()
            self.actual_angle = None
            self.speed = speed
            self.time = time
            self.delta_t = delta_t

        async def on_start(self):
            self.bot: AlphaBot2 = self.agent.bot

        async def run(self):
            self.actual_angle = await self.ask_angle()
            if self.actual_angle is None:
                logger.info(f"[Behaviour] No angle given")
                return
            self.bot.setBothPWM(self.speed)
            angle_history = [self.actual_angle]
            delta_history = []
            await self.calibration_sequence(angle_history,delta_history)
            for i in range(7):
                await self.calibration_sequence(angle_history, delta_history, self.delta_t)
            logger.info(f"[Calibration result] : {delta_history}")
            test = self.interpolate(delta_history)

            logger.info(f"[Interpolate] : {test}")
            self.test_sequence(test)
            self.save_result()

        async def ask_angle(self):
            logger.debug("[Behaviour] Ask controller for actual angle")

            msg = Message(to="alberto-ctrl@isc-coordinator.lan")
            msg.set_metadata("performative", "inform")
            msg.set_metadata("ontology", "calibration")
            msg.body = "actual_angle"
            await self.send(msg)

            reply = await self.receive(timeout=15.0)

            if reply:
                try:
                    actual_angle = json.loads(reply.body)["angle"]
                    return actual_angle
                except:
                    logger.debug("[Behaviour] Angle format is not correct")
            else:
                logger.debug("[Behaviour] No response from controller")

        async def calibration_sequence(self, angle_history, delta_history, delta_t = 0.0):
                logger.info(f"[Time] Time : {self.time}")
                logger.info(f"[Time] Additional time : {delta_t}")
                logger.info(f"[Behaviour] Robot turn left for {self.time+delta_t} second(s)")
                self.bot.left()
                await asyncio.sleep(self.time+delta_t)
                self.time += delta_t
                self.bot.stop()
                await asyncio.sleep(1)
                logger.info("[Behaviour] Robot Stop")
                self.actual_angle = await self.ask_angle()
                angle_history.append(self.actual_angle)
                delta = abs(((angle_history[-2]-angle_history[-1]+180)%360)-180)
                delta_history.append([delta,self.time])

        def interpolate(self, delta_history):
            x = []
            y = []
            for c in delta_history:
                x.append(c[0])
                y.append(c[1])
            print(x)
            print(y)
            return np.interp([45,90,135],x,y)
        
        async def test_sequence(self, test):
            test_angle_history = []
            test_delta_history = []
            for t in test :
                self.actual_angle = await self.ask_angle()
                test_angle_history.append(self.actual_angle)
                self.bot.left()
                await asyncio.sleep(t)
                self.bot.stop()
                self.actual_angle = await self.ask_angle()
                test_angle_history.append(self.actual_angle)
                test_delta_history.append(((test_angle_history[-2]-test_angle_history[-1]+180)%360)-180)
            self.bot.stop()
            return test_delta_history
        
        def save_result(self, delta_history,test_delta_history):
            data = dict()
            data["speed"] = self.speed
            data["measure"] = {a : t for a,t in delta_history}
            data["test"] = {a : t for a,t in test_delta_history}
            
            save_path = Path("test_result")
            save_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = str(save_path / f"debug_{timestamp}.json")
            json.dump(data,filename)
                
    async def setup(self):
        self.bot = AlphaBot2()
        calibration_behavior = self.TargetAngleCalibrationBehaviour(0.1)
        
        self.add_behaviour(calibration_behavior)
