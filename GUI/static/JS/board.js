// Board JavaScript - Chess board creation and piece management

// Create the chess board structure
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

// Set up the initial chess pieces
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

// Select a piece
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

// Move a piece (visual only for now)
function movePiece(targetSquare, targetPosition) {
    const pieceCode = selectedPiece.element.dataset.piece;
    const fromPosition = selectedPiece.position;
    
    // Remove piece from original square
    removePieceFromSquare(selectedPiece.element);
    
    // Add piece to target square
    addPieceToSquare(targetSquare, pieceCode);
    
    // Record the move
    recordMove(pieceCode, fromPosition, targetPosition);
    
    // Save board state for navigation
    saveBoardState();
    
    // Clear selection
    selectedPiece.element.classList.remove('selected');
    
    document.getElementById('click-status').textContent = 
        `Moved ${getPieceNameFromCode(pieceCode)} from ${selectedPiece.position} to ${targetPosition}`;
    
    // Reset selection
    selectedPiece = null;
}
