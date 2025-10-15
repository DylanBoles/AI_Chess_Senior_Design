/* 
Game JavaScript - Game logic, move validation, game state
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/static/CSS/game.js
*/

//------------------------------------------------------------------------------
//
// function: getPieceNameFromCode
//
// arguments:
//  pieceCode: String representing the piece ("wK", "bQ")
//
// returns:
//  string: full name of the piece or "Empty/Unknown piece" ("wk" == "White King")
//
// description:
//  For Logging, Converts a piece into a human readable piece name for display logging
//
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: getPieceSymbol
//
// arguments:
//  pieceCode: String representing the piece ("wK", "bQ")
//
// returns:
//  string: Unicode chess symbole corresponding to its respected piece
//
// description:
//  For Visual Representation (Retrieves the proper unicode symbol for piece code)
//
//------------------------------------------------------------------------------

function getPieceSymbol(pieceCode) {
    const symbols = {
        'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
        'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟'
    };
    return symbols[pieceCode] || '?';
}

//------------------------------------------------------------------------------
//
// function: initializeMovesPanel
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Set up the panel with UI default of "No moves yet" message
//
//------------------------------------------------------------------------------

function initializeMovesPanel() {
    const movesList = document.getElementById('moves-list');
    movesList.innerHTML = '<div style="text-align: center; color: #888; font-style: italic;">No moves yet</div>';
}

//------------------------------------------------------------------------------
//
// function: recordMove
//
// arguments:
//  pieceCode: string represents the moved piece ("wk" or "wN") 
//  fromPosition: string repesents starting square (e4, or f5)
//  toPosition: string repesents ending square (e6 or f6)
//
// returns:
//  nothing
//
// description:
//  Records a move into the game history, increment the move count
//  and referesh the move display panel
//
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: updateMovesDisplay
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Updates all the moves panel to display all moves made so far
// Groups white and black under respective their move numbers.
//
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: formatMove
//
// arguments:
//  move: object containing piece from and to fields
//
// returns:
//  string formated move with piece symbol and positions
//
// description:
//  Converts a move object into a user-readable string for display in the moves panel.
//
//------------------------------------------------------------------------------

function formatMove(move) {
    const pieceSymbol = getPieceSymbol(move.piece);
    return `${pieceSymbol}${move.from}-${move.to}`;
}
//
// End of file