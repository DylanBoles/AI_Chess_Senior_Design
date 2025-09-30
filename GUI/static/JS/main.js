// Main JavaScript - Initialization and global variables

// Global variables
let selectedPiece = null;
let gameMoves = [];
let moveNumber = 1;
let isGamePaused = false;
let currentMoveIndex = -1; // -1 means at the beginning, 0+ means at that move
let boardHistory = []; // Store board states for navigation
let gameSpeed = 10; // Game speed in G/sec

// Initialize the chess board when page loads
document.addEventListener('DOMContentLoaded', function() {
    createChessBoard();
    setupPieces();
    initializeMovesPanel();
    setupGameControls();
});

// Reset selection and highlights
function resetSelection() {
    if (selectedPiece) {
        selectedPiece.element.classList.remove('selected');
        selectedPiece = null;
    }
    document.getElementById('click-status').textContent = 'Click on a square to test interaction';
}
