import random
from game_definitions.win_conditions import PieceIsPlacedAt, EnemyPieceTypeRemoved, EnemyTotalPiecesLeft, Or, And

class WinConditionGenerator:
    def __init__(self, board, symmetric, n_pieceTypes):
        self.board = board
        self.x = board.width
        self.y = board.height
        self.symmetric = symmetric
        self.n_pieceTypes = n_pieceTypes

    def generateCondition(self):
        n = random.randint(1,2)
        if n == 2:
            operator = random.choice([Or, And])
            conditions = random.sample([self.piecePlacedAt, self.piecePlacedAt, self.pieceTypeRemoved, self.totalPiecesLeft], 2)
            return operator(conditions[0](), conditions[1]())
        return self.generateSimpleCondition()

    def generateSimpleCondition(self):
        return random.choice([self.piecePlacedAt, self.pieceTypeRemoved, self.totalPiecesLeft])()

    def piecePlacedAt(self):
        targetSquares = self.generateRandomArea(symmetric=self.symmetric)
        return PieceIsPlacedAt(targetSquares)

    def pieceTypeRemoved(self):
        return EnemyPieceTypeRemoved(random.randint(1, self.n_pieceTypes))

    def totalPiecesLeft(self):
        return EnemyTotalPiecesLeft(random.randint(1, (len(self.board.matrix)+1)//4))
       
    def generateRandomArea(self, symmetric=False):
        if symmetric:
            x, y = (self.x // 2) + (self.x % 2), (self.y // 2) - ((self.y + 1) % 2)
        else:
            x, y = self.x, (self.y // 2) - ((self.y + 1) % 2)
        a,b = random.randint(1,x), random.randint(1,y)
        off_x, off_y = random.randint(0, self.x - a), random.randint(self.y - y, self.y - b)
        area = { (off_x + a_, off_y + b_) for a_ in range(a) for b_ in range(b) }
        if symmetric:
            mirroredArea = {(self.x-a-1, b) for (a,b) in area}
            area |= mirroredArea
        return area
        