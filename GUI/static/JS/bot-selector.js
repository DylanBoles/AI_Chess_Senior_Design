// Bot Selector JavaScript - Handle bot selection and game initialization
// Date: 10/08/2025
// file: /AI_Chess_Senior_Design/GUI/static/JS/bot-selector.js

// Global variables for bot selection
let selectedBot = null;
let gameStarted = false;

// Initialize bot selector when page loads
function initializeBotSelector() {
    const botOptions = document.querySelectorAll('.bot-option');
    const startGameBtn = document.getElementById('start-game-btn');
    
    // Add click event listeners to bot options
    botOptions.forEach(option => {
        option.addEventListener('click', function() {
            selectBot(this);
        });
    });
    
    // Add click event listener to start game button
    startGameBtn.addEventListener('click', function() {
        startGame();
    });
}

// Select a bot
function selectBot(botElement) {
    // Remove previous selection
    document.querySelectorAll('.bot-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    // Add selection to clicked bot
    botElement.classList.add('selected');
    
    // Store selected bot data
    selectedBot = {
        name: botElement.querySelector('.bot-name').textContent,
        elo: botElement.dataset.elo,
        skill: botElement.dataset.skill
    };
    
    // Show selected bot info
    showSelectedBotInfo();
}

// Show selected bot information
function showSelectedBotInfo() {
    const selectedBotInfo = document.getElementById('selected-bot-info');
    const selectedBotName = document.getElementById('selected-bot-name');
    const selectedBotElo = document.getElementById('selected-bot-elo');
    
    selectedBotName.textContent = selectedBot.name;
    selectedBotElo.textContent = `${selectedBot.elo} ELO`;
    selectedBotInfo.style.display = 'block';
}

// Start the game with selected bot
async function startGame() {
    if (!selectedBot) {
        alert('Please select a bot first!');
        return;
    }
    
    if (!piConnected) {
        alert('Cannot start game: Not connected to Raspberry Pi');
        return;
    }
    
    try {
        // Show loading state
        document.getElementById('click-status').textContent = 'Starting game...';
        
        // Send bot selection to backend
        const response = await fetch('/api/set-bot-difficulty', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                elo: parseInt(selectedBot.elo),
                skill: parseInt(selectedBot.skill)
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Hide bot selector and show game moves
            document.getElementById('bot-selector').style.display = 'none';
            document.getElementById('game-moves').style.display = 'block';
            
            // Initialize game state
            gameStarted = true;
            initializeMovesPanel();
            
            // Update the board with the Pi's board state if provided
            if (result.board_state) {
                updateBoardFromPiState(result.board_state);
            } else {
                // Fallback: reset the board to starting position
                setupPieces();
            }
            
            // Save initial board state
            saveBoardState();
            
            // Update status
            document.getElementById('click-status').textContent = 
                `Game started! Playing against ${selectedBot.name} (${selectedBot.elo} ELO)`;
            
            // Enable game controls
            enableGameControls();
            
        } else {
            document.getElementById('click-status').textContent = 
                `Failed to start game: ${result.message}`;
        }
        
    } catch (error) {
        console.error('Start game error:', error);
        document.getElementById('click-status').textContent = 
            'Failed to start game. Please try again.';
    }
}

// Reset to bot selector (called when game is reset)
function resetToBotSelector() {
    gameStarted = false;
    selectedBot = null;
    
    // Hide game moves and show bot selector
    document.getElementById('game-moves').style.display = 'none';
    document.getElementById('bot-selector').style.display = 'block';
    
    // Clear selections
    document.querySelectorAll('.bot-option').forEach(option => {
        option.classList.remove('selected');
    });
    
    document.getElementById('selected-bot-info').style.display = 'none';
    
    // Reset game state
    gameMoves = [];
    moveNumber = 1;
    boardHistory = [];
    currentMoveIndex = -1;
    
    // Disable game controls
    disableGameControls();
    
    // Update status
    document.getElementById('click-status').textContent = 'Select a bot to start playing';
}

// Enable game controls when game starts
function enableGameControls() {
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = '1';
    });
}

// Disable game controls when in bot selector
function disableGameControls() {
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    });
}

// Get current bot information
function getCurrentBot() {
    return selectedBot;
}

// Check if game has started
function isGameStarted() {
    return gameStarted;
}
