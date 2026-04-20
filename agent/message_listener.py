import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from agent.camera import CameraPanTiltBehaviour


class MessageListenerBehaviour(CyclicBehaviour):
    agent: Agent

    async def run(self):
        msg = await self.receive(timeout=9999)
        if msg is not None and msg.body is not None:
            await self.process_message(msg.body)

    async def process_message(self, msg: str):
        try:
            data = json.loads(msg)
        except:
            return

        msg_type: str = data.get("type")

        if msg_type == "pan-tilt-test":
            self.agent.add_behaviour(CameraPanTiltBehaviour())
        
        elif msg_type == "stop":
            await self.agent.stop()
