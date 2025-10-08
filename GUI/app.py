## this is my app..........
from flask import Flask, render_template, jsonify, request
import requests
import json
from config import PI_BASE_URL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG, MOVE_TIMEOUT, ENGINE_TIMEOUT

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/test')
def test_api():
    return jsonify({
        'message': 'API is working!',
        'status': 'success',
        'chess': '♔♕♖♗♘♙'
    })

@app.route('/api/test-pi-connection')
def test_pi_connection():
    """Test connection to Raspberry Pi"""
    try:
        print(f"Testing connection to Pi at: {PI_BASE_URL}/api/status")
        response = requests.get(f"{PI_BASE_URL}/api/status", timeout=5)
        print(f"Pi response status: {response.status_code}")
        print(f"Pi response: {response.text}")
        
        if response.status_code == 200:
            return jsonify({
                'status': 'success',
                'message': 'Connected to Pi successfully',
                'pi_response': response.json()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Pi returned status {response.status_code}',
                'pi_response': response.text
            }), 500
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Cannot connect to Pi: {str(e)}'
        }), 500

@app.route('/api/move', methods=['POST'])
def handle_move():
    """Handle a move from the frontend and send it to the Pi"""
    try:
        data = request.get_json()
        move_data = {
            'from': data.get('from'),
            'to': data.get('to'),
            'piece': data.get('piece'),
            'move_number': data.get('move_number', 1)
        }
        
        print(f"Laptop: Sending move to Pi: {move_data}")
        print(f"Laptop: Pi URL: {PI_BASE_URL}/api/move")
        
        # Send move to Raspberry Pi
        response = requests.post(f"{PI_BASE_URL}/api/move", 
                               json=move_data, 
                               timeout=MOVE_TIMEOUT)
        
        print(f"Laptop: Pi response status: {response.status_code}")
        print(f"Laptop: Pi response: {response.text}")
        
        if response.status_code == 200:
            pi_response = response.json()
            return jsonify({
                'status': 'success',
                'move_accepted': pi_response.get('move_accepted', True),
                'board_state': pi_response.get('board_state'),
                'game_over': pi_response.get('game_over', False),
                'winner': pi_response.get('winner')
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to communicate with Raspberry Pi'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        }), 500
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Server error: {str(e)}'
        }), 500

@app.route('/api/board-state', methods=['GET'])
def get_board_state():
    """Get current board state from the Pi"""
    try:
        response = requests.get(f"{PI_BASE_URL}/api/board-state", timeout=5)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get board state from Pi'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        }), 500

@app.route('/api/engine-move', methods=['POST'])
def get_engine_move():
    """Get the engine's move from the Pi"""
    try:
        response = requests.post(f"{PI_BASE_URL}/api/engine-move", 
                               json={'board_state': request.get_json()}, 
                               timeout=ENGINE_TIMEOUT)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to get engine move from Pi'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        }), 500

@app.route('/api/game-control', methods=['POST'])
def game_control():
    """Send game control commands to the Pi"""
    try:
        data = request.get_json()
        command = data.get('command')  # 'pause', 'resume', 'reset', 'new_game'
        
        response = requests.post(f"{PI_BASE_URL}/api/game-control", 
                               json={'command': command}, 
                               timeout=5)
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send command to Pi'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        }), 500

@app.route('/api/pi-status', methods=['GET'])
def check_pi_status():
    """Check if the Raspberry Pi is connected and responsive"""
    try:
        response = requests.get(f"{PI_BASE_URL}/api/status", timeout=3)
        
        if response.status_code == 200:
            return jsonify({
                'status': 'connected',
                'pi_response': response.json()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Pi responded with error'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'disconnected',
            'message': f'Cannot connect to Pi: {str(e)}'
        }), 503

@app.route('/api/game-control', methods=['POST'])
def handle_game_control():
    """Handle game control commands"""
    try:
        data = request.get_json()
        command = data.get('command')
        
        print(f"Laptop: Sending game control command to Pi: {command}")
        
        response = requests.post(f"{PI_BASE_URL}/api/game-control", 
                               json={'command': command}, 
                               timeout=5)
        
        print(f"Laptop: Pi response status: {response.status_code}")
        print(f"Laptop: Pi response: {response.text}")
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to send command to Pi'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)