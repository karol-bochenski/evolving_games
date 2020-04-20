from game_elements.player import Player

class And:
    def __init__(self, conditionA, conditionB, player=Player.P1):
        self.conditionA = conditionA
        self.conditionB = conditionB
        self.player = player

    def check(self, board):
        return self.conditionA.check(board) and self.conditionB.check(board)
    
    def invert(self, board):
        return And(self.conditionA.invert(board), self.conditionB.invert(board), ~self.player)

    def heuristicValue(self, game_state):
        return (self.conditionA.heuristicValue(game_state) + self.conditionB.heuristicValue()) / 2
    
    def toDict(self):
        return { "and": [self.conditionA.toDict(), self.conditionB.toDict()] }

class Or:
    def __init__(self, conditionA, conditionB, player=Player.P1):
        self.conditionA = conditionA
        self.conditionB = conditionB
        self.player = player

    def check(self, board):
        return self.conditionA.check(board) or self.conditionB.check(board)
    
    def invert(self, board):
        return Or(self.conditionA.invert(board), self.conditionB.invert(board), ~self.player)

    def heuristicValue(self, game_state):
        return (self.conditionA.heuristicValue(game_state) + self.conditionB.heuristicValue(game_state)) / 2
    
    def toDict(self):
        return { "or": [self.conditionA.toDict(), self.conditionB.toDict()] }

class PieceIsPlacedAt:
    def __init__(self, target_squares, player=Player.P1):
        self.target_squares = target_squares
        self.player = player

    def check(self, board):
        for square in self.target_squares:
            if(board[square].owner == self.player):
                return True
        return False
    
    def invert(self, board):
        inverted_squares = [(a, board.height-b-1) for (a,b) in self.target_squares]
        placedAt = PieceIsPlacedAt(inverted_squares, ~self.player)
        return placedAt
    
    def heuristicValue(self, game_state):
        p1Pieces = game_state.getPiecesForPlayer(self.player)
        for piecePosition, pieceId in p1Pieces:
            minDistance = 999999
            for targetSquare in self.target_squares:
                x,y = targetSquare - piecePosition
                distance = abs(x) + abs(y)
                if(distance < minDistance):
                    minDistance = distance
            game_state.getHeuristicValueOfPiece()

    def toDict(self):
        rows_map = {}
        for x,y in self.target_squares:
            if y in rows_map:
                rows_map[y]+= "," + str(x)
            else:
                rows_map[y] = str(x)
        return {
            "piecePlacedAt": rows_map
        }

class EnemyPieceTypeRemoved:
    def __init__(self, pieceId, player=Player.P1):
        self.pieceId = pieceId
        self.player = player

    def check(self, board):
        for _,square in board.matrix.items():
            if square.owner != ~self.player:
                continue
            if square.piece == self.pieceId:
                return False
        return True

    def invert(self, board):
        return EnemyPieceTypeRemoved(self.pieceId, ~self.player)

    def toDict(self):
        return {
            "EnemyPieceTypeRemoved": self.pieceId
        }

class EnemyTotalPiecesLeft:
    def __init__(self, totalLeft, player=Player.P1):
        self.totalLeft = totalLeft
        self.player = player

    def check(self, board):
        total = 0
        for _,square in board.matrix.items():
            if square.owner == ~self.player:
                total += 1
        return total <= self.totalLeft

    def invert(self, board):
        return EnemyTotalPiecesLeft(self.totalLeft,~self.player)

    def toDict(self):
        return {
            "EnemyTotalPiecesLeft": self.totalLeft
        }

def fromDict(conditionDict):
    key = list(conditionDict.keys())[0]
    value = conditionDict[key]
    if key == "and":
        return And(fromDict(value[0]), fromDict(value[1]))
    if key == "or":
        return Or(fromDict(value[0]), fromDict(value[1]))
    if key == "EnemyPieceTypeRemoved":
        return EnemyPieceTypeRemoved(int(value))
    if key == "EnemyTotalPiecesLeft":
        return EnemyTotalPiecesLeft(int(value))
    target_squares = []
    for rowNr, row in value.items():
        for ch in row.split(","):
            target_squares.append((int(rowNr), int(ch)))
    return PieceIsPlacedAt(target_squares)

winConditionFromDict = fromDict