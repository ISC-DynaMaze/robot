import json
from pathlib import Path

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour

from agent.camera import CameraPanTiltBehaviour

class MessageListenerBehaviour(CyclicBehaviour):
    agent: Agent

    def __init__(self, save_dir: Path):
        super().__init__()
        self.save_dir: Path = save_dir
        self.save_dir.mkdir(parents=True, exist_ok=True)

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

        #if msg_type == "bot-img":
        #    img_data = base64.b64decode(data["img"])
        #    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        #    filename = f"photo_{timestamp}.jpg"
        #    filepath = self.save_dir / filename

        #    # Save the received image
        #    async with aiofiles.open(filepath, "wb") as img_file:
        #        await img_file.write(img_data)
        
        if msg_type == "pan-tilt-test":
            self.agent.add_behaviour(CameraPanTiltBehaviour())
