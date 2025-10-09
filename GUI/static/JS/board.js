/* 
Board Initialization, Creation and Piece Management
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/static/CSS/board.js
*/

/* 
Create the chess board structure and makes an ID for this called 'chessboard', define the tanks 1 - 8 and files a - h
defines click events for the moves and colors classes (white or black)

Function Details:
    - clears and existing board content to reset the layout
    - Iterates throught the 8 ranks and 8 files to make a total of 64 squares
    - Assigns each square
        - a color class based on position (alternating b & w)
        - coordincate data attributes (row, col, and chess position ex. "e4")
        - a click event listener that triggers 'handleSquareClick()' when pressed
    - Appends each completed row to the main board container

The created structure makes a playable game grid used by the game logic allowing users to select and move pieces

Dependencies:
- HTML element with ID "chessboard" must exist in the Document Object Model(DOM)

*/
function createChessBoard() {
    const board = document.getElementById('chessboard');
    board.innerHTML = '';

    const files = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'];
    const ranks = ['8', '7', '6', '5', '4', '3', '2', '1'];

    for (let row = 0; row < 8; row++) {
        const boardRow = document.createElement('div');
        boardRow.className = 'board-row';

        for (let col = 0; col < 8; col++) {
            const square = document.createElement('div');
            square.className = `square ${(row + col) % 2 === 0 ? 'white' : 'black'}`;
            square.dataset.row = row;
            square.dataset.col = col;
            square.dataset.position = files[col] + ranks[row];

            // Add click event
            square.addEventListener('click', function() {
                handleSquareClick(this);
            });

            boardRow.appendChild(square);
        }
        board.appendChild(boardRow);
    }
}

// Set up the initial chess pieces with piece calls
function setupPieces() {
    const pieces = {
        // Black pieces (row 0-1)
        'a8': 'bR', 'b8': 'bN', 'c8': 'bB', 'd8': 'bQ', 'e8': 'bK', 'f8': 'bB', 'g8': 'bN', 'h8': 'bR',
        'a7': 'bP', 'b7': 'bP', 'c7': 'bP', 'd7': 'bP', 'e7': 'bP', 'f7': 'bP', 'g7': 'bP', 'h7': 'bP',
        
        // White pieces (row 6-7)
        'a2': 'wP', 'b2': 'wP', 'c2': 'wP', 'd2': 'wP', 'e2': 'wP', 'f2': 'wP', 'g2': 'wP', 'h2': 'wP',
        'a1': 'wR', 'b1': 'wN', 'c1': 'wB', 'd1': 'wQ', 'e1': 'wK', 'f1': 'wB', 'g1': 'wN', 'h1': 'wR'
    };

    // Place pieces on the board
    for (const [position, pieceCode] of Object.entries(pieces)) {
        const square = document.querySelector(`.square[data-position="${position}"]`);
        if (square) {
            addPieceToSquare(square, pieceCode);
        }
    }
}

// Add a piece to a square using images
function addPieceToSquare(square, pieceCode) {
    // Clear any existing content
    square.textContent = '';
    
    // Remove any existing piece classes
    const pieceClasses = ['piece', 'piece-wK', 'piece-wQ', 'piece-wR', 'piece-wB', 'piece-wN', 'piece-wP', 
                         'piece-bK', 'piece-bQ', 'piece-bR', 'piece-bB', 'piece-bN', 'piece-bP'];
    square.classList.remove(...pieceClasses);
    
    // Add the piece class
    square.classList.add('piece', `piece-${pieceCode}`);
    square.dataset.piece = pieceCode;
}

// Remove a piece from a square
function removePieceFromSquare(square) {
    const pieceClasses = ['piece', 'piece-wK', 'piece-wQ', 'piece-wR', 'piece-wB', 'piece-wN', 'piece-wP', 
                         'piece-bK', 'piece-bQ', 'piece-bR', 'piece-bB', 'piece-bN', 'piece-bP'];
    square.classList.remove(...pieceClasses);
    delete square.dataset.piece;
    square.textContent = '';
}

// Handle square clicks
function handleSquareClick(square) {
    // Check if Pi is connected
    if (!piConnected) {
        document.getElementById('click-status').textContent = '🔴 Not connected to Raspberry Pi. Cannot make moves.';
        return;
    }
    
    // Don't allow moves when game is paused
    if (isGamePaused) {
        document.getElementById('click-status').textContent = 'Game is paused. Click Play to resume.';
        return;
    }
    
    const position = square.dataset.position;
    const hasPiece = square.dataset.piece; // Check if square has a piece using dataset.piece
    
    // If no piece is selected and this square has a piece
    if (!selectedPiece && hasPiece) {
        selectPiece(square, position);
    } 
    // If we have a selected piece and click on another square
    else if (selectedPiece && selectedPiece.element !== square) {
        movePiece(square, position);
    }
    // Clicking the same square or empty square resets selection
    else {
        resetSelection();
    }
}

// Select a piece Gets the actual Coords
function selectPiece(square, position) {
    selectedPiece = {
        element: square,
        position: position,
        pieceCode: square.dataset.piece
    };
    square.classList.add('selected');
    
    document.getElementById('click-status').textContent = 
        `Selected: ${position} (${getPieceNameFromCode(square.dataset.piece)})`;
}

// Move a piece and send to backend
function movePiece(targetSquare, targetPosition) {
    const pieceCode = selectedPiece.element.dataset.piece;
    const fromPosition = selectedPiece.position;
    
    // Show loading state
    document.getElementById('click-status').textContent = 'Processing move...';
    
    // Send move to backend API
    sendMoveToBackend(pieceCode, fromPosition, targetPosition)
        .then(response => {
            if (response.status === 'success') {
                // Move was accepted by the engine
                if (response.move_accepted) {
                    // Update the board using the Pi's board state
                    updateBoardFromPiState(response.board_state);
                    
                    // Record the move
                    recordMove(pieceCode, fromPosition, targetPosition);
                    
                    // Save board state for navigation
                    saveBoardState();
                    
                    document.getElementById('click-status').textContent = 
                        `Moved ${getPieceNameFromCode(pieceCode)} from ${fromPosition} to ${targetPosition}`;
                    
                    // Check if game is over
                    if (response.game_over) {
                        document.getElementById('click-status').textContent = 
                            `Game Over! Winner: ${response.winner || 'Draw'}`;
                        isGamePaused = true;
                        updateGameControls();
                    } else {
                        // Get engine's move after a short delay
                        setTimeout(() => {
                            getEngineMove();
                        }, 500);
                    }
                } else {
                    // Move was rejected - don't update the board
                    document.getElementById('click-status').textContent = 
                        `Invalid move: ${fromPosition} to ${targetPosition}. Try refreshing the board.`;
                    
                    // Offer to sync the board state
                    setTimeout(() => {
                        if (confirm("Board state may be out of sync. Reset the game?")) {
                            resetGame();
                        }
                    }, 1000);
                }
            } else {
                // Error occurred
                document.getElementById('click-status').textContent = 
                    `Error: ${response.message}`;
            }
        })
        .catch(error => {
            console.error('Move error:', error);
            document.getElementById('click-status').textContent = 
                'Connection error. Please try again.';
        });
    
    // Clear selection
    selectedPiece.element.classList.remove('selected');
    selectedPiece = null;
}

// Send move to backend API
async function sendMoveToBackend(pieceCode, fromPosition, toPosition) {
    const moveData = {
        from: fromPosition,
        to: toPosition,
        piece: pieceCode,
        move_number: moveNumber
    };
    
    try {
        const response = await fetch('/api/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(moveData)
        });
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Get engine move from backend
async function getEngineMove() {
    try {
        document.getElementById('click-status').textContent = 'Engine is thinking...';
        
        const response = await fetch('/api/engine-move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({})
        });
        
        const result = await response.json();
        
        if (result.status === 'success' && result.engine_move) {
            // Update the board using the Pi's board state
            if (result.board_state) {
                updateBoardFromPiState(result.board_state);
            } else {
                // Fallback to individual move if no board state
                applyEngineMove(result.engine_move);
            }
            
            // Record the move
            recordMove(result.engine_move.piece, result.engine_move.from, result.engine_move.to);
            
            // Save board state
            saveBoardState();
            
            document.getElementById('click-status').textContent = 
                `Engine moved: ${result.engine_move.from} to ${result.engine_move.to}`;
            
            // Check if game is over
            if (result.game_over) {
                document.getElementById('click-status').textContent = 
                    `Game Over! Winner: ${result.winner || 'Draw'}`;
                isGamePaused = true;
                updateGameControls();
            }
        } else {
            document.getElementById('click-status').textContent = 
                `Engine error: ${result.message}`;
        }
    } catch (error) {
        console.error('Engine move error:', error);
        document.getElementById('click-status').textContent = 
            'Failed to get engine move. Please try again.';
    }
}

// Update the entire board from Pi's board state
function updateBoardFromPiState(boardState) {
    // Clear all pieces first
    const squares = document.querySelectorAll('.square');
    squares.forEach(square => {
        removePieceFromSquare(square);
    });
    
    // Add pieces based on Pi's board state
    for (const [position, pieceSymbol] of Object.entries(boardState)) {
        const square = document.querySelector(`.square[data-position="${position}"]`);
        if (square) {
            // Convert chess library piece symbols to our piece codes
            const pieceCode = convertPieceSymbolToCode(pieceSymbol);
            if (pieceCode) {
                addPieceToSquare(square, pieceCode);
            }
        }
    }
}

// Convert chess library piece symbols to our piece codes
function convertPieceSymbolToCode(pieceSymbol) {
    const pieceMap = {
        'K': 'wK', 'Q': 'wQ', 'R': 'wR', 'B': 'wB', 'N': 'wN', 'P': 'wP',
        'k': 'bK', 'q': 'bQ', 'r': 'bR', 'b': 'bB', 'n': 'bN', 'p': 'bP'
    };
    return pieceMap[pieceSymbol] || null;
}

// Apply engine move to the board
function applyEngineMove(engineMove) {
    const fromSquare = document.querySelector(`.square[data-position="${engineMove.from}"]`);
    const toSquare = document.querySelector(`.square[data-position="${engineMove.to}"]`);
    
    if (fromSquare && toSquare) {
        const pieceCode = fromSquare.dataset.piece;
        
        // Remove piece from original square
        removePieceFromSquare(fromSquare);
        
        // Add piece to target square
        addPieceToSquare(toSquare, pieceCode);
    }
}

// Reset the game
async function resetGame() {
    try {
        document.getElementById('click-status').textContent = 'Resetting game...';
        
        // Send reset command to Pi
        const response = await fetch('/api/game-control', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ command: 'reset' })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            // Reset the frontend board to starting position
            setupPieces();
            
            // Clear move history
            gameMoves = [];
            moveNumber = 1;
            boardHistory = [];
            currentMoveIndex = -1;
            
            // Update moves display
            updateMovesDisplay();
            
            // Save initial board state
            saveBoardState();
            
            document.getElementById('click-status').textContent = 'Game reset successfully!';
        } else {
            document.getElementById('click-status').textContent = `Reset failed: ${result.message}`;
        }
    } catch (error) {
        console.error('Reset error:', error);
        document.getElementById('click-status').textContent = 'Failed to reset game.';
    }
}


