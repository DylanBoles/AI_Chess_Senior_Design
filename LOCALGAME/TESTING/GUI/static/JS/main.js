/* 
Main JavaScript - Initialization and global variables
Date: 10/08/2025
file: /AI_Chess_Senior_Design/GUI/static/CSS/main.js
*/

//------------------------------------------------------------------------------
//
// Global Variables
//
// description:
//  These variables manage the overall game state, connection status, and
//  timing control for the AI Chess GUI.
//
//------------------------------------------------------------------------------

let selectedPiece = null;
let gameMoves = [];
let moveNumber = 1;
let isGamePaused = false;
let currentMoveIndex = -1; // -1 means at the beginning, 0+ means at that move
let boardHistory = []; // Store board states for navigation
let gameSpeed = 10; // Game speed in G/sec
let piConnected = false;
let connectionCheckInterval = null;
let currentGameMode = "user_vs_cpu"; // Track current game mode
let currentPlayer = "white"; // Track current player (white/black)

//------------------------------------------------------------------------------
//
// function: DOMContentLoaded
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Initializes the chessboard, pieces, control systems, and connection checks
//  once the web page is fully connected
//
//------------------------------------------------------------------------------

document.addEventListener('DOMContentLoaded', function() {
    createChessBoard();
    setupPieces();
    initializeBotSelector();
    setupGameControls();
    checkPiConnection();
    startConnectionMonitoring();
    
    // Initially disable game controls until bot is selected
    disableGameControls();

        // --- Overlay mode & difficulty flow ---
    const modeOverlay = document.getElementById('mode-overlay');
    const difficultyOverlay = document.getElementById('difficulty-overlay');
    const overlayUserBtn = document.getElementById('overlay-user-vs-cpu');
    const overlayCpuBtn = document.getElementById('overlay-cpu-vs-cpu');
    const diffBackBtn = document.getElementById('difficulty-back-btn');
    const diffStartBtn = document.getElementById('difficulty-start-btn');
    const leftColumn = document.getElementById('left-difficulty-column');
    const rightColumn = document.getElementById('right-difficulty-column');
    const whiteCards = document.getElementById('white-cards');
    const blackCards = document.getElementById('black-cards');

    // show first overlay on load
    if (modeOverlay) modeOverlay.style.display = 'flex';

    let chosenMode = null;
    let chosenWhiteElo = null;
    let chosenBlackElo = null;

    function clearSelectionIn(container) {
        const cards = container.querySelectorAll('.difficulty-card');
        cards.forEach(c=>c.classList.remove('selected'));
    }

    function addCardListeners(container, isWhite) {
        container.querySelectorAll('.difficulty-card').forEach(card => {
            card.addEventListener('click', () => {
                // single-select behaviour per column
                clearSelectionIn(container);
                card.classList.add('selected');
                const elo = parseInt(card.getAttribute('data-elo'));
                if (isWhite) chosenWhiteElo = elo; else chosenBlackElo = elo;

                // enable start when appropriate
                if (chosenMode === 'user_vs_cpu' && chosenBlackElo) diffStartBtn.disabled = false;
                if (chosenMode === 'cpu_vs_cpu' && chosenWhiteElo && chosenBlackElo) diffStartBtn.disabled = false;
            });
        });
    }

    overlayUserBtn.addEventListener('click', () => {
        chosenMode = 'user_vs_cpu';
        // show only the right column (CPU)
        leftColumn.style.display = 'none';
        rightColumn.style.display = 'block';
        document.getElementById('right-column-title').textContent = 'CPU Engine';
        document.getElementById('difficulty-title').textContent = 'Select CPU Difficulty';
        // reset
        clearSelectionIn(blackCards);
        chosenWhiteElo = null; chosenBlackElo = null; diffStartBtn.disabled = true;
        modeOverlay.style.display = 'none';
        difficultyOverlay.style.display = 'flex';
    });

    overlayCpuBtn.addEventListener('click', () => {
        chosenMode = 'cpu_vs_cpu';
        leftColumn.style.display = 'block';
        rightColumn.style.display = 'block';
        document.getElementById('difficulty-title').textContent = 'Select White and Black Difficulty';
        clearSelectionIn(whiteCards); clearSelectionIn(blackCards);
        chosenWhiteElo = null; chosenBlackElo = null; diffStartBtn.disabled = true;
        modeOverlay.style.display = 'none';
        difficultyOverlay.style.display = 'flex';
    });

    diffBackBtn.addEventListener('click', () => {
        difficultyOverlay.style.display = 'none';
        modeOverlay.style.display = 'flex';
    });

    // add listeners to card pools
    addCardListeners(blackCards, false);
    addCardListeners(whiteCards, true);

    diffStartBtn.addEventListener('click', async () => {
        // build payload depending on mode
        let payload = { mode: chosenMode };
        if (chosenMode === 'user_vs_cpu') {
            payload.black_elo = chosenBlackElo;
        } else {
            payload.white_elo = chosenWhiteElo;
            payload.black_elo = chosenBlackElo;
        }

        // POST to server
        try {
            const response = await fetch('/api/set-game-mode', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Set global game mode
                currentGameMode = chosenMode;
                
                // Hide overlays
                difficultyOverlay.style.display = 'none';
                modeOverlay.style.display = 'none';
                
                // Hide bot selector and show game moves
                const botSelector = document.getElementById('bot-selector');
                const gameMoves = document.getElementById('game-moves');
                if (botSelector) botSelector.style.display = 'none';
                if (gameMoves) gameMoves.style.display = 'block';
                
                // Initialize game state
                gameStarted = true;
                currentPlayer = 'white'; // Always start with white
                
                // Reset board to starting position
                setupPieces();
                initializeMovesPanel();
                saveBoardState();
                
                // Enable game controls
                enableGameControls();
                
                // Start game based on mode
                if (chosenMode === 'cpu_vs_cpu') {
                    // CPU vs CPU: Start automatic play
                    document.getElementById('click-status').textContent = 
                        `CPU vs CPU game started! White: ${chosenWhiteElo} ELO, Black: ${chosenBlackElo} ELO`;
                    setTimeout(() => {
                        getEngineMove();
                    }, 1000);
                } else {
                    // User vs CPU: User plays white, wait for user move
                    document.getElementById('click-status').textContent = 
                        `Game started! You are White. CPU (Black) is ${chosenBlackElo} ELO. Make your move!`;
                }
            } else {
                alert('Error setting mode: ' + (data.message || 'unknown'));
                difficultyOverlay.style.display = 'flex';
            }
        } catch (err) {
            console.error('Failed to set mode', err);
            alert('Failed to contact server');
            difficultyOverlay.style.display = 'flex';
        }
    });

    // Game mode UI logic
    const gameModeSelect = document.getElementById("game-mode");
    const userCpuBox = document.getElementById("user-vs-cpu-difficulty");
    const cpuCpuBox = document.getElementById("cpu-vs-cpu-difficulty");

    gameModeSelect.addEventListener("change", () => {
        const startCpuVsCpuBtn = document.getElementById("start-cpu-vs-cpu-btn");
        if (gameModeSelect.value === "user_vs_cpu") {
            userCpuBox.style.display = "block";
            cpuCpuBox.style.display = "none";
            if (startCpuVsCpuBtn) startCpuVsCpuBtn.style.display = "none";
        } else {
            userCpuBox.style.display = "none";
            cpuCpuBox.style.display = "block";
            if (startCpuVsCpuBtn) startCpuVsCpuBtn.style.display = "block";
        }
    });
    
    // Add event listener for start CPU vs CPU button
    const startCpuVsCpuBtn = document.getElementById("start-cpu-vs-cpu-btn");
    if (startCpuVsCpuBtn) {
        startCpuVsCpuBtn.addEventListener("click", () => {
            // First set the game mode, then start the game
            const mode = document.getElementById("game-mode").value;
            let payload = { mode };
            payload.white_elo = parseInt(document.getElementById("white-elo").value);
            payload.black_elo = parseInt(document.getElementById("black-elo").value);
            
            fetch("/api/set-game-mode", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify(payload)
            })
            .then(res => res.json())
            .then(data => {
                if (data.status === "success") {
                    currentGameMode = mode;
                    startCpuVsCpuGame();
                } else {
                    alert("Error: " + data.message);
                }
            })
            .catch(error => {
                console.error("Error setting game mode:", error);
                alert("Failed to set game mode. Please try again.");
            });
        });
    }
});


//------------------------------------------------------------------------------
//
// function: getElementById
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
// Send listener to the bakc end API to listen for the click of the button
//
//------------------------------------------------------------------------------

// document.getElementById("set-game-mode-btn").addEventListener("click", () => {
//     const mode = document.getElementById("game-mode").value;

//     let payload = { mode };

//     if (mode === "user_vs_cpu") {
// 	payload.black_elo = parseInt(document.getElementById("cpu-elo").value);
//     } else {
// 	payload.white_elo = parseInt(document.getElementById("white-elo").value);
// 	payload.black_elo = parseInt(document.getElementById("black-elo").value);
//     }

//     fetch("/api/set-game-mode", {
// 	method: "POST",
// 	headers: {"Content-Type": "application/json"},
// 	body: JSON.stringify(payload)
//     })
// 	.then(res => res.json())
//     	.then(data => {
// 	    if (data.status === "success") {
// 		currentGameMode = mode; // Store the game mode
// 		console.log("Game mode set", data);
// 		alert("Game mode set to: " + (mode === "user_vs_cpu" ? "User vs Stockfish" : "Stockfish vs Stockfish"));
// 	    } else {
// 		alert("Error: " + data.message);
// 	    }
// 	})
// 	.catch(error => {
// 	    console.error("Error setting game mode:", error);
// 	    alert("Failed to set game mode. Please try again.");
// 	});
// });


//------------------------------------------------------------------------------
//
// function: checkPiConnection
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Sends connection to the backend to check if the Raspberry PI is connected.
//  Updates global connection status and user interface accordingly
//
//------------------------------------------------------------------------------

async function checkPiConnection() {
    try {
        const response = await fetch('/api/pi-status');
        const result = await response.json();
        
        if (result.status === 'connected') {
            piConnected = true;
            // Check if it's standalone mode (has engine_connected field)
            if (result.engine_connected !== undefined) {
                updateConnectionStatus('Standalone mode - Chess engine ready', 'connected');
            } else {
                updateConnectionStatus('Connected to Raspberry Pi', 'connected');
            }
        } else {
            piConnected = false;
            updateConnectionStatus('Disconnected from Raspberry Pi', 'disconnected');
        }
    } catch (error) {
        piConnected = false;
        updateConnectionStatus('Cannot connect to Raspberry Pi', 'disconnected');
    }
}

//------------------------------------------------------------------------------
//
// function: startConnectionMonitoring
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Continuosly monitors the Raspberry PI connection every 10 seconds
//  by repeading 'checkPiConnection' function
//
//------------------------------------------------------------------------------

function startConnectionMonitoring() {
    // Check connection every 10 seconds
    connectionCheckInterval = setInterval(checkPiConnection, 10000);
}

//------------------------------------------------------------------------------
//
// function: updateConnectionStatus
//
// arguments:
//  message: string representing the connection status message
//  status: string either "connected" or "disconnected"
//
// returns:
//  nothing
//
// description:
//  Updates the UI element showing the current state of the PI
//  including visual indicator and visual message
//
//------------------------------------------------------------------------------

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

//------------------------------------------------------------------------------
//
// function: resetSelection
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
//  Clears any currently selected chess piece and updates the status message
//  depending on the connection state to the raspberry PI
//
//------------------------------------------------------------------------------

function resetSelection() {
    if (selectedPiece) {
        selectedPiece.element.classList.remove('selected');
        selectedPiece = null;
    }
    
    if (piConnected) {
        document.getElementById('click-status').textContent = 'Click on a square to test interaction';
    } else {
        document.getElementById('click-status').textContent = '🔴 Not connected - Please wait...';
    }
}

//------------------------------------------------------------------------------
//
// function: overlay-user-vs-cpu
//
// arguments:
//  none
//
// returns:
//  nothing
//
// description:
// The overelay pick before the game starts
//------------------------------------------------------------------------------

// document.getElementById("overlay-user-vs-cpu").addEventListener("click", () => {
//     document.getElementById("mode-overlay").style.display = "none";

//     // Auto-select mode
//     document.getElementById("game-mode").value = "user_vs_cpu";

//     // Trigger existing button logic
//     document.getElementById("set-game-mode-btn").click();
// });

// document.getElementById("overlay-cpu-vs-cpu").addEventListener("click", () => {
//     document.getElementById("mode-overlay").style.display = "none";

//     // Auto-select mode
//     document.getElementById("game-mode").value = "cpu_vs_cpu";

//     // Trigger existing button logic
//     document.getElementById("set-game-mode-btn").click();

//     // Auto-start CPU vs CPU if needed
//     const startBtn = document.getElementById("start-cpu-cpu-btn");
//     if (startBtn) startBtn.click();
// });

//
// End of file
