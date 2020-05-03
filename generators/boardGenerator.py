import random
from game_elements.player import Player
from game_elements.board import Board

class BoardGenerator():
    def __init__(self, x,y, n_piece_types=1):
        self.x = x
        self.y = y
        self.n_piece_types = n_piece_types
        
    def generateBoard(self, symmetric=False):
        player1Pieces = self.generateInitialShape(symmetric)
        player1Pieces = self.ensureNoMajority(player1Pieces)
        player1Pieces = self.ensureAllPiecesUsed(player1Pieces)
        player2mirrored = random.choice([True, False])
        board = Board(self.x,self.y, player1Pieces, player2mirrored)
        return board, player2mirrored

    def mirrorBoard(self, points, x_axis=False, y_axis=False):
        ret = {}
        for (a,b),pid in points.items():
            a_ = (self.x-a-1) if y_axis else (a)
            b_ = (self.y-b-1) if x_axis else (b)
            ret[a_, b_] = pid
        return ret

    def generateInitialShape(self, symmetric=False):
        if symmetric:
            x, y = (self.x // 2) + (self.x % 2), (self.y // 2) - ((self.y + 1) % 2)
        else:
            x, y = self.x, (self.y // 2) - ((self.y + 1) % 2)
        n_pieces = random.randint(self.n_piece_types, x*y)
        chosenPoints = {}
        tries = 0
        while ((len(chosenPoints) != n_pieces)):
            tries += 1
            a,b = random.randint(1,x), random.randint(1,y)
            off_x, off_y = random.randint(0, x - a), random.randint(0, y - b)
            area = { (off_x + a_, off_y + b_) for a_ in range(a) for b_ in range(b) }
            piece_type = random.randint(1, self.n_piece_types)
            if len(chosenPoints) < n_pieces:
                for point in area:
                    chosenPoints[point] = piece_type
            else:
                for point in area:
                    if point in chosenPoints:
                        del chosenPoints[point]
        if symmetric:
            return {**chosenPoints, **self.mirrorBoard(chosenPoints, y_axis=True)}
        return chosenPoints

    def ensureAllPiecesUsed(self, pieces):
        missingPieces = { pieceId for pieceId in range(1, self.n_piece_types +1) } - set(pieces.values())
        tries = 0
        while (missingPieces and tries < 20):
            a,b = random.choice(list(pieces.keys()))
            pieces[a,b] = random.choice(list(missingPieces))
            pieces[self.x-a-1, b] = random.choice(list(missingPieces))
            missingPieces = { pieceId for pieceId in range(1, self.n_piece_types +1) } - set(pieces.values())
            tries += 1
        return pieces
    
    def ensureNoMajority(self, pieces):
        if(self.n_piece_types <= 2):
            return pieces
        mostPieces, pieceId = self.getMostPlacedPiece(pieces)
        tries = 0
        while (mostPieces > (len(pieces) * 0.50)) and tries < 20:
            a,b = random.choice([(a,b) for (a,b),pid in pieces.items() if pid==pieceId])
            pieces[(a,b)] = random.choice(list({pid for pid in range(1,self.n_piece_types+1)} - {pieceId}))
            pieces[(self.x - a -1, b)] = pieces[(a,b)]
            mostPieces, pieceId = self.getMostPlacedPiece(pieces)
            tries += 1
        return pieces
            
    def getMostPlacedPiece(self, pieces):
        counted = [0 for _ in range(self.n_piece_types + 1)]
        for pid in pieces.values():
            counted[pid] += 1
        mostPieces = max(counted)
        return mostPieces, counted.index(mostPieces)
        