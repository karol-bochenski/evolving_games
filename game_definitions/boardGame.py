from game_definitions.win_conditions import winConditionFromDict
from game_elements.player import Player
from game_elements.piece import Piece
from game_elements.board import Board
from .moves import Move
from .vector import Vector
from copy import copy, deepcopy
import random

class BoardGame():
    """Class containing all information about a playable board game

    Attributes
    ----------
    initialBoard : Board
        Object of type Board containing initial placement of all game pieces. State of the first turn of a game will start with this placement.
    piece_types : List[Piece]
        Ordered definition of all possible types of pieces in a game. During the game all pieces are defined by a number that represents index of this list. 
    winConditions : List[Condition]
        List of all conditions that define when a player achieves victory

    """

    def __init__(self, board, player2mirrored, listOfPieces, winConditions):
        self.initialBoard = board
        self.isPlayer2mirrored = player2mirrored
        self.piece_types   = { Player.P1:listOfPieces,  Player.P2:self.invertPieces(listOfPieces) }
        self.winConditions = { Player.P1:winConditions, Player.P2:self.invertConditions(winConditions) }

    def __copy__(self):
        return BoardGame(self.initialBoard, self.isPlayer2mirrored, self.piece_types[Player.P1], self.winConditions)

    def __deepcopy__(self, memo):
        return BoardGame(deepcopy(self.initialBoard, memo), self.isPlayer2mirrored, deepcopy(self.piece_types[Player.P1], memo), deepcopy(self.winConditions, memo))
    
    def invertPieces(self, listOfPieces):
        pieces = []
        for piece in listOfPieces[1:]:
            pieces.append(piece.inverted(axis=1))
        return [None] + pieces
    
    def invertConditions(self, winConditions):
        return winConditions.invert(self.initialBoard)
        
    def initialState(self):
        return GameState(self, self.initialBoard)

    def toDict(self):
        rows = [["0" for _ in range(self.initialBoard.width)] for _ in range((self.initialBoard.height // 2) + 1)]
        highestRow = 0
        for (x,y), square in self.initialBoard.matrix.items():
            if (y >= self.initialBoard.height // 2 + 1):
                continue
            rows[y][x] = square.piece
            if y > highestRow:
                highestRow = y
        formattedRows = []
        for i in range(highestRow+1):
            formattedRows.append("".join([str(x) for x in rows[i]]))
        formattedRows = " ".join(formattedRows)
        return {
            "dimensions" : str(self.initialBoard.width) + "x" + str(self.initialBoard.height),
            "placement" : formattedRows,
            "player2mirrored" : self.isPlayer2mirrored,
            "pieces" : [piece.toDict() for piece in self.piece_types[Player.P1][1:]],
            "winConditions": self.winConditions[Player.P1].toDict()
        }

    @staticmethod
    def fromDict(gameDefinitionDict):
        width, height = [int(dim) for dim in gameDefinitionDict["dimensions"].split("x")]
        player2mirrored = gameDefinitionDict["player2mirrored"]
        pieceTypes = [None] + [ Piece.fromDict(pieceDefinitionDict) for pieceDefinitionDict in gameDefinitionDict["pieces"] ]
        player1placements = { (a,b):int(id) for b,row in enumerate(gameDefinitionDict["placement"].split(" ")) for a,id in enumerate(row) if id != '0'}
        player2placements = { (width-a-1 if player2mirrored else a,height - b - 1):int(id) for (a,b),id in player1placements.items() }
        board = Board(width, height, [(Player.P1, player1placements), (Player.P2, player2placements)])
        winCondition = winConditionFromDict(gameDefinitionDict["winConditions"])
        return BoardGame(board,player2mirrored, pieceTypes, winCondition)

class GameState():
    """Class defining possible state of the board during a game

    Attributes
    ----------
    game : BoardGame
        reference to the parent's game definition, used for determining possible moves based on current state for current turn, or whether the current game state is terminal
    board : Board
        placement of pieces at the start of the current turn
    currentPlayer : Player
        player that has control of current turn

    """
    def __init__(self, game, board, player = Player.P1, round_count=0):
        self.game = game
        self.board = copy(board)
        self.currentPlayer = player
        self.round_count = round_count
        self._possibleStates = None
        self._possibleMoves = None

    def __hash__(self):
        return (self.board, self.currentPlayer).__hash__()

    def __eq__(self, other):
        return self.board == other.board and self.currentPlayer == other.currentPlayer

    def copy(self):
        return GameState(self.game, self.board, player=self.currentPlayer, round_count=self.round_count)

    @property
    def possibleStates(self):
        if self._possibleStates is None:
            if(not self.winner is None):
                return []
            states = []
            for move in self.possibleMoves:
                states.append(self.applyMove(move))
            self._possibleStates = states
        return self._possibleStates

    @property
    def possibleMoves(self):
        if self._possibleMoves is None:
            possibleMoves = [] 
            for position, piece in self.getCurrentPlayersPieces():
                for move in piece.getLegalMoves(self, position):
                    possibleMoves.append(move)
            self._possibleMoves = possibleMoves
        return self._possibleMoves
    
    @property
    def finished(self):
        if self.round_count > 500:
            return True
        if(self.winner != None):
            return True
        if(len(self.possibleMoves) == 0):
            return True
        return False
    
    @property
    def winner(self):
        if len(self.getPiecesForPlayer(self.currentPlayer)) == 0:
            return ~self.currentPlayer
        winCondition = self.game.winConditions[~self.currentPlayer]
        if winCondition.check(self.board):
            return ~self.currentPlayer
        return None
        
    def getCurrentPlayersPieces(self):
        return self.getPiecesForPlayer(self.currentPlayer)

    def getPiecesForPlayer(self, player):
        pieces = []
        for position, square in self.board.iterate():
            if square.owner == player:
                piece = self.game.piece_types[player][square.piece]
                pieces.append((position,piece))
        return pieces

    def applyMove(self, moveInfo):
        """Function that applies specified move to the current game state and returns new game state, thread-safe but slow"""
        state = self.applyMove_(moveInfo)
        return state

    def applyMove_(self, moveInfo):
        """Function that applies specified move to the current game state and returns new game state, thread-safe but slow"""
        state = moveInfo.apply()
        return state

    def nextRound(self):
        self.currentPlayer = ~self.currentPlayer
        self.round_count += 1
        return self

    def simulateRandomPlayout(self):
        game_state = self.copy()
        states = {game_state}
        while not game_state.finished:
            #game_state._possibleMoves = None
            moves = game_state.possibleMoves
            moveInfo = random.choice(moves)
            game_state = game_state.applyMove(moveInfo)
            states |= {game_state}
        return game_state.winner

    def getHeuristicValue(self):
        values = [0,0]
        for position, piece in self.getPiecesForPlayer(Player.P1):
            values[0] += piece.heuristicValue(self.board, position)
        for position, piece in self.getPiecesForPlayer(Player.P2):
            values[1] += piece.heuristicValue(self.board, position)
        return values
    
    def printState(self):
        print("Player: ", end="")
        print(self.currentPlayer)
        print("\\", end="")
        for i in range(self.board.width):
            print(" " + str(i), end="")
        print("")
        for j in range(self.board.height):
            print(str(j) + "|",end='')
            for i in range(self.board.width):
                square = self.board[Vector(i,j)]
                if square.owner is None:
                    print(" :",end='')
                else:
                    print(str(square.owner) + ':',end='')
            print("|")
