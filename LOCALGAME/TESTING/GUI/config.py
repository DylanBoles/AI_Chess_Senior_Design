"""
Global variables for the app.py web application
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/config.py

Standalone version - no Raspberry Pi connection needed

"""
# Flask app settings
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5001
FLASK_DEBUG = True

# Usr Vs CPU || CPU vs CPU
game_mode = "usr_v_cpu"
engine_white = None
engine_black = None
white_elo = 1350
black_elo = 1350

# Chess engine settings
ENGINE_SKILL_LEVEL = 10  # Range: 0 (weakest) to 20 (strongest)
ENGINE_ELO_RATING = 1350  # Target playing strength
ENGINE_THINK_TIME = 2.0  # Seconds for engine to think

# Game settings
ENGINE_TIMEOUT = 15  # Seconds to wait for engine response
