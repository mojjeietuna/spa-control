---
name: spa-control
description: "Controls a Balboa-based spa/hot tub over the local WiFi network. Use for all spa-related commands, including checking status, turning lights on/off, changing heating modes (ready/rest), setting temperature ranges (high/low), and setting the target temperature."

---

# Spa Control

This skill provides direct control over a Balboa-based spa using the `pybalboa` Python library.

## Prerequisites

This skill assumes the `pybalboa` library is installed in a Python virtual environment located at `spa_controller/.venv`. It also assumes the spa's IP address is known.

**Spa IP Address:** `192.168.1.220`

## Core Script

The primary tool is `scripts/control.py`. It is a Python script that takes a command as its first argument.

### Usage

```bash
/path/to/venv/bin/python scripts/control.py <command> [argument]
```

### Available Commands

- `status`: Get the current status of the spa.
- `lights_on`: Turn the lights on.
- `lights_off`: Turn the lights off.
- `circ_pump_on`: Turn the circulation pump on.
- `circ_pump_off`: Turn the circulation pump off.
- `mode_ready`: Set the heating mode to 'Ready'.
- `mode_rest`: Set the heating mode to 'Rest'.
- `range_high`: Set the temperature range to 'High'.
- `range_low`: Set the temperature range to 'Low'.
al-
- `set_temp <temp>`: Set the target temperature.

### Example

To set the spa temperature to 39.5 degrees:

```bash
/Users/minime/.openclaw/workspace/spa_controller/.venv/bin/python scripts/control.py set_temp 39.5
```

## Workflow

1.  Identify the user's intent (e.g., "turn on the spa lights").
2.  Map the intent to one of the available commands.
3.  Construct the full command to execute `scripts/control.py` using the correct Python virtual environment.
4.  Execute the command.
5.  Report the final, verified status from the script's output back to the user.
