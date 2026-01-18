"""
Web Application Server for AI Chess GUI (API Endpoints for Flask)
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/app.py

import system modules & Libraries
"""
from flask import Flask, render_template, jsonify, request
import requests
import json
from config import PI_BASE_URL, FLASK_HOST, FLASK_PORT, FLASK_DEBUG, MOVE_TIMEOUT, ENGINE_TIMEOUT

""" Determin the root path """
app = Flask(__name__)

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


@app.route('/api/test-pi-connection')
def test_pi_connection():
    """ 
    This will check whether the Raspberry PI chess server is online and reachable 

    This endpoint sends a 'GET' request to the Raspberry PI's '/api/status' endpoint to verify:
    - The Pi server is running and reachable over the network.
    - The Pi responds successfully within the time out period which is == 5 seconds

    Returns:
        JSON Response containing:
            - 'Status': 'success' if connection succeeded, 'error' otherwise
            - 'message': Description of the connection result
            - 'pi_response': The Pi's response body or error details
    
    Log the Pi’s HTTP status code and response text to the console
    If the Pi responds successfully (HTTP 200 OK)  

    """
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
    """
    Get current board state from the Pi
    
    Request "GET" the board state with a timeout of 5 seconds
    If it is successful return 200 otherwise return error and 500
    Check for Network errors

    """
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
    """
    Get the engine's move from the Pi

    Request 'POST' to retreive the stockfish or chess engines move in response to player
    request the board state From the engine unless the Request times out (15 Seconds)

    If it is successful return 200 otherwise return error and 500
    Check for Network Errors
    
    """
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

@app.route('/api/pi-status', methods=['GET'])
def check_pi_status():
    """
    Check if the Raspberry Pi is connected and responsive
    We check if the Pi is connected via the network otherwise we send an error
    If it is successful return 200 otherwise return error and 500

    Send 503 message if disconnected

    Wait/Time out time of 3 seconds

    """
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
        data = request.get_json()
        elo = data.get('elo')
        skill = data.get('skill')
        
        if not elo or not skill:
            return jsonify({
                'status': 'error',
                'message': 'ELO rating and skill level are required'
            }), 400
        
        print(f"Laptop: Setting bot difficulty - ELO: {elo}, Skill: {skill}")
        
        response = requests.post(f"{PI_BASE_URL}/api/set-bot-difficulty", 
                               json={'elo': elo, 'skill': skill}, 
                               timeout=5)
        
        print(f"Laptop: Pi response status: {response.status_code}")
        print(f"Laptop: Pi response: {response.text}")
        
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to set bot difficulty on Pi'
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': f'Connection error: {str(e)}'
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

""" 
Send in:
    host: 0.0.0.0
    port: 5001
    debug: True

"""
if __name__ == '__main__':
    app.run(debug=FLASK_DEBUG, host=FLASK_HOST, port=FLASK_PORT)