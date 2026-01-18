// Bot Selector JavaScript - Handle bot selection and game initialization
// Date: 10/08/2025
// file: /AI_Chess_Senior_Design/GUI/static/JS/bot-selector.js

// Global variables for bot selection & game state
let selectedBot = null;
let gameStarted = false;

//------------------------------------------------------------------------------
//
// function: initializeBotSelector
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Sets up event listeners fro bot selection and start game button.
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: selectBot
//
// arguments:
//  botElement
//
// returns:
//  nothing
//
// description:
//  Highlights the selected bot and stores its information globally
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: showSelectedBotInfo
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Displays the selected bot's name and ELO rating in the UI
//------------------------------------------------------------------------------

function showSelectedBotInfo() {
    const selectedBotInfo = document.getElementById('selected-bot-info');
    const selectedBotName = document.getElementById('selected-bot-name');
    const selectedBotElo = document.getElementById('selected-bot-elo');
    
    selectedBotName.textContent = selectedBot.name;
    selectedBotElo.textContent = `${selectedBot.elo} ELO`;
    selectedBotInfo.style.display = 'block';
}

//------------------------------------------------------------------------------
//
// function: startGame
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Initializes a new game using the selected bot and updates the board state.
//------------------------------------------------------------------------------

async function startGame() {
    // For CPU vs CPU mode, skip bot selection
    if (currentGameMode === "cpu_vs_cpu") {
        await startCpuVsCpuGame();
        return;
    }
    
    // For user vs CPU mode, require bot selection
    if (!selectedBot) {
        alert('Please select a bot first!');
        return;
    }
    
    if (!piConnected) {
        alert('Cannot start game: Engine not ready. Please wait...');
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

//------------------------------------------------------------------------------
//
// function: startCpuVsCpuGame
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Starts a CPU vs CPU game without requiring bot selection
//------------------------------------------------------------------------------

async function startCpuVsCpuGame() {
    if (!piConnected) {
        alert('Cannot start game: Engine not ready. Please wait...');
        return;
    }
    
    try {
        // Show loading state
        document.getElementById('click-status').textContent = 'Starting CPU vs CPU game...';
        
        // Hide bot selector and show game moves
        document.getElementById('bot-selector').style.display = 'none';
        document.getElementById('game-moves').style.display = 'block';
        
        // Initialize game state
        gameStarted = true;
        initializeMovesPanel();
        
        // Reset the board to starting position
        setupPieces();
        
        // Save initial board state
        saveBoardState();
        
        // Update status
        const whiteElo = document.getElementById('white-elo') ? parseInt(document.getElementById('white-elo').value) : 1350;
        const blackElo = document.getElementById('black-elo') ? parseInt(document.getElementById('black-elo').value) : 1350;
        document.getElementById('click-status').textContent = 
            `CPU vs CPU game started! White: ${whiteElo} ELO, Black: ${blackElo} ELO`;
        
        // Enable game controls
        enableGameControls();
        
        // Start the game by making the first move (white starts)
        currentPlayer = "white";
        setTimeout(() => {
            getEngineMove();
        }, 1000);
        
    } catch (error) {
        console.error('Start CPU vs CPU game error:', error);
        document.getElementById('click-status').textContent = 
            'Failed to start CPU vs CPU game. Please try again.';
    }
}

//------------------------------------------------------------------------------
//
// function: resetToBotSelector
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Resets the interface and state variables back to the bot selection screen.
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: enableGameControls
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Enables all game control buttons after a game has started.
//------------------------------------------------------------------------------

function enableGameControls() {
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = '1';
    });
}

//------------------------------------------------------------------------------
//
// function: disableGameControls
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Disables all game control buttons while in bot selection mode.
//------------------------------------------------------------------------------

function disableGameControls() {
    const controlButtons = document.querySelectorAll('.control-btn');
    controlButtons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.5';
    });
}

//------------------------------------------------------------------------------
//
// function: getCurrentBot
//
// arguments:
//  none
//
// returns:
//  Object or null - current bot information or null if none is selected
//
// description:
//  Checks if Game is currently active
//------------------------------------------------------------------------------

function getCurrentBot() {
    return selectedBot;
}

//------------------------------------------------------------------------------
//
// function: isGameStarted
//
// arguments:
//  none
//
// returns:
//  Boolean valu - true if a game is active, false otherwise
//
// description:
//  Checks if Game is currently active
//------------------------------------------------------------------------------

function isGameStarted() {
    return gameStarted;
}
//
// End of file