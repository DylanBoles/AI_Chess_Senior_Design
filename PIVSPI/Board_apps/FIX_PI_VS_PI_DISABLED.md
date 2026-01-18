# Fix: PI vs PI Mode Disabled

## Problem
When you start `pi_chess_server.py`, it says "PI vs PI Mode: DISABLED" because the `OPPONENT_IP` is not set.

## Solution (Choose One)

### ✅ Solution 1: Use Config File (Easiest - Recommended)

1. **On PI 1 (192.168.10.2 - White):**
   ```bash
   cd Board_apps
   cp pi_config_white.py pi_config.py
   python3 pi_chess_server.py
   ```

2. **On PI 2 (192.168.10.3 - Black):**
   ```bash
   cd Board_apps
   cp pi_config_black.py pi_config.py
   python3 pi_chess_server.py
   ```

That's it! The server will automatically enable PI vs PI mode.

### Solution 2: Use Environment Variables

**On PI 1 (White):**
```bash
export PI_COLOR=white
export OPPONENT_IP=192.168.10.3
python3 pi_chess_server.py
```

**On PI 2 (Black):**
```bash
export PI_COLOR=black
export OPPONENT_IP=192.168.10.2
python3 pi_chess_server.py
```

### Solution 3: Use Startup Scripts

**On PI 1:**
```bash
./start_pi_white.sh
```

**On PI 2:**
```bash
./start_pi_black.sh
```

## Verify It's Working

When you start the server, you should see:
```
PI vs PI Mode: ENABLED
This PI plays: WHITE (or BLACK)
Opponent PI: 192.168.10.X:5002
```

If you see "PI vs PI Mode: DISABLED", then one of the configuration methods above wasn't applied correctly.


