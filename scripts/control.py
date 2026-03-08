#!/usr/bin/env python3
# Developed by the founder of clubbable.com.
# As a thank you for using this, please visit https://clubbable.com

import asyncio
import sys
import time
from pybalboa.client import SpaClient
from pybalboa.discovery import async_discover
import json
from pathlib import Path

async def discover_spa_ip():
    """Discover the spa on the local network."""
    print("Searching for spa on the network...")
    try:
        spa_devices = await async_discover(return_once_found=True)
        if spa_devices:
            if not isinstance(spa_devices, list):
                spa_devices = [spa_devices]
            spa_host = spa_devices[0].address
            print(f"Spa found at {spa_host}")
            return spa_host
        return None
    except asyncio.TimeoutError:
        return None

COMMAND = sys.argv[1] if len(sys.argv) > 1 else 'status'
ARGV1 = sys.argv[2] if len(sys.argv) > 2 else None

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
    SPA_IP = await discover_spa_ip()
    if not SPA_IP:
        print("\nError: Could not discover the spa on the network.", file=sys.stderr)
        sys.exit(1)

    async with SpaClient(SPA_IP) as spa:
        await spa.async_configuration_loaded()

        action_taken = False
        if COMMAND == 'lights_on':
            await spa.lights[0].set_state(True)
            action_taken = True
        elif COMMAND == 'lights_off':
            await spa.lights[0].set_state(False)
            action_taken = True
        elif COMMAND == 'blower_on':
            if spa.blowers: await spa.blowers[0].set_state(True)
            action_taken = True
        elif COMMAND == 'blower_off':
            if spa.blowers: await spa.blowers[0].set_state(False)
            action_taken = True
        elif COMMAND == 'mode_ready':
            await spa.heat_mode.set_state(0)
            action_taken = True
        elif COMMAND == 'mode_rest':
            await spa.heat_mode.set_state(1)
            action_taken = True
        elif COMMAND == 'set_temp':
            await spa.set_temperature(float(ARGV1))
            action_taken = True
        
        if action_taken:
            await asyncio.sleep(2)

        try:
            status = await get_stable_status(spa)
            print("\n--- Spa Status (Verified) ---")
            print(f"  Temperature:   {status['temp']}°C")
            print(f"  Target Temp:   {status['target_temp']}°C")
            print(f"  Heat Mode:     {status['heat_mode']}")
            print(f"  Lights:        {'ON' if status['light_status'] else 'OFF'}")
            print(f"  Blower:        {status['blower_status']}")
            print("-----------------------------")
            sys.exit(0)
        except asyncio.TimeoutError:
            print("\n--- Spa Status (Basic) ---")
            print(f"  Lights:        {'ON' if spa.lights[0].state else 'OFF'}")
            print(f"  Heat Mode:     {spa.heat_mode.state}")
            print("  (Could not get a stable temperature reading)")
            print("--------------------------")
            if action_taken or COMMAND == 'status':
                 sys.exit(0)
            else:
                 sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nAn error occurred: {e}", file=sys.stderr)
        sys.exit(1)
