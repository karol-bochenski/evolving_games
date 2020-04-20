from game_definitions.boardGame import BoardGame
from game_elements.player import Player
from game_elements.board import Board
from game_elements.player import Player
from game_elements.piece import Piece
from game_definitions.vector import Vector
import random
import time
import utils
from generators import moveGenerator, boardGenerator
from generators.winConditionGenerator import WinConditionGenerator
from mcts import mcts
import yaml

def mcts_playout(game):
    game_state = game.initialState()
    while(not game_state.finished):
        if(game_state.currentPlayer == Player.P1):
            move = random.choice(game_state.possibleMoves)
            game_state = game_state.applyMove(move)
        else:
            game_state = mcts.findNextMove(game_state).game_state
    return game_state

def randomBoardSize(n_pieces):
    X, Y = 0,0
    while (X * Y) < (n_pieces * 2):
        X,Y = random.randint(3,10),random.randint(5,10)
    return X,Y

def generatePieces(n_pieces):
    return [None] + [Piece(i+1, moveGenerator.generateMoveSet()) for i in range(n_pieces)]

def _generateGame():
    n_pieces = random.randint(1,6)
    width, height = randomBoardSize(n_pieces)
    symmetric = random.choice([True, False])
    board, player2mirrored = boardGenerator.BoardGenerator(width, height, n_pieces).generateBoard(symmetric=symmetric)
    pieces = generatePieces(n_pieces)
    winConditions = WinConditionGenerator(board, symmetric, n_pieces).generateCondition()
    return BoardGame(board, player2mirrored, pieces, winConditions)

def generateGame():
    game = None
    while not game:
        try:
            game = _generateGame()
        except BaseException:
            continue
    return game

def controlledPlayout(game):
    game_state = game.initialState()
    turnCount = 0
    moveablePieces = set()
    while(not game_state.finished):
        moves = game_state.possibleMoves
        for move in moves:
            moveablePiece = game_state.board[move.origin].piece
            moveablePieces.add(moveablePiece)
        move = random.choice(game_state.possibleMoves)
        game_state = game_state.applyMove(move)
        turnCount += 1
    return game_state, turnCount, moveablePieces

def testGame(game):
    wasWinner = False
    unmovedPieces = {a for a in range(1, len(game.piece_types[Player.P1]))}
    for _ in range(50):
        game_state, turnCount, movedPieces = controlledPlayout(game)
        if turnCount < 10:
            return False
        if game_state.winner:
            wasWinner = True
        unmovedPieces = unmovedPieces - movedPieces
        if not unmovedPieces and wasWinner:
            return True
    return False

def generatePlayable(outputDir="generated/games",n = 1000):
    i = 0
    while i < n:
        game = generateGame()
        res = testGame(game)
        if(res):
            if(i % (n // 10) == 0 ):
                print(str((100 * i) / n) + "%")
            utils.toFile(game, outputDir + "/game_" + str(i) + ".yml")
            i += 1