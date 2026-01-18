#!/bin/bash
# Startup script for Raspberry Pi playing BLACK
# IP: 192.168.10.3
# This PI plays black pieces

export PI_COLOR=black
export OPPONENT_IP=192.168.10.2
export OPPONENT_PORT=5002

echo "Starting PI Chess Server (BLACK)"
echo "This PI plays: BLACK"
echo "Opponent PI: $OPPONENT_IP:$OPPONENT_PORT"
echo ""

python3 pi_chess_server.py


