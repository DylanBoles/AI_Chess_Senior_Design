#!/bin/bash
# Startup script for Raspberry Pi playing WHITE
# IP: 192.168.10.2
# This PI plays white pieces

export PI_COLOR=white
export OPPONENT_IP=192.168.10.3
export OPPONENT_PORT=5002

echo "Starting PI Chess Server (WHITE)"
echo "This PI plays: WHITE"
echo "Opponent PI: $OPPONENT_IP:$OPPONENT_PORT"
echo ""

python3 pi_chess_server.py


