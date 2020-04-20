# Evolving Board Games
 
 This project serves as a research part my bachelors thesis, in which i'm trying to use evolutionary algorithms to generate and evaluate playable and interesting board games.

## Searchable space
- dimension of table, rectangular
- types of pawns
  - possible moves
  - possible attack moves
- number of pawns
   - asymetrical
- initial placement of pawns
  - not scattered randomly
  - at most 4 distinct groups
- winning condition
  - asymetrical (i.e. only one team could have target squares that it has to reach, other team would win only by eliminating enemy pawns)
  - could specify a single target square that pawns have to reach
  - could specify multiple targets that pawns have to reach (maybe at the same time)
  - could specify squares that have to be reached my more than one pawn

## Game elements

- game definition:
  - initial placement of pieces
  - definition of types of pieces

- piece type:
  - holds its all possible move definitions

- move definition:
  - defines movement relative to its piece
  - defines conditions for the move (e.g. only to empty square or have to jump over an enemy)
  - defines target if move is attacking (e.g. remove enemy piece that have just been jumped over)

- ingame move:
  - combines definition of a move with current position of piece on the board, stating a next legal move in current game state
  - can be applied to a current game state to produce the next game state

- board:
  - rectangular (with x,y coordinates)
  - enumerable
  - keeps track all pieces and their owners

- game state:
  - current position of all pieces in the game
  - has all information needed to define all legal moves for the next turn

- win conditions:
  - defines condition that have to be met in a game state for a specific player to lose e.g:
    - win if a piece reaches the other side of the board
    - win if a specific enemy piece is removed from the board
    - win if 2 or more specified squares on the boards are taken by a player


 - More information, with usage and explanations can be found in this [jupyter notebook](demo.ipynb)
