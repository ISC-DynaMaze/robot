from __future__ import annotations

import asyncio
import base64
import json
from typing import TYPE_CHECKING

import aiofiles
from spade.behaviour import Message, OneShotBehaviour

from agent.PCA9685 import PCA9685

if TYPE_CHECKING:
    from robot_control import RobotAgent


class CameraBehaviour(OneShotBehaviour):
    agent: RobotAgent

    def __init__(self, requester_jid: str):
        super().__init__()
        self.requester_jid: str = requester_jid

    async def run(self) -> None:
        filename: str = "photo.jpg"
        self.agent.cam.capture_file(filename)
        async with aiofiles.open(filename, "rb") as img_file:
            img_data = await img_file.read()
            encoded_img = base64.b64encode(img_data).decode("utf-8")
        data = {"type": "bot-img", "img": encoded_img}
        msg: Message = Message(
            to=self.requester_jid,
            body=json.dumps(data),
            metadata={"performative": "inform"},
        )
        await self.send(msg)


class CameraPanTiltBehaviour(OneShotBehaviour):
    agent: RobotAgent

    MIN_ANGLE = 600
    MAX_ANGLE = 2600

    async def run(self):
        pwm = PCA9685(0x40, debug=True)
        pwm.setPWMFreq(50)
        step = 10
        while True:
            # setServoPulse(2,2500)
            for i in range(self.MIN_ANGLE, self.MAX_ANGLE, step):
                pwm.setServoPulse(0, i)
                await asyncio.sleep(0.02)
            
            for i in range(self.MAX_ANGLE, self.MIN_ANGLE, -step):
                pwm.setServoPulse(0, i)
                await asyncio.sleep(0.02)
            break
