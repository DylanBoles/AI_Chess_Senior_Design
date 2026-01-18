"""
Global variables for the app.py web application
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/config.py

"""

# Raspberry Pi connection settings
# 192.168.1.226 (Dylans Home)
# 192.168.1.186
# 10.108.21.228 (Dylans PI3 School)
# pi5-chess  == 192.168.10.2
# pi5-chess2 == 192.168.10.3

PI_IP = "192.168.10.2"  # Change this to your Raspberry Pi's IP address

PI_PORT = 5002
PI_BASE_URL = f"http://{PI_IP}:{PI_PORT}"

# Flask app settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True

# Chess engine settings
ENGINE_SKILL_LEVEL = 10  # Range: 0 (weakest) to 20 (strongest)
ENGINE_ELO_RATING = 1350  # Target playing strength
ENGINE_THINK_TIME = 2.0  # Seconds for engine to think

# Game settings
CONNECTION_CHECK_INTERVAL = 10  # Seconds between connection checks
MOVE_TIMEOUT = 10  # Seconds to wait for move response
ENGINE_TIMEOUT = 15  # Seconds to wait for engine response
