/* 
Main JavaScript - Initialization and global variables
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/static/CSS/main.js
*/

//------------------------------------------------------------------------------
//
// Global Variables
//
// description:
//  These variables manage the overall game state, connection status, and
//  timing control for the AI Chess GUI.
//
//------------------------------------------------------------------------------

let selectedPiece = null;
let gameMoves = [];
let moveNumber = 1;
let isGamePaused = false;
let currentMoveIndex = -1; // -1 means at the beginning, 0+ means at that move
let boardHistory = []; // Store board states for navigation
let gameSpeed = 10; // Game speed in G/sec
let piConnected = false;
let connectionCheckInterval = null;

//------------------------------------------------------------------------------
//
// function: DOMContentLoaded
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Initializes the chessboard, pieces, control systems, and connection checks
//  once the web page is fully connected
//
//------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function() {
    createChessBoard();
    setupPieces();
    initializeBotSelector();
    setupGameControls();
    checkPiConnection();
    startConnectionMonitoring();
    
    // Initially disable game controls until bot is selected
    disableGameControls();
});

//------------------------------------------------------------------------------
//
// function: checkPiConnection
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Sends connection to the backend to check if the Raspberry PI is connected.
//  Updates global connection status and user interface accordingly
//
//------------------------------------------------------------------------------

async function checkPiConnection() {
    try {
        const response = await fetch('/api/pi-status');
        const result = await response.json();
        
        if (result.status === 'connected') {
            piConnected = true;
            updateConnectionStatus('Connected to Raspberry Pi', 'connected');
        } else {
            piConnected = false;
            updateConnectionStatus('Disconnected from Raspberry Pi', 'disconnected');
        }
    } catch (error) {
        piConnected = false;
        updateConnectionStatus('Cannot connect to Raspberry Pi', 'disconnected');
    }
}

//------------------------------------------------------------------------------
//
// function: startConnectionMonitoring
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Continuosly monitors the Raspberry PI connection every 10 seconds
//  by repeading 'checkPiConnection' function
//
//------------------------------------------------------------------------------

function startConnectionMonitoring() {
    // Check connection every 10 seconds
    connectionCheckInterval = setInterval(checkPiConnection, 10000);
}

//------------------------------------------------------------------------------
//
// function: updateConnectionStatus
//
// arguments:
//  message: string representing the connection status message
//  status: string either "connected" or "disconnected"
//
// returns:
//  nothing
//
// description:
//  Updates the UI element showing the current state of the PI
//  including visual indicator and visual message
//
//------------------------------------------------------------------------------

function updateConnectionStatus(message, status) {
    const statusElement = document.getElementById('click-status');
    const originalText = statusElement.textContent;
    
    // Add connection indicator
    const indicator = status === 'connected' ? '🟢' : '🔴';
    statusElement.textContent = `${indicator} ${message}`;
    
    // If this was just a status check and not an error, restore original text after 2 seconds
    if (originalText !== 'Click on a square to test interaction' && 
        !originalText.includes('Error:') && 
        !originalText.includes('Processing') &&
        !originalText.includes('Engine is thinking')) {
        setTimeout(() => {
            if (statusElement.textContent === `${indicator} ${message}`) {
                statusElement.textContent = originalText;
            }
        }, 2000);
    }
}

//------------------------------------------------------------------------------
//
// function: resetSelection
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Clears any currently selected chess piece and updates the status message
//  depending on the connection state to the raspberry PI
//
//------------------------------------------------------------------------------

function resetSelection() {
    if (selectedPiece) {
        selectedPiece.element.classList.remove('selected');
        selectedPiece = null;
    }
    
    if (piConnected) {
        document.getElementById('click-status').textContent = 'Click on a square to test interaction';
    } else {
        document.getElementById('click-status').textContent = '🔴 Not connected to Raspberry Pi';
    }
}
//
// End of file