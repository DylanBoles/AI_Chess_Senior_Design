"""
Web Application Server for AI Chess GUI (API Endpoints for Flask)
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/app.py

Standalone version - works without Raspberry Pi connection
Uses Stockfish engine locally

import system modules & Libraries
"""
from flask import Flask, render_template, jsonify, request
import chess
import chess.engine
import json
import os
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, ENGINE_TIMEOUT

""" Determin the root path """
app = Flask(__name__)

# Global game state
board = chess.Board()
engine = None
game_active = False
current_player = 'white'  # 'white' for human, 'black' for engine

# Game mode variables
game_mode = "user_vs_cpu"
engine_white = None
engine_black = None
white_elo = 1350
black_elo = 1350

def initialize_engine():
    """Initialize the Stockfish chess engine locally"""
    global engine
    try:
        # Try common Stockfish paths
        stockfish_paths = [
            "/usr/games/stockfish",  # Linux
            "/usr/local/bin/stockfish",  # macOS (Homebrew)
            "stockfish",  # If in PATH
            "/opt/homebrew/bin/stockfish",  # macOS (Apple Silicon Homebrew)
        ]
        
        # Also check if STOCKFISH_PATH environment variable is set
        if os.getenv('STOCKFISH_PATH'):
            stockfish_paths.insert(0, os.getenv('STOCKFISH_PATH'))
        
        engine = None
        for path in stockfish_paths:
            try:
                engine = chess.engine.SimpleEngine.popen_uci(path)
                print(f"Stockfish initialized from: {path}")
                break
            except:
                continue
        
        if not engine:
            raise Exception("Stockfish not found. Please install Stockfish or set STOCKFISH_PATH environment variable.")
        
        # Configure engine with default settings
        engine.configure({
            "Skill Level": 10,          # Range: 0 (weakest) to 20 (strongest)
            "UCI_LimitStrength": True,  # Force it to play below max strength
            "UCI_Elo": 1350            # Target playing strength
        })
        print("Chess engine initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize chess engine: {e}")
        print("\nTo install Stockfish:")
        print("  macOS: brew install stockfish")
        print("  Linux: sudo apt-get install stockfish")
        print("  Or download from: https://stockfishchess.org/download/")
        return False

def create_engine(stockfish_path = None):
    """
    Allows for the program to add another Stockfish
    cpu vs cpu play
    """
    paths = ["/usr/games/stockfish", "/usr/local/bin/stockfish", "stockfish", "/opt/homebrew/bin/stockfish"]

    # insert the stockfish path to the list
    if stockfish_path:
        paths.insert(0, stockfish_path)
    
    # Also check if STOCKFISH_PATH environment variable is set
    if os.getenv('STOCKFISH_PATH'):
        paths.insert(0, os.getenv('STOCKFISH_PATH'))

    for p in paths:
        try:
            return chess.engine.SimpleEngine.popen_uci(p)
        except:
            continue
    # return None if engine creation fails
    return None

@app.route('/api/set-game-mode', methods=['POST'])
def set_game_mode():
    global game_mode, engine_white, engine_black, white_elo, black_elo, board, current_player

    data = request.get_json()
    mode = data.get('mode')

    # Check to make sure it is one of the two modes
    if mode not in ["user_vs_cpu", "cpu_vs_cpu"]:
        return jsonify({"status": "error", "message": "Invalid mode"}), 400

    game_mode = mode

    # Get ELO ratings from request
    white_elo = data.get("white_elo", 1350)
    black_elo = data.get("black_elo", 1350)

    # Reset board to starting position
    board = chess.Board()
    
    # Initialize current_player based on game mode
    if mode == "user_vs_cpu":
        # User plays white, CPU plays black
        current_player = 'white'
        engine_white = None
        engine_black = create_engine()
        if engine_black is None:
            return jsonify({"status": "error", "message": "Failed to create engine"}), 500
        engine_black.configure({"UCI_LimitStrength": True, "UCI_Elo": black_elo})
        print(f"User vs CPU mode: User=White, CPU=Black ({black_elo} ELO)")

    elif mode == "cpu_vs_cpu":
        # Both sides are CPU
        current_player = 'white'  # White starts
        engine_white = create_engine()
        engine_black = create_engine()
        if engine_white is None or engine_black is None:
            return jsonify({"status": "error", "message": "Failed to create engines"}), 500
        engine_white.configure({"UCI_LimitStrength": True, "UCI_Elo": white_elo})
        engine_black.configure({"UCI_LimitStrength": True, "UCI_Elo": black_elo})
        print(f"CPU vs CPU mode: White={white_elo} ELO, Black={black_elo} ELO")

    return jsonify({
        "status": "success",
        "mode": mode,
        "white_elo": white_elo,
        "black_elo": black_elo,
        "board_state": get_board_state(),
        "current_player": current_player
    })

def get_board_state():
    """Get current board state as a dictionary"""
    board_state = {}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            square_name = chess.square_name(square)
            piece_symbol = piece.symbol()
            board_state[square_name] = piece_symbol
    return board_state

def is_valid_move(from_square, to_square, piece_code):
    """Validate if a move is legal"""
    try:
        from_sq = chess.parse_square(from_square)
        to_sq = chess.parse_square(to_square)
        move = chess.Move(from_sq, to_sq)
        return move in board.legal_moves
    except Exception as e:
        print(f"Move validation error: {e}")
        return False

def make_move(from_square, to_square):
    """Make a move on the board"""
    try:
        from_sq = chess.parse_square(from_square)
        to_sq = chess.parse_square(to_square)
        move = chess.Move(from_sq, to_sq)
        
        if move in board.legal_moves:
            board.push(move)
            return True
        return False
    except:
        return False

def get_engine_move():
    """Get the engine's move"""
    if not engine:
        print("Engine not initialized")
        return None
        
    if board.is_game_over():
        print("Game is over, cannot get engine move")
        return None
    
    try:
        # Give engine time to think
        result = engine.play(board, chess.engine.Limit(time=0.01))
        move = result.move
        
        # Validate the move before making it
        if move not in board.legal_moves:
            print(f"Engine tried illegal move: {move}")
            return None
        
        # Compute piece and SAN before pushing
        piece = board.piece_at(move.from_square).symbol() if board.piece_at(move.from_square) else None
        san_notation = board.san(move)
        
        # Make the move
        board.push(move)
        global current_player
        current_player = 'black' if current_player == 'white' else 'white'
        
        # Return move information
        return {
            'from': chess.square_name(move.from_square),
            'to': chess.square_name(move.to_square),
            'piece': piece,
            'san': san_notation
        }
    except Exception as e:
        print(f"Engine move error: {e}")
        return None

@app.route('/')
def index():
    """ 
    Return the route at which the app takes to display the webpage 
    
    """
    return render_template('index.html')

@app.route('/api/test')
def test_api():
    """ 
    Test the API and confirm that the Flask GUI server is running and responding to requests 
    
    """
    return jsonify({
        'message': 'API is working!',
        'status': 'success',
        'chess': '♔♕♖♗♘♙'
    })

@app.route('/api/pi-status', methods=['GET'])
def check_pi_status():
    """
    Check connection status (standalone mode - always returns connected)
    This endpoint exists for compatibility with the frontend
    """
    # In standalone mode, if the server is running, the engine should be initialized
    # But we check anyway to be safe
    if engine is not None:
        return jsonify({
            'status': 'connected',
            'message': 'Standalone mode - Stockfish engine ready',
            'engine_connected': True
        })
    else:
        # This shouldn't happen if server started properly, but handle it gracefully
        return jsonify({
            'status': 'disconnected',
            'message': 'Engine not initialized',
            'engine_connected': False
        }), 503

    
@app.route('/api/move', methods=['POST'])
def handle_move():
    """
    Handle a move from the frontend and send it to the Pi

    Send the move made by the user to the Raspberry Pi using the move_data dictionary 
    - The Piece type
    - Starting Square
    - Ending Square
    - Move number in the game 
    Are all sent to the Pi to be interpreted we send it using request.post to send the move_data dictionary before the Timeout (10 Seconds)

    If HTTP status code 200 is recieced the status is accepted and we send the 'board state', 'if the game is over', the move is accepted', and 'if there is a winner'
    Else we send an error that the move was not sent and display a message stating "Failed to communicate with Raspberry Pi"

    Also, return errors if there are errors in Connection or server Error

    """
    try:
        data = request.get_json()
        from_square = data.get('from')
        to_square = data.get('to')
        piece = data.get('piece')
        
        if not from_square or not to_square:
            return jsonify({
                'status': 'error',
                'message': 'Missing from or to square'
            }), 400
        
        # Validate the move
        if not is_valid_move(from_square, to_square, piece):
            return jsonify({
                'status': 'error',
                'message': 'Invalid move',
                'move_accepted': False
            }), 400
        
        # Make the move
        if make_move(from_square, to_square):
            # Update current player after move
            global current_player
            if current_player == 'white':
                current_player = 'black'
            else:
                current_player = 'white'
            
            # Check if game is over
            game_over = board.is_game_over()
            winner = None
            
            if game_over:
                result = board.result()
                if result == '1-0':
                    winner = 'white'
                elif result == '0-1':
                    winner = 'black'
                else:
                    winner = 'draw'
            
            return jsonify({
                'status': 'success',
                'move_accepted': True,
                'board_state': get_board_state(),
                'game_over': game_over,
                'winner': winner,
                'current_player': current_player
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to make move',
                'move_accepted': False
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/board-state', methods=['GET'])
def get_board_state_endpoint():
    """
    Get current board state (local processing, no Pi needed)
    """
    try:
        return jsonify({
            'status': 'success',
            'board_state': get_board_state(),
            'current_player': current_player,
            'game_over': board.is_game_over(),
            'board_fen': board.fen()
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error getting board state: {str(e)}'
        }), 500

@app.route('/api/engine-move', methods=['POST'])
def get_engine_move_endpoint():
    """
    Get the engine's move from the Pi

    Request 'POST' to retreive the stockfish or chess engines move in response to player
    request the board state From the engine unless the Request times out (15 Seconds)

    If it is successful return 200 otherwise return error and 500
    Check for Network Errors
    
    """
    global current_player

    try:
        # Get the correct engine (white, black or none)
        engine_to_use = get_engine_for_turn()

        if engine_to_use is None:
            return jsonify({
                'status': 'error',
                'message': 'Chess engine not initialized'
            }), 400
        
        if board.is_game_over():
            return jsonify({
                'status': 'error',
                'message': 'Game is over'
            }), 400

        # Engine will think and play
        result = engine_to_use.play(board, chess.engine.Limit(time=1.0))
        move = result.move

        board.push(move)

        # Swap the current Player
        if current_player == "black":
            current_player = "white"
        else:
            current_player = "black"

        # Get piece symbol before move (need to peek at previous position)
        # Since we already pushed, we need to get the piece from the move
        piece_symbol = None
        try:
            # Get piece from the move's from_square (before the move)
            # We need to temporarily pop to get the piece
            board.pop()
            piece = board.piece_at(move.from_square)
            if piece:
                piece_symbol = piece.symbol()
            board.push(move)
        except:
            pass

        # Check if game is over
        game_over = board.is_game_over()
        winner = None
        if game_over:
            result = board.result()
            if result == '1-0':
                winner = 'white'
            elif result == '0-1':
                winner = 'black'
            else:
                winner = 'draw'
        
        # build a response
        return jsonify({
            "status": "success",
            "engine_move": {
                "from": chess.square_name(move.from_square),
                "to": chess.square_name(move.to_square),
                "piece": piece_symbol
            },
            "board_state": get_board_state(),
            "game_over": game_over,
            "winner": winner,
            "current_player": current_player
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Engine error: {str(e)}"
        }), 500

        
# Helper Function
def get_engine_for_turn():
    if game_mode == "user_vs_cpu":
        # Only Black is Stockfish for now
        if current_player == "black":
            return engine_black
        else:
            return None
    elif game_mode == "cpu_vs_cpu":
        # Both sides are Stockfish
        if current_player == "white":
            return engine_white
        else:
            return engine_black

    return None
    
@app.route('/api/set-bot-difficulty', methods=['POST'])
def set_bot_difficulty():
    """
    Set the bot difficulty level for the chess engine on the Raspberry Pi.
    
    This endpoint receives the selected bot's ELO rating and skill level from the frontend
    and forwards it to the Raspberry Pi to configure the chess engine accordingly.
    
    Example Frontend request body:
        {
            "elo": 1000,
            "skill": 10
        }
    
    WorkFlow:
        1. Receive the JSON payload from the frontend
        2. Extract the ELO rating and skill level
        3. Forward the configuration to the Raspberry Pi
        4. Wait up to 5 seconds for a response
        5. Return the Pi's response back to frontend, or send error
    
    """
    try:
        if not engine:
            return jsonify({
                'status': 'error',
                'message': 'Engine not initialized'
            }), 500
        
        data = request.get_json()
        elo = data.get('elo')
        skill = data.get('skill')
        
        if not elo or not skill:
            return jsonify({
                'status': 'error',
                'message': 'ELO rating and skill level are required'
            }), 400
        
        # Ensure ELO is within Stockfish's supported range (1350-2850)
        if elo < 1350:
            elo = 1350
        elif elo > 2850:
            elo = 2850
            
        # Ensure skill level is within range (0-20)
        if skill < 0:
            skill = 0
        elif skill > 20:
            skill = 20
        
        # Configure the engine with the new settings
        engine.configure({
            "Skill Level": skill,
            "UCI_LimitStrength": True,
            "UCI_Elo": elo
        })
        
        # Reset the board to starting position when setting difficulty
        global board
        board = chess.Board()
        
        print(f"Bot difficulty set: ELO {elo}, Skill Level {skill}")
        
        return jsonify({
            'status': 'success',
            'message': f'Bot difficulty set: ELO {elo}, Skill Level {skill}',
            'elo': elo,
            'skill': skill,
            'board_state': get_board_state()
        })
        
    except Exception as e:
        print(f"Error setting bot difficulty: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Failed to set bot difficulty: {str(e)}'
        }), 500

@app.route('/api/game-control', methods=['POST'])
def handle_game_control():
    """
    Handle game control commands from the frontend GUI and forward them to the Raspberry PI.

    This endpoint is triggered whenever a control button (reset, pause, play, next, prev) is pressed on the web interface. the command is recieved in JSON format extracted from the 'command' key, and sent via POST to the Raspberry PI's corresponding 'api/game-control= endpoint.

    Example Frontend request body:
        {
            "command" : "reset"
        }

    WorkFlow:
        1. Recieve the JSON payload from the frontend
        2. Extract the control command
        3. Forward the command to the Raspberry Pi using an HTTP POST request
        4. Wait up to 5 seconds for a response
        5. Return the Pi's response back to frontend, or send error

    Checks Network Connections

    """
    try:
        data = request.get_json()
        command = data.get('command')
        
        global board, game_active, current_player, game_mode
        
        if command == 'reset':
            board = chess.Board()
            # Reset current player based on game mode
            if game_mode == "user_vs_cpu":
                current_player = 'white'  # User plays white
            elif game_mode == "cpu_vs_cpu":
                current_player = 'white'  # White starts in CPU vs CPU
            else:
                current_player = 'white'  # Default to white
            return jsonify({
                'status': 'success',
                'message': 'Game reset to starting position',
                'board_state': get_board_state(),
                'current_player': current_player
            })
        
        elif command == 'pause':
            game_active = False
            return jsonify({
                'status': 'success',
                'message': 'Game paused'
            })
        
        elif command == 'resume':
            game_active = True
            return jsonify({
                'status': 'success',
                'message': 'Game resumed'
            })
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unknown command: {command}'
            }), 400
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Control error: {str(e)}'
        }), 500

def cleanup():
    """Cleanup resources"""
    global engine
    if engine:
        engine.quit()
        print("Chess engine closed")

""" 
Send in:
    host: 0.0.0.0
    port: 5001
    debug: True

"""
if __name__ == '__main__':
    print("Starting Standalone Chess Server (no Pi required)...")
    
    # Initialize chess engine
    if initialize_engine():
        print("Server ready!")
        try:
            app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            cleanup()
    else:
        print("Failed to initialize chess engine. Server cannot start.")
        print("Please install Stockfish and try again.")
