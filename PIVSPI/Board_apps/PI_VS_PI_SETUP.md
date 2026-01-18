# Raspberry Pi vs Raspberry Pi Setup Guide

This guide explains how to set up and run the chess application in PI vs PI mode, where two Raspberry Pis play against each other.

## Prerequisites

Both Raspberry Pis need:
- Python 3.7+
- Stockfish chess engine installed
- Flask and requests libraries
- chess and chess-engine libraries
- Network connectivity to each other

## IP Addresses

- **PI 1 (White)**: 192.168.10.2
- **PI 2 (Black)**: 192.168.10.3

Both Pis run their servers on port **5002**.

## Installation

### On Both Raspberry Pis:

1. Install Stockfish:
```bash
sudo apt update
sudo apt install stockfish
```

2. Install Python dependencies:
```bash
pip3 install flask requests chess chess-engine
```

## Configuration

The PI vs PI mode can be configured using **three methods** (in order of priority):
1. **Environment variables** (highest priority)
2. **Config file** (`pi_config.py`)
3. **Defaults** (lowest priority)

### Method 1: Config File (Easiest - Recommended)

Create a `pi_config.py` file in the same directory as `pi_chess_server.py`:

#### On PI 1 (192.168.10.2 - White):
```python
PI_COLOR = 'white'
OPPONENT_IP = '192.168.10.3'
OPPONENT_PORT = 5002
```

#### On PI 2 (192.168.10.3 - Black):
```python
PI_COLOR = 'black'
OPPONENT_IP = '192.168.10.2'
OPPONENT_PORT = 5002
```

**Quick setup:** Copy the appropriate template file:
- `cp pi_config_white.py pi_config.py` (on white PI)
- `cp pi_config_black.py pi_config.py` (on black PI)

### Method 2: Environment Variables

- `PI_COLOR`: The color this PI plays ('white' or 'black')
- `OPPONENT_IP`: The IP address of the opponent PI
- `OPPONENT_PORT`: The port the opponent PI runs on (default: 5002)

## Running PI vs PI Mode

### Method 1: Using Config File (Easiest)

1. Create `pi_config.py` on each PI (see Configuration section above)
2. Simply run:
```bash
python3 pi_chess_server.py
```

The server will automatically detect PI vs PI mode from the config file!

### Method 2: Using Startup Scripts

#### On PI 1 (192.168.10.2 - White):
```bash
cd /path/to/Board_apps
chmod +x start_pi_white.sh
./start_pi_white.sh
```

#### On PI 2 (192.168.10.3 - Black):
```bash
cd /path/to/Board_apps
chmod +x start_pi_black.sh
./start_pi_black.sh
```

### Method 2: Using Environment Variables

#### On PI 1 (192.168.10.2 - White):
```bash
export PI_COLOR=white
export OPPONENT_IP=192.168.10.3
export OPPONENT_PORT=5002
python3 pi_chess_server.py
```

#### On PI 2 (192.168.10.3 - Black):
```bash
export PI_COLOR=black
export OPPONENT_IP=192.168.10.2
export OPPONENT_PORT=5002
python3 pi_chess_server.py
```

## How It Works

1. **White PI starts first**: When the white PI starts, it automatically makes the first move after 2 seconds.

2. **Move flow**:
   - White PI calculates its move using Stockfish
   - White PI sends the move to Black PI via HTTP POST to `/api/receive-opponent-move`
   - Black PI receives the move, validates it, and applies it to its board
   - Black PI calculates its response move
   - Black PI sends the move back to White PI
   - This continues until the game ends

3. **Game synchronization**: Both Pis maintain their own board state, which should stay synchronized as moves are exchanged.

## Viewing the Game

You can view the game by connecting the GUI to either PI:

1. Update `GUI/config.py` to point to one of the PIs:
   ```python
   PI_IP = "192.168.10.2"  # or "192.168.10.3"
   ```

2. Start the GUI server:
   ```bash
   cd GUI
   python3 app.py
   ```

3. Open your browser to `http://localhost:5001`

The GUI will display the current board state from whichever PI you're connected to.

## Troubleshooting

### Connection Issues

1. **Check IP addresses**: Ensure both Pis have the correct static IPs configured
   ```bash
   # On each PI, check IP
   hostname -I
   ```

2. **Test connectivity**: From one PI, ping the other:
   ```bash
   ping 192.168.10.2  # or 192.168.10.3
   ```

3. **Check firewall**: Ensure port 5002 is open on both Pis:
   ```bash
   sudo ufw allow 5002
   ```

4. **Test API connection**: From one PI, test the other's API:
   ```bash
   curl http://192.168.10.2:5002/api/status
   curl http://192.168.10.3:5002/api/status
   ```

### Game Not Starting

1. **Check logs**: Look at the console output on both Pis for error messages

2. **Verify environment variables**: Make sure `PI_COLOR` and `OPPONENT_IP` are set correctly

3. **Check engine initialization**: Ensure Stockfish is installed and accessible:
   ```bash
   which stockfish
   /usr/games/stockfish
   ```

### Moves Not Being Received

1. **Check network**: Verify both Pis can reach each other

2. **Check server status**: Use the status endpoint:
   ```bash
   curl http://192.168.10.2:5002/api/status
   ```

3. **Check logs**: Look for error messages about failed move transmission

## API Endpoints

### New Endpoint for PI vs PI Mode

- `POST /api/receive-opponent-move`: Receives moves from the opponent PI
  - Request body: `{'from': 'e2', 'to': 'e4', 'piece': 'P', 'san': 'e4'}`
  - Response: `{'status': 'success', 'move_accepted': True, 'board_state': {...}}`

### Updated Endpoints

- `GET /api/status`: Now includes PI vs PI mode information:
  - `pi_vs_pi_mode`: Boolean indicating if PI vs PI mode is enabled
  - `pi_color`: The color this PI plays ('white' or 'black')
  - `opponent_ip`: The opponent PI's IP address
  - `is_my_turn`: Boolean indicating if it's this PI's turn (only in PI vs PI mode)

## Stopping the Game

To stop the game, press `Ctrl+C` on either PI. The game will stop immediately.

## Notes

- Both Pis maintain independent board states that should stay synchronized
- The white PI always starts the game
- If a move fails to transmit, the game may desynchronize - check logs on both Pis
- The GUI can connect to either PI to view the game state
- Engine difficulty can be configured using the `/api/set-bot-difficulty` endpoint

