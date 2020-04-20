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
    
    def __init__(self, width, height, placements):
        self.width = width
        self.height = height
        self.matrix = {}
        for player, placement in placements:
            for (x,y), pawn_id in placement.items():
                self.place(Vector(x,y), pawn_id, player)

    def __copy__(self):
        board = Board(self.width,self.height, [])
        board.matrix = copy.copy(self.matrix)
        return board

    #def __deepcopy__(self,memo):
    #    return Board(0,0, matrix=copy.deepcopy(self.matrix, memo))

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
        del self.matrix[origin]

    def iterate(self):
        for position, square in  self.matrix.items():
            yield position, square
    
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
        square.board = self
        return square

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

    def isAlly(self, other):
        return self.owner == other.owner

    def isEnemy(self, other):
        return ~self.owner == other.owner

    def isEmpty(self):
        return self.piece == None

    def __repr__(self):
        return "Square[" + str(self.piece) + ", " + str(self.owner) + "]"

Square.EMPTY = Square(None, None, None, None)