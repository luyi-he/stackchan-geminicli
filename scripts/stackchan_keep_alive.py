import asyncio
import os
import contextlib
from stackchan_mcp.gateway import Gateway

async def keep_alive():
    os.environ["STACKCHAN_TTS_ENGINE"] = "edge"
    gateway = Gateway()
    async with contextlib.AsyncExitStack() as stack:
        await gateway.start()
        stack.push_async_callback(gateway.stop)
        
        print("Keep-alive service started. Monitoring connection...")
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
