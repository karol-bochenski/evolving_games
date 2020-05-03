import copy
from game_definitions.vector import Vector

class Board:
    """Class representing board state at any time during the game

    Attributes
    ----------
    x : int
        number of columns in the board
    y : int
        number of rows in the board
    matrix : Dict (2d vector => pieceId)
        dictionary that holds information about location of all game pieces currently on the board
    """
    
    def __init__(self, width, height, placement={}, player2Mirrored=False):
        self.width = width
        self.height = height
        self.matrix = {}
        for (x,y), pawn_id in placement.items():
            self.place(Vector(x,y), pawn_id, Player.P1)
            player2x = self.width - x - 1 if player2Mirrored else x
            self.place(Vector(player2x, self.height - y - 1), pawn_id, Player.P2)

    def __copy__(self):
        board = Board(self.width,self.height)
        board.game = self.game
        board.matrix = copy.copy(self.matrix)
        return board

    def __deepcopy__(self,memo):
        board = Board(self.width, self.height)
        board.game = self.game
        for position, square in self.matrix.items():
            board.place(position, square.piece, square.owner)
        return board

    def __hash__(self):
        return (self.width, self.height, frozenset(self.matrix.items())).__hash__()

    def __eq__(self, other):
        return self.width == other.width and self.height == other.height and self.matrix == other.matrix

    def place(self, position, pieceType, owner):
        self.matrix[position] = Square(pieceType, owner, position, self)

    def remove(self, position):
        if position in self.matrix:
            del self.matrix[position]
    
    def movePiece(self, origin, move_to):
        self.matrix[move_to] = self.matrix[origin]
        self.matrix[move_to].coords = move_to
        del self.matrix[origin]

    def iterate(self):
        for _, square in  self.matrix.items():
            yield square
    
    def contains(self, point):
        if(point[0] < 0 or point[0] >= self.width):
            return False
        if(point[1] < 0 or point[1] >= self.height):
            return False
        return True

    def __setitem__(self, key, value):
        self.matrix[key] = value
    
    def __getitem__(self, key):
        square = self.matrix.get(key)
        if not square:
            return Square(None, None, key, self)
        return square

from game_elements.player import Player

class Square:
    """Definition of a single square on the board

    Single square contains information about what piece is currently on it's place and which player's is its owner
    The square is considered to be empty when value of 'piece' attribute is None
 
    Attributes
    ----------
    piece : int
        Identifying number of a piece that is placed on the square, see 'pieceTypes' attribute of 'boardGame' class
    owner : Player
        Owner (player 1 or player 2) of piece placed on this square
    """

    def __init__(self, piece, owner, coords, board):
        self.piece = piece
        self.owner = owner
        self.coords = coords
        self.board = board
        self.legalMoves = None

    def getLegalMoves(self):
        if self.legalMoves:
            return self.legalMoves
        moveset = self.board.game.piece_types[self.owner][self.piece].moveset
        allValidMoves = []
        for move in moveset:
            validMoves = move.validMoves(self.board, self.coords)
            allValidMoves += validMoves
        self.legalMoves = allValidMoves
        return allValidMoves

    def isAlly(self, other):
        return self.owner == other.owner

    def isEnemy(self, other):
        return ~self.owner == other.owner

    def isEmpty(self):
        return self.piece == None

    def __repr__(self):
        return "Square[" + str(self.piece) + ", " + str(self.owner) + "]"

Square.EMPTY = Square(None, None, None, None)

