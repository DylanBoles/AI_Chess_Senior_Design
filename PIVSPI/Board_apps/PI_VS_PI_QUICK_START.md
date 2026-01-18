# PI vs PI Quick Start Guide

## Quick Setup

### On PI 1 (192.168.10.2 - White):
```bash
cd Board_apps
export PI_COLOR=white
export OPPONENT_IP=192.168.10.3
python3 pi_chess_server.py
```

### On PI 2 (192.168.10.3 - Black):
```bash
cd Board_apps
export PI_COLOR=black
export OPPONENT_IP=192.168.10.2
python3 pi_chess_server.py
```

## Or Use the Startup Scripts

### On PI 1 (White):
```bash
cd Board_apps
chmod +x start_pi_white.sh
./start_pi_white.sh
```

### On PI 2 (Black):
```bash
cd Board_apps
chmod +x start_pi_black.sh
./start_pi_black.sh
```

## What Happens

1. Both Pis start their servers
2. White PI automatically makes the first move after 2 seconds
3. Moves are automatically exchanged between the two Pis
4. Game continues until checkmate, stalemate, or draw

## View the Game

Connect the GUI to either PI by updating `GUI/config.py`:
```python
PI_IP = "192.168.10.2"  # or "192.168.10.3"
```

Then start the GUI:
```bash
cd GUI
python3 app.py
```

Open browser to: `http://localhost:5001`

## Troubleshooting

- **Can't connect?** Check that both Pis can ping each other
- **Game not starting?** Make sure environment variables are set correctly
- **Moves not working?** Check the console logs on both Pis for errors

For detailed information, see `PI_VS_PI_SETUP.md`


