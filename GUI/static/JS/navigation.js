// Navigation JavaScript - Move navigation and history

// Save current board state to history
function saveBoardState() {
    const boardState = [];
    const squares = document.querySelectorAll('.square');
    
    squares.forEach(square => {
        const position = square.dataset.position;
        const piece = square.dataset.piece || null;
        boardState.push({ position, piece });
    });
    
    boardHistory.push(boardState);
    currentMoveIndex = boardHistory.length - 1;
}

// Load board state from history
function loadBoardState(moveIndex) {
    if (moveIndex < 0 || moveIndex >= boardHistory.length) return;
    
    const boardState = boardHistory[moveIndex];
    
    // Clear all pieces
    const squares = document.querySelectorAll('.square');
    squares.forEach(square => {
        removePieceFromSquare(square);
    });
    
    // Restore pieces
    boardState.forEach(({ position, piece }) => {
        if (piece) {
            const square = document.querySelector(`.square[data-position="${position}"]`);
            if (square) {
                addPieceToSquare(square, piece);
            }
        }
    });
    
    currentMoveIndex = moveIndex;
    updateNavigationButtons();
}

// Go to previous move
function previousMove() {
    if (currentMoveIndex > 0) {
        loadBoardState(currentMoveIndex - 1);
        document.getElementById('click-status').textContent = 
            `Viewing move ${currentMoveIndex} of ${boardHistory.length - 1}`;
    }
}

// Go to next move
function nextMove() {
    if (currentMoveIndex < boardHistory.length - 1) {
        loadBoardState(currentMoveIndex + 1);
        document.getElementById('click-status').textContent = 
            `Viewing move ${currentMoveIndex} of ${boardHistory.length - 1}`;
    }
}

// Reset to current game state
function resetToCurrentGame() {
    loadBoardState(boardHistory.length - 1);
    document.getElementById('click-status').textContent = 'Back to current game state';
}

// Update navigation button states
function updateNavigationButtons() {
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    
    // Enable/disable previous button
    prevBtn.disabled = currentMoveIndex <= 0;
    
    // Enable/disable next button
    nextBtn.disabled = currentMoveIndex >= boardHistory.length - 1;
}


