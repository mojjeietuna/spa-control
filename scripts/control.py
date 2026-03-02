import asyncio
import sys
import time
from pybalboa.client import SpaClient
from pybalboa.discovery import async_discover

SPA_IP = '192.168.1.220'
COMMAND = sys.argv[1] if len(sys.argv) > 1 else 'status'
ARGV1 = sys.argv[2] if len(sys.argv) > 2 else None

async def wake_spa():
    try:
        await async_discover(return_once_found=True, timeout=2)
    except asyncio.TimeoutError:
        pass
    await asyncio.sleep(2)

async def get_stable_status(spa):
    start_time = time.time()
    while time.time() - start_time < 20:
        temp = spa.temperature
        if temp is not None and 0 < temp < 50:
            return {
                "temp": temp,
                "target_temp": spa.target_temperature,
                "heat_mode": spa.heat_mode.state,
                "light_status": spa.lights[0].state if spa.lights else 'N/A',
                "blower_status": spa.blowers[0].state if spa.blowers else 'N/A'
            }
        await asyncio.sleep(1)
    raise asyncio.TimeoutError("Failed to get stable sensor data.")

async def main():
    await wake_spa()
    async with SpaClient(SPA_IP) as spa:
        await spa.async_configuration_loaded()

        if COMMAND == 'lights_on':
            await spa.lights[0].set_state(True)
        elif COMMAND == 'lights_off':
            await spa.lights[0].set_state(False)
        elif COMMAND == 'blower_on':
            if spa.blowers: await spa.blowers[0].set_state(True)
        elif COMMAND == 'blower_off':
            if spa.blowers: await spa.blowers[0].set_state(False)
        elif COMMAND == 'mode_ready':
            await spa.heat_mode.set_state(0)
        elif COMMAND == 'mode_rest':
            await spa.heat_mode.set_state(1)
        elif COMMAND == 'set_temp':
            await spa.set_temperature(float(ARGV1))
        
        status = await get_stable_status(spa)

        print("\n--- Spa Status (Verified) ---")
        print(f"  Temperature:   {status['temp']}°C")
        print(f"  Target Temp:   {status['target_temp']}°C")
        print(f"  Heat Mode:     {status['heat_mode']}")
        print(f"  Lights:        {'ON' if status['light_status'] else 'OFF'}")
        print(f"  Blower:        {status['blower_status']}")
        print("-----------------------------")
        sys.exit(0)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)
