import asyncio
import os
import contextlib
import json
from aiohttp import web
from stackchan_mcp.gateway import Gateway
from stackchan_mcp.tts.orchestrator import synthesize_and_send

# Notification presets
PRESETS = {
    "approval": {
        "face": "surprised",
        "pitch": 40,
        "text": "Lorrie，有任务需要审批。"
    },
    "done": {
        "face": "happy",
        "pitch": 25,
        "text": "Lorrie，任务执行完毕，结果已经为您准备好了。"
    },
    "error": {
        "face": "sad",
        "pitch": 10,
        "text": "哎呀，代码出错了，Lorrie快来看看吧。"
    }
}

async def play_and_clear_speech(gateway, preset):
    # Set the text bubble
    await gateway.esp32.call_tool("self.display.set_speech_bubble", {"text": preset["text"]})
    # Wait for audio to finish playing
    await synthesize_and_send({"text": preset["text"]}, gateway=gateway)
    # Clear the text bubble
    await gateway.esp32.call_tool("self.display.set_speech_bubble", {"text": ""})
    # Reset face to idle and mouth to closed
    await gateway.esp32.call_tool("self.display.set_avatar", {"face": "idle"})
    await gateway.esp32.call_tool("self.display.set_mouth", {"mouth": "closed"})
    # Reset head posture to straight ahead (looking up)
    await gateway.esp32.call_tool("self.robot.set_head_angles", {"yaw": 0, "pitch": 40})

async def handle_notify(request):
    try:
        data = await request.json()
        gateway = request.app["gateway"]
        
        # Determine settings from preset or direct input
        preset_name = data.get("preset")
        if preset_name == "reset":
            if gateway.esp32.device_connected:
                await gateway.esp32.call_tool("self.display.set_avatar", {"face": "idle"})
                await gateway.esp32.call_tool("self.display.set_mouth", {"mouth": "closed"})
                await gateway.esp32.call_tool("self.display.set_speech_bubble", {"text": ""})
                return web.Response(text="OK")
            return web.Response(text="Device disconnected", status=400)

        if preset_name == "reboot":
            if gateway.esp32.device_connected:
                await gateway.esp32.call_tool("self.reboot", {})
                return web.Response(text="Rebooting")
            return web.Response(text="Device disconnected", status=400)

        if preset_name and preset_name in PRESETS:
            preset = PRESETS[preset_name]
            text = preset["text"]
            face = preset["face"]
            pitch = preset["pitch"]
        else:
            text = data.get("text", "你好，Lorrie。")
            face = data.get("face", "happy")
            pitch = data.get("pitch", 25)

        if gateway.esp32.device_connected:
            await gateway.esp32.call_tool("self.display.set_avatar", {"face": face})
            await gateway.esp32.call_tool("self.robot.set_head_angles", {"yaw": 0, "pitch": pitch})

            # Run synthesize_and_send and clear bubble as a background task
            asyncio.create_task(play_and_clear_speech(gateway, {"text": text}))
            return web.Response(text="OK")
        return web.Response(text="Device disconnected", status=400)
    except Exception as e:
        return web.Response(text=str(e), status=500)

async def keep_alive():
    os.environ["STACKCHAN_TTS_ENGINE"] = "edge"
    gateway = Gateway()
    async with contextlib.AsyncExitStack() as stack:
        await gateway.start()
        stack.push_async_callback(gateway.stop)
        
        # Setup local HTTP server for IPC
        app = web.Application()
        app["gateway"] = gateway
        app.router.add_post('/notify', handle_notify)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '127.0.0.1', 9999)
        await site.start()
        stack.push_async_callback(runner.cleanup)
        
        print("Keep-alive & Notify IPC service started on port 9999. Monitoring connection...")
        while True:
            if gateway.esp32.device_connected:
                try:
                    # Request battery/device status as a silent heartbeat
                    await gateway.esp32.call_tool("self.get_device_status", {})
                    # Also set brightness to max just to be sure it doesn't sleep
                    await gateway.esp32.call_tool("self.screen.set_brightness", {"level": 255})
                except Exception as e:
                    print(f"Heartbeat failed: {e}")
            else:
                print("Robot disconnected, waiting for reconnection...")
                
            # Send heartbeat every 30 seconds
            await asyncio.sleep(30)

if __name__ == "__main__":
    asyncio.run(keep_alive())

