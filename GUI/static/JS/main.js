// Main JavaScript - Initialization and global variables

// Global variables
let selectedPiece = null;
let gameMoves = [];
let moveNumber = 1;
let isGamePaused = false;
let currentMoveIndex = -1; // -1 means at the beginning, 0+ means at that move
let boardHistory = []; // Store board states for navigation
let gameSpeed = 10; // Game speed in G/sec
let piConnected = false;
let connectionCheckInterval = null;

// Initialize the chess board when page loads
document.addEventListener('DOMContentLoaded', function() {
    createChessBoard();
    setupPieces();
    initializeMovesPanel();
    setupGameControls();
    checkPiConnection();
    startConnectionMonitoring();
});

// Check connection to Raspberry Pi
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

// Start monitoring connection status
function startConnectionMonitoring() {
    // Check connection every 10 seconds
    connectionCheckInterval = setInterval(checkPiConnection, 10000);
}

// Update connection status display
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

// Reset selection and highlights
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


