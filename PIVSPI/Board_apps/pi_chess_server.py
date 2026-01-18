#!/usr/bin/env python3
"""
Raspberry Pi Chess Server
Handles chess engine communication and game logic for the AI Chess project.
This server runs on the Raspberry Pi and communicates with the laptop GUI.
Supports PI vs PI mode where two Pis play against each other.
"""

import chess
import chess.engine
from flask import Flask, request, jsonify
import json
import threading
import time
import requests
import os

app = Flask(__name__)

# Global game state
board = chess.Board()
engine = None
game_active = False
current_player = 'white'  # 'white' for human, 'black' for engine

# PI vs PI mode configuration
# Set via environment variables, config file, or defaults
# Priority: Environment variables > Config file > Defaults

# Try to load from config file first (if it exists)
PI_COLOR_CONFIG = None
OPPONENT_IP_CONFIG = None
OPPONENT_PORT_CONFIG = None

try:
    # Try to import config if it exists in the same directory
    import sys
    config_path = os.path.join(os.path.dirname(__file__), 'pi_config.py')
    if os.path.exists(config_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("pi_config", config_path)
        pi_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(pi_config)
        PI_COLOR_CONFIG = getattr(pi_config, 'PI_COLOR', None)
        OPPONENT_IP_CONFIG = getattr(pi_config, 'OPPONENT_IP', None)
        OPPONENT_PORT_CONFIG = getattr(pi_config, 'OPPONENT_PORT', None)
        print(f"Loaded PI vs PI config from pi_config.py")
except Exception as e:
    print(f"Could not load pi_config.py: {e}")

# Use environment variables first, then config file, then defaults
PI_COLOR = os.environ.get('PI_COLOR', PI_COLOR_CONFIG or 'white').lower()  # 'white' or 'black'
OPPONENT_IP = os.environ.get('OPPONENT_IP', OPPONENT_IP_CONFIG)  # e.g., '192.168.10.2' or '192.168.10.3'
OPPONENT_PORT = int(os.environ.get('OPPONENT_PORT', OPPONENT_PORT_CONFIG or '5002'))
OPPONENT_BASE_URL = f"http://{OPPONENT_IP}:{OPPONENT_PORT}" if OPPONENT_IP else None
PI_VS_PI_MODE = OPPONENT_IP is not None

# Move processing lock to prevent race conditions
move_lock = threading.Lock()

def initialize_engine():
    """Initialize the Stockfish chess engine"""
    global engine
    try:
        engine = chess.engine.SimpleEngine.popen_uci("/usr/games/stockfish")
        engine.configure({
            "Skill Level": 10,          # Range: 0 (weakest) to 20 (strongest)
            "UCI_LimitStrength": True,  # Force it to play below max strength
            "UCI_Elo": 1350            # Target playing strength (e.g., 1200–2800)
        })
        print("Chess engine initialized successfully")
        return True
    except Exception as e:
        print(f"Failed to initialize chess engine: {e}")
        return False

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
        print(f"Validating move: {from_square} to {to_square}")
        
        # Convert position strings to chess squares
        from_sq = chess.parse_square(from_square)
        to_sq = chess.parse_square(to_square)
        
        print(f"Parsed squares: {from_sq} to {to_sq}")
        
        # Create move object
        move = chess.Move(from_sq, to_sq)
        
        print(f"Created move object: {move}")
        print(f"Move in legal moves: {move in board.legal_moves}")
        
        # Check if move is legal
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
        print(f"Getting engine move. Board FEN: {board.fen()}")
        print(f"Legal moves: {[board.san(move) for move in board.legal_moves]}")
        
        # Give engine 2 seconds to think
        result = engine.play(board, chess.engine.Limit(time=2.0))
        move = result.move
        
        print(f"Engine suggested move: {move}")
        
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
        print(f"Engine move applied: {move}")
        
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

def send_move_to_opponent(move_data):
    """Send a move to the opponent PI in PI vs PI mode"""
    if not PI_VS_PI_MODE or not OPPONENT_BASE_URL:
        return False
    
    try:
        print(f"Sending move to opponent PI at {OPPONENT_BASE_URL}/api/receive-opponent-move")
        response = requests.post(
            f"{OPPONENT_BASE_URL}/api/receive-opponent-move",
            json=move_data,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Move successfully sent to opponent PI")
            return True
        else:
            print(f"Failed to send move to opponent: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error sending move to opponent PI: {e}")
        return False

def is_my_turn():
    """Check if it's this PI's turn to move"""
    if not PI_VS_PI_MODE:
        return False
    
    # Check if it's this PI's color's turn
    is_white_turn = board.turn  # True if white to move, False if black to move
    return (PI_COLOR == 'white' and is_white_turn) or (PI_COLOR == 'black' and not is_white_turn)

def auto_make_move():
    """Automatically make a move if it's this PI's turn (for PI vs PI mode)"""
    if not PI_VS_PI_MODE or not is_my_turn():
        return
    
    if board.is_game_over():
        print("Game is over, cannot make move")
        return
    
    with move_lock:
        # Double-check it's still our turn after acquiring lock
        if not is_my_turn():
            return
        
        print(f"PI {PI_COLOR}: It's my turn, making engine move...")
        engine_move = get_engine_move()
        
        if engine_move:
            # Send move to opponent PI
            move_data = {
                'from': engine_move['from'],
                'to': engine_move['to'],
                'piece': engine_move['piece'],
                'san': engine_move['san'],
                'board_state': get_board_state()
            }
            send_move_to_opponent(move_data)
            print(f"PI {PI_COLOR}: Move made and sent to opponent")
        else:
            print(f"PI {PI_COLOR}: Failed to get engine move")

@app.route('/api/status', methods=['GET'])
def status():
    """Check server status"""
    return jsonify({
        'status': 'running',
        'engine_connected': engine is not None,
        'game_active': game_active,
        'current_player': current_player,
        'board_fen': board.fen(),
        'pi_vs_pi_mode': PI_VS_PI_MODE,
        'pi_color': PI_COLOR,
        'opponent_ip': OPPONENT_IP,
        'is_my_turn': is_my_turn() if PI_VS_PI_MODE else None
    })

@app.route('/api/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to see board state and legal moves"""
    legal_moves = []
    for move in board.legal_moves:
        legal_moves.append({
            'from': chess.square_name(move.from_square),
            'to': chess.square_name(move.to_square),
            'san': board.san(move)
        })
    
    return jsonify({
        'board_fen': board.fen(),
        'legal_moves': legal_moves,
        'turn': 'white' if board.turn else 'black'
    })

@app.route('/api/move', methods=['POST'])
def handle_move():
    """Handle a move from the laptop"""
    try:
        data = request.get_json()
        from_square = data.get('from')
        to_square = data.get('to')
        piece = data.get('piece')
        
        print(f"Received move: {from_square} to {to_square}, piece: {piece}")
        print(f"Current board FEN: {board.fen()}")
        print(f"Legal moves: {[board.san(move) for move in board.legal_moves]}")
        
        if not from_square or not to_square:
            print("Error: Missing from or to square")
            return jsonify({
                'status': 'error',
                'message': 'Missing from or to square'
            }), 400
        
        # Validate the move (we don't need the piece parameter for validation)
        if not is_valid_move(from_square, to_square, piece):
            print(f"Move validation failed: {from_square} to {to_square}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid move',
                'move_accepted': False
            }), 400
        
        # Make the move
        with move_lock:
            if make_move(from_square, to_square):
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
                
                response_data = {
                    'status': 'success',
                    'move_accepted': True,
                    'board_state': get_board_state(),
                    'game_over': game_over,
                    'winner': winner,
                    'current_player': 'black' if current_player == 'white' else 'white'
                }
                
                # In PI vs PI mode, if it's now the opponent's turn, they will make their move
                # automatically when they receive it via /api/receive-opponent-move
                # No need to trigger anything here
                
                return jsonify(response_data)
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

@app.route('/api/engine-move', methods=['POST'])
def handle_engine_move():
    """Get the engine's move"""
    try:
        if not engine:
            return jsonify({
                'status': 'error',
                'message': 'Chess engine not initialized'
            }), 500
        
        if board.is_game_over():
            return jsonify({
                'status': 'error',
                'message': 'Game is over'
            }), 400
        
        # Get engine move
        with move_lock:
            engine_move = get_engine_move()
            
            if engine_move:
                # Check if game is over after engine move
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
                
                response_data = {
                    'status': 'success',
                    'engine_move': engine_move,
                    'board_state': get_board_state(),
                    'game_over': game_over,
                    'winner': winner
                }
                
                # In PI vs PI mode, send move to opponent
                # The opponent will receive the move and make their response automatically
                if PI_VS_PI_MODE and not game_over:
                    move_data = {
                        'from': engine_move['from'],
                        'to': engine_move['to'],
                        'piece': engine_move['piece'],
                        'san': engine_move['san'],
                        'board_state': get_board_state()
                    }
                    send_move_to_opponent(move_data)
                
                return jsonify(response_data)
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to get engine move'
                }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Engine error: {str(e)}'
        }), 500

@app.route('/api/receive-opponent-move', methods=['POST'])
def receive_opponent_move():
    """Receive a move from the opponent PI in PI vs PI mode"""
    try:
        if not PI_VS_PI_MODE:
            return jsonify({
                'status': 'error',
                'message': 'Not in PI vs PI mode'
            }), 400
        
        data = request.get_json()
        from_square = data.get('from')
        to_square = data.get('to')
        
        print(f"PI {PI_COLOR}: Received move from opponent: {from_square} to {to_square}")
        
        if not from_square or not to_square:
            return jsonify({
                'status': 'error',
                'message': 'Missing from or to square'
            }), 400
        
        with move_lock:
            # Validate the move
            if not is_valid_move(from_square, to_square, None):
                print(f"PI {PI_COLOR}: Invalid move received from opponent")
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid move'
                }), 400
            
            # Make the move
            if make_move(from_square, to_square):
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
                
                print(f"PI {PI_COLOR}: Opponent's move applied successfully")
                
                # If it's now our turn and game is not over, make our move
                if not game_over and is_my_turn():
                    print(f"PI {PI_COLOR}: It's now my turn, making move...")
                    # Schedule our move in a separate thread
                    threading.Thread(target=auto_make_move, daemon=True).start()
                
                return jsonify({
                    'status': 'success',
                    'move_accepted': True,
                    'board_state': get_board_state(),
                    'game_over': game_over,
                    'winner': winner
                })
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to make move'
                }), 400
            
    except Exception as e:
        print(f"PI {PI_COLOR}: Error receiving opponent move: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/board-state', methods=['GET'])
def get_board_state_endpoint():
    """Get current board state"""
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

@app.route('/api/sync-board', methods=['POST'])
def sync_board():
    """Sync the board state from the frontend"""
    try:
        data = request.get_json()
        frontend_board_state = data.get('board_state', {})
        
        # Reset the board to starting position
        global board
        board = chess.Board()
        
        # Apply moves one by one to reconstruct the board state
        # This is a simple approach - in a real implementation you'd want to track moves
        print(f"Syncing board state from frontend: {frontend_board_state}")
        
        return jsonify({
            'status': 'success',
            'message': 'Board state synced',
            'board_state': get_board_state(),
            'board_fen': board.fen()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Error syncing board: {str(e)}'
        }), 500

@app.route('/api/game-control', methods=['POST'])
def game_control():
    """Handle game control commands"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        # if command == 'new_game':
        #     global board, game_active, current_player
        #     board = chess.Board()
        #     game_active = True
        #     current_player = 'white'
        #     return jsonify({
        #         'status': 'success',
        #         'message': 'New game started'
        #     })
        
        if command == 'reset':
            global board, game_active, current_player
            with move_lock:
                board = chess.Board()
                current_player = 'white'
                
                # In PI vs PI mode, if we're white, we start the game
                if PI_VS_PI_MODE and PI_COLOR == 'white':
                    # Schedule first move in a separate thread
                    threading.Thread(target=auto_make_move, daemon=True).start()
                
                return jsonify({
                    'status': 'success',
                    'message': 'Game reset to starting position',
                    'board_state': get_board_state()
                })
        
        elif command == 'pause':
            game_active = False
            return jsonify({
                'status': 'success',
                'message': 'Game paused'
            })
        
        elif command == 'resume':
            game_active = True
            # In PI vs PI mode, if it's our turn, make a move
            if PI_VS_PI_MODE and is_my_turn():
                threading.Thread(target=auto_make_move, daemon=True).start()
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

@app.route('/api/set-bot-difficulty', methods=['POST'])
def set_bot_difficulty():
    """Set bot difficulty level (ELO and skill)"""
    try:
        if not engine:
            return jsonify({
                'status': 'error',
                'message': 'Engine not initialized'
            }), 500
        
        data = request.get_json()
        elo = data.get('elo', 1000)
        skill = data.get('skill', 10)
        
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
        print(f"Board reset to starting position")
        
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

@app.route('/api/engine-config', methods=['POST'])
def configure_engine():
    """Configure engine settings"""
    try:
        if not engine:
            return jsonify({
                'status': 'error',
                'message': 'Engine not initialized'
            }), 500
        
        data = request.get_json()
        skill_level = data.get('skill_level', 10)
        elo_rating = data.get('elo_rating', 1350)
        
        engine.configure({
            "Skill Level": skill_level,
            "UCI_LimitStrength": True,
            "UCI_Elo": elo_rating
        })
        
        return jsonify({
            'status': 'success',
            'message': f'Engine configured: Skill Level {skill_level}, ELO {elo_rating}'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Configuration error: {str(e)}'
        }), 500

def cleanup():
    """Cleanup resources"""
    global engine
    if engine:
        engine.quit()
        print("Chess engine closed")

if __name__ == '__main__':
    print("Starting Raspberry Pi Chess Server...")
    
    # Display configuration
    if PI_VS_PI_MODE:
        print(f"PI vs PI Mode: ENABLED")
        print(f"This PI plays: {PI_COLOR.upper()}")
        print(f"Opponent PI: {OPPONENT_IP}:{OPPONENT_PORT}")
    else:
        print("PI vs PI Mode: DISABLED (User vs PI mode)")
    
    # Initialize chess engine
    if initialize_engine():
        print("Server ready!")
        
        # In PI vs PI mode, if we're white, start the game after a short delay
        if PI_VS_PI_MODE and PI_COLOR == 'white':
            print(f"PI {PI_COLOR.upper()}: Will make first move in 2 seconds...")
            def start_game():
                time.sleep(2)
                if not board.is_game_over():
                    auto_make_move()
            threading.Thread(target=start_game, daemon=True).start()
        
        try:
            app.run(host='0.0.0.0', port=5002, debug=False)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            cleanup()
    else:
        print("Failed to initialize chess engine. Server cannot start.")
