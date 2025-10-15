/* 
Controls JavaScript - All control button functionality
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/static/CSS/controls.js
*/

//------------------------------------------------------------------------------
//
// function: setupGameControls
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Initializes all control buttons and sets up their event listeners.
//  Also Manages the game speed slider and initial board state
//
//------------------------------------------------------------------------------

function setupGameControls() {
    const pauseBtn = document.getElementById('pause-btn');
    const playBtn = document.getElementById('play-btn');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const resetBtn = document.getElementById('reset-btn');
    // const newGameBtn = document.getElementById('new-game-btn');
    const speedSlider = document.getElementById('speed-slider');
    
    pauseBtn.addEventListener('click', pauseGame);
    playBtn.addEventListener('click', resumeGame);
    prevBtn.addEventListener('click', previousMove);
    nextBtn.addEventListener('click', nextMove);
    resetBtn.addEventListener('click', resetToCurrentGame);
    // newGameBtn.addEventListener('click', resetGame);
    
    // Speed slider functionality
    speedSlider.addEventListener('input', function() {
        gameSpeed = parseInt(this.value);
        document.getElementById('speed-value').textContent = gameSpeed;
        
        // Update warning text based on speed
        const warning = document.querySelector('.speed-warning');
        if (gameSpeed >= 10) {
            warning.textContent = 'Must be <10 g/sec to see chessboard';
            warning.style.color = '#ff0000';
        } else {
            warning.textContent = 'Speed OK - chessboard visible';
            warning.style.color = '#000000';
        }
    });
    
    // Initialize board history with starting position
    saveBoardState();
}

//------------------------------------------------------------------------------
//
// function: pauseGame
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Pauses the game, disables board interaction, and enables move navigation
//
//------------------------------------------------------------------------------

function pauseGame() {
    isGamePaused = true;
    
    // Hide pause button, show play button
    document.getElementById('pause-btn').style.display = 'none';
    document.getElementById('play-btn').style.display = 'block';
    
    // Clear any current selection
    resetSelection();
    
    // Update status message
    document.getElementById('click-status').textContent = 'Game paused. Use navigation buttons to review moves.';
    
    // Add visual indication that game is paused
    const board = document.getElementById('chessboard');
    board.style.opacity = '0.7';
    board.style.pointerEvents = 'none';
    
    // Update navigation button states
    updateNavigationButtons();
}

//------------------------------------------------------------------------------
//
// function: resumeGame
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Resumes normal gameplay, and re-enables board interaction
//
//------------------------------------------------------------------------------

function resumeGame() {
    isGamePaused = false;
    
    // Hide play button, show pause button
    document.getElementById('play-btn').style.display = 'none';
    document.getElementById('pause-btn').style.display = 'block';
    
    // Reset to current game state
    resetToCurrentGame();
    
    // Update status message
    document.getElementById('click-status').textContent = 'Click on a square to test interaction';
    
    // Remove visual indication that game is paused
    const board = document.getElementById('chessboard');
    board.style.opacity = '1';
    board.style.pointerEvents = 'auto';
}

//------------------------------------------------------------------------------
//
// function: updateGameControls
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Synchronizes button states and board interactivity
//  with the current pause/resume status.
//
//------------------------------------------------------------------------------

function updateGameControls() {
    if (isGamePaused) {
        // show play button and disable board
        document.getElementById('pause-btn').style.display = 'none';
        document.getElementById('play-btn').style.display = 'block';
        
        const board = document.getElementById('chessboard');
        board.style.opacity = '0.7';
        board.style.pointerEvents = 'none';
    } else {
        // show pause button and enable board
        document.getElementById('play-btn').style.display = 'none';
        document.getElementById('pause-btn').style.display = 'block';
        
        const board = document.getElementById('chessboard');
        board.style.opacity = '1';
        board.style.pointerEvents = 'auto';
    }
    
    // Always refresh navigation button states
    updateNavigationButtons();
}
//
// End of file