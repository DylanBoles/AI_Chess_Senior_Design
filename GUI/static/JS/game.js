// Game JavaScript - Game logic, move validation, game state

// Get piece name from code
function getPieceNameFromCode(pieceCode) {
    if (!pieceCode) return 'Empty';
    
    const pieceNames = {
        'wK': 'White King', 'wQ': 'White Queen', 'wR': 'White Rook', 
        'wB': 'White Bishop', 'wN': 'White Knight', 'wP': 'White Pawn',
        'bK': 'Black King', 'bQ': 'Black Queen', 'bR': 'Black Rook', 
        'bB': 'Black Bishop', 'bN': 'Black Knight', 'bP': 'Black Pawn'
    };
    return pieceNames[pieceCode] || 'Unknown Piece';
}

// Get piece symbol for display
function getPieceSymbol(pieceCode) {
    const symbols = {
        'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
        'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟'
    };
    return symbols[pieceCode] || '?';
}

// Initialize the moves panel
function initializeMovesPanel() {
    const movesList = document.getElementById('moves-list');
    movesList.innerHTML = '<div style="text-align: center; color: #888; font-style: italic;">No moves yet</div>';
}

// Record a move in the game history
function recordMove(pieceCode, fromPosition, toPosition) {
    const move = {
        piece: pieceCode,
        from: fromPosition,
        to: toPosition,
        moveNumber: moveNumber,
        isWhite: pieceCode.startsWith('w')
    };
    
    gameMoves.push(move);
    updateMovesDisplay();
    moveNumber++;
}

// Update the moves display
function updateMovesDisplay() {
    const movesList = document.getElementById('moves-list');
    
    if (gameMoves.length === 0) {
        movesList.innerHTML = '<div style="text-align: center; color: #888; font-style: italic;">No moves yet</div>';
        return;
    }
    
    let html = '';
    let currentMoveNumber = 1;
    
    for (let i = 0; i < gameMoves.length; i += 2) {
        const whiteMove = gameMoves[i];
        const blackMove = gameMoves[i + 1];
        
        html += `<div class="move-item">`;
        html += `<span class="move-number">${currentMoveNumber}.</span>`;
        html += `<span class="move-text white-move">${formatMove(whiteMove)}</span>`;
        
        if (blackMove) {
            html += `<span class="move-text black-move">${formatMove(blackMove)}</span>`;
        }
        
        html += `</div>`;
        currentMoveNumber++;
    }
    
    movesList.innerHTML = html;
    
    // Scroll to bottom to show latest moves
    movesList.scrollTop = movesList.scrollHeight;
}

// Format a move for display
function formatMove(move) {
    const pieceSymbol = getPieceSymbol(move.piece);
    return `${pieceSymbol}${move.from}-${move.to}`;
}


