# AI_Chess_Senior_Design
Created By Samuel Georgi, Shane Mullin, Dylan Boles & Zephan Joseph

Two Hardware Devices Able to play each other using AI
Able to handle a program that Has AI open source data to games.
Can speed up to 1000 games per second (sequentially) or slow down to watch each individual move. 
Go back moves and forward moves as well as reset to current state of the game. 
Launch from the laptop and codes will be downloaded to hardware to execute games. 
A Stop and Start for the games Hardware can use programing language that is widely used. 
Be able to control Program Complexity. Such as the amount of look aheads in the game. (5 look aheads, 10 look aheads, etc.)

## Design Proposal Requirments
- Screen/User Interface Look
- Description Hardware
- Programming Enviorment
- AI Training and AI Enviorment

## CSS Design
├── main.css          # Base styles, layout, typography
├── board.css         # Chess board specific styles
├── controls.css      # All control buttons and panels
└── moves.css         # Moves panel styles

## JavaScript Design
├── main.js           # Main initialization and global variables
├── board.js          # Chess board creation and piece management
├── game.js           # Game logic, move validation, game state
├── controls.js       # All control button functionality
├── navigation.js     # Move navigation and history
└── utils.js          # Utility functions and helpers

## Communications
Browser (JS GUI)
   ↓
Laptop Flask app (/api/move)
   ↓
Raspberry Pi Flask server (/api/move)
   ↓
Stockfish processes + updates board
   ↓
Pi sends updated board + status
   ↓
Laptop Flask app returns data to browser
   ↓
GUI updates pieces on screen

## When it is Engine Turn
Browser → /api/engine-move → Pi → Stockfish → Pi → Laptop → Browser
