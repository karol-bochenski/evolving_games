from typing import List, Set
from game_elements.board import Board
from game_definitions import move_conditions 
from .vector import Vector

class Move:
    def __init__(self, origin, destination, apply_func):
        self.origin = origin
        self.destination = destination
        self.apply_func = apply_func

    def apply(self, state):
        self.apply_func(self.origin, self.destination, state.board)
        state.nextRound()

class Hop:
    def __init__(self, destination, can_attack=False, condition=None):
        self.direction = destination
        self.can_attack = can_attack
        self.condition = condition

    def inverted(self, axis=0):
        move_to = self.direction.inverted(axis)
        condition = None
        if self.condition:
            condition = self.condition.inverted(axis)
        return Hop(move_to, can_attack=self.can_attack, condition=condition)

    def apply(self):
        def f(origin, destination, board):
            board.movePiece(origin, destination)
        return f

    def validMoves(self, board, origin):
        destination = origin + self.direction
        if not board.contains(destination):
            return []
        orig_square = board[origin]
        dest_square = board[destination]
        if orig_square.owner == dest_square.owner: #Cannot move to a square occupied by friendly piece
            return []
        if not self.can_attack and ~orig_square.owner == dest_square.owner: #If move is not an attacking one then cannot move to enemy square
            return []
        move = Move(origin, destination, self.apply())
        if self.condition:
            conditionPassed = self.condition.check(board, move)
            if conditionPassed:
                return [move]
            return []
        return [move]

    def heuristicValue(self):
        return (0.5 / (1 if self.condition else 2)) + (0.5 if self.can_attack else 0)

    def toDict(self):
        dict_ = {"hop" : str(self.direction.asDirection())}
        if(self.condition):
            dict_["if"] = self.condition.toString()
        if(self.can_attack):
            dict_["canAttack"] = True
        return dict_

    @staticmethod
    def fromDict(hopDict):
        direction = Vector.fromDirection(hopDict["hop"])
        canAttack = hopDict["canAttack"] if "canAttack" in hopDict else False
        condition = move_conditions.fromDict(hopDict["if"]) if "if" in hopDict else None
        return Hop(direction, can_attack=canAttack, condition=condition)

class Slide:
    def __init__(self, direction, condition):
        self.direction = direction
        self.condition = condition

    def inverted(self,axis):
        direction = self.direction.inverted(axis) 
        condition = None
        if self.condition:
            condition = self.condition.inverted(axis)
        return Slide(direction, condition)

    def apply(self):
        def f(origin, destination, board):
            board.movePiece(origin, destination)
        return f

    def validMoves(self, board, origin):
        moves = []
        current_square = origin + self.direction
        while (board.contains(current_square) and board[current_square].owner is None):
            move = Move(origin, current_square, self.apply())
            if self.condition:
                result = self.condition.check(board.move)
                if result:
                    moves.append(move)
            else:
                moves.append(move)
            current_square = current_square + self.direction
        if(board[current_square].owner == ~board[origin].owner):
            move = Move(origin, current_square, self.apply())
            if self.condition:
                result = self.condition.check(board, move)
                if result:
                    moves.append(move)
            else:
                moves.append(move)
        return moves

    def heuristicValue(self):
        return ((2 + abs(self.direction[0]) + self.direction[1]) / (1 if self.condition else 2)) / (1 if self.condition else 2)

    def toDict(self):
        dict_ = {"slide" : str(self.direction.asDirection())}
        if(self.condition):
            dict_["if"] = self.condition.toString()
        return dict_

    @staticmethod
    def fromDict(slideDict):
        direction = Vector.fromDirection(slideDict["slide"])
        condition = move_conditions.fromDict(slideDict["if"]) if "if" in slideDict else None
        return Slide(direction, condition=condition)

class Leap:
    def __init__(self, direction, condition=None):
        self.direction = direction
        self.condition = condition
        
    def inverted(self, axis=0):
        direction = self.direction.inverted(axis)
        condition = None
        if self.condition:
            condition = self.condition.inverted(axis)
        return Leap(direction, condition)

    def apply(self):
        def f(origin, destination, board):
            leapedOver = origin + self.direction
            if(~board[origin].owner == board[leapedOver].owner):
                board.remove(leapedOver)
            board.movePiece(origin, destination)
        return f

    def validMoves(self, board, origin):
        current_square = origin + (self.direction * 2)
        if(board.contains(current_square) and board[current_square].owner is None):
            move = Move(origin, current_square, self.apply())
            if self.condition:
                result = self.condition.check(board, move)
                if result:
                    return [move]
                return []
            return [move]
        return []

    def heuristicValue(self):
        return (1 + self.direction[1] + 0.5 * (self.direction[0])) / (2 if self.condition else 1)

    def toDict(self):
        dict_ = {"leap" : str(self.direction.asDirection())}
        if(self.condition):
            dict_["if"] = self.condition.toString()
        return dict_

    @staticmethod
    def fromDict(leapDict):
        direction = Vector.fromDirection(leapDict["leap"])
        condition = move_conditions.fromDict(leapDict["if"]) if "if" in leapDict else None
        return Leap(direction, condition=condition)

class EnemyAt:
    def __init__(self, vector):
        self.vector = vector

    def inverted(self, axis=0):
        return EnemyAt(self.vector.inverted(axis))

    def passes(self, position, board):
        return ~board[position].owner == board[position + self.vector].owner

class AllyAt:
    def __init__(self, vector):
        self.vector = vector

    def inverted(self, axis=0):
        return AllyAt(self.vector.inverted(axis))

    def passes(self, position, board):
        return board[position].owner == board[position + self.vector].owner

class YMoreThan:
    def __init__(self, y, inverted = False):
        self.y = y
        self.is_inverted = inverted

    def inverted(self, axis=0):
        return YMoreThan(self.y, inverted=not self.is_inverted)

    def passes(self, position, board):
        if(self.is_inverted):
            return position[1] < board.y - self.y - 1
        return position[1] > self.y

class YLessThan:
    def __init__(self, y, inverted = False):
        self.y = y
        self.is_inverted = inverted

    def inverted(self, axis=0):
        return YMoreThan(self.y, inverted=not self.is_inverted)

    def passes(self, position, board):
        if(self.is_inverted):
            return (board.y - self.y - 1) > self.y
        return position[1] < self.y


def fromDict(moveDict):
    fields = list(moveDict.keys())
    if "hop" in fields:
        return Hop.fromDict(moveDict)
    if "leap" in fields:
        return Leap.fromDict(moveDict)
    return Slide.fromDict(moveDict)