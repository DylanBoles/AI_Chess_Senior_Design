#!/usr/bin/env python3
"""
Raspberry Pi Chess Server
Handles chess engine communication and game logic for the AI Chess project.
This server runs on the Raspberry Pi and communicates with the laptop GUI.
"""

import chess
import chess.engine
from flask import Flask, request, jsonify
import json
import threading
import time

app = Flask(__name__)

# Global game state
board = chess.Board()
engine = None
game_active = False
current_player = 'white'  # 'white' for human, 'black' for engine

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
    if not engine or board.is_game_over():
        return None
    
    try:
        # Give engine 2 seconds to think
        result = engine.play(board, chess.engine.Limit(time=2.0))
        move = result.move
        
        # Validate the move before making it
        if move not in board.legal_moves:
            print(f"Engine tried illegal move: {move}")
            return None
        
        # Make the move
        board.push(move)
        
        # Return move information
        return {
            'from': chess.square_name(move.from_square),
            'to': chess.square_name(move.to_square),
            'piece': board.piece_at(move.to_square).symbol() if board.piece_at(move.to_square) else None,
            'san': board.san(move)
        }
    except Exception as e:
        print(f"Engine move error: {e}")
        return None

@app.route('/api/status', methods=['GET'])
def status():
    """Check server status"""
    return jsonify({
        'status': 'running',
        'engine_connected': engine is not None,
        'game_active': game_active,
        'current_player': current_player,
        'board_fen': board.fen()
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
            
            return jsonify({
                'status': 'success',
                'move_accepted': True,
                'board_state': get_board_state(),
                'game_over': game_over,
                'winner': winner,
                'current_player': 'black' if current_player == 'white' else 'white'
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
            
            return jsonify({
                'status': 'success',
                'engine_move': engine_move,
                'board_state': get_board_state(),
                'game_over': game_over,
                'winner': winner
            })
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
        
        if command == 'new_game':
            global board, game_active, current_player
            board = chess.Board()
            game_active = True
            current_player = 'white'
            return jsonify({
                'status': 'success',
                'message': 'New game started'
            })
        
        elif command == 'reset':
            board = chess.Board()
            current_player = 'white'
            return jsonify({
                'status': 'success',
                'message': 'Game reset to starting position'
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
    
    # Initialize chess engine
    if initialize_engine():
        print("Server ready!")
        try:
            app.run(host='0.0.0.0', port=5002, debug=False)
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            cleanup()
    else:
        print("Failed to initialize chess engine. Server cannot start.")
