from game_elements.board import Board
from game_definitions import moves

class Piece:
    def __init__(self, id, moveset):
        self.id = id
        self.moveset = moveset

    def inverted(self, axis):
        inverted_moveset = []
        for move in self.moveset:
            inverted_moveset.append(move.inverted(axis))
        return Piece(self.id, inverted_moveset)
    
    def toDict(self):
        moveDict = []
        duplicates = set()
        for move in self.moveset:
            if move.direction in duplicates or move.direction.inverted() in duplicates:
                continue
            duplicates.add(move.direction)
            moveDict.append(move.toDict())
        return {
            str(self.id) : {
                "moves": moveDict
                }
            }

    @staticmethod
    def fromDict(pieceDict):
        moveList = []
        for moveDict in pieceDict[list(pieceDict.keys())[0]]['moves']:
            move = moves.fromDict(moveDict)
            moveList.append(move)
            if move.direction[0] != 0:
                moveList.append(move.inverted(0))
        return Piece(3,moveList)

    def getLegalMoves(self, game_state, origin):
        return [validMove for moves in self.moveset for validMove in moves.validMoves(game_state, origin)]

    def heuristicValue(self, game_state, origin):
        staticValue = sum(move.heuristicValue() for move in self.moveset)
        currentValue = len(self.getLegalMoves(game_state, origin))
        return staticValue + currentValue