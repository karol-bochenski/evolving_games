from game_elements.board import Board
from game_definitions import moves

class Piece:
    def __init__(self, id, moveset):
        self.id = id
        self.moveset = moveset
        self.calculateMobilityValue()
        
    def inverted(self, axis):
        inverted_moveset = []
        for move in self.moveset:
            inverted_moveset.append(move.inverted(axis))
        invertedPiece = Piece(self.id, inverted_moveset)
        invertedPiece.mobility_value = self.mobility_value
        return invertedPiece
    
    def toDict(self):
        moveDict = []
        duplicates = set()
        for move in self.moveset:
            if (type(move),move.direction) in duplicates or (type(move),move.direction.inverted()) in duplicates:
                continue
            duplicates.add((type(move), move.direction))
            moveDict.append(move.toDict())
        return {
            str(self.id) : {
                "moves": moveDict
                }
            }

    @staticmethod
    def fromDict(pieceDict):
        moveList = []
        pieceId = list(pieceDict.keys())[0]
        for moveDict in pieceDict[pieceId]['moves']:
            move = moves.fromDict(moveDict)
            moveList.append(move)
            if move.direction[0] != 0:
                moveList.append(move.inverted(0))
        return Piece(pieceId,moveList)

    def calculateMobilityValue(self):
        value = 1
        for move in self.moveset:
            value += move.heuristicValue()
        self.mobility_value = value