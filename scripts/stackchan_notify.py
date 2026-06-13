import asyncio
import os
import sys
import contextlib
from stackchan_mcp.gateway import Gateway
from stackchan_mcp.tts.orchestrator import synthesize_and_send

# Notification presets
PRESETS = {
    "approval": {
        "face": "surprised",
        "pitch": 40,
        "text": "主人，有任务需要审批。"
    },
    "done": {
        "face": "happy",
        "pitch": 25,
        "text": "主人，任务执行完毕，结果已经为您准备好了。"
    },
    "error": {
        "face": "sad",
        "pitch": 10,
        "text": "哎呀，代码出错了，主人快来看看吧。"
    }
}

async def notify(preset_name):
    if preset_name not in PRESETS:
        print(f"Unknown preset: {preset_name}")
        return

    preset = PRESETS[preset_name]
    os.environ["STACKCHAN_TTS_ENGINE"] = "edge"
    
    gateway = Gateway()
    async with contextlib.AsyncExitStack() as stack:
        await gateway.start()
        stack.push_async_callback(gateway.stop)
        
        # Wait for robot
        for _ in range(30):
            if gateway.esp32.device_connected:
                break
            await asyncio.sleep(1)
        
        if not gateway.esp32.device_connected:
            return

        # Execute notification
        await gateway.esp32.call_tool("self.display.set_avatar", {"face": preset["face"]})
        await gateway.esp32.call_tool("self.robot.set_head_angles", {"yaw": 0, "pitch": preset["pitch"]})
        await synthesize_and_send({"text": preset["text"]}, gateway=gateway)
        await asyncio.sleep(6) # Give it time to finish

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(notify(sys.argv[1]))
    else:
        print("Usage: python stackchan_notify.py <approval|done|error>")
