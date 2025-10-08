# Configuration settings for the AI Chess project

# Raspberry Pi connection settings
PI_IP = "192.168.1.226"  # Change this to your Raspberry Pi's IP address
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