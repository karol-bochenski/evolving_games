class At:
    def __init__(self, direction):
        self.direction = direction

    def inverted(self, axis):
        return At(self.direction.inverted(axis))

    def get(self, board, position):
        return position + self.direction

    def toString(self):
        return "at " + self.direction.asDirection()

class Facing:
    def __init__(self, direction):
        self.direction = direction

    def inverted(self, axis):
        return Facing(self.direction.inverted(axis))

    def toString(self):
        return "facing " + self.direction.asDirection()

    def get(self, board, position):
        current_position = position + self.direction
        while board.contains(current_position):
            current_square = board[current_position]
            if not current_square.isEmpty():
                return current_position
            current_position += self.direction
        return board[current_position]

class Enemy:
    def check(self, origin, destination):
        return origin.isEnemy(destination)

    def toString(self):
        return "enemy"

class Ally:
    def check(self, origin, destination):
        return origin.isAlly(destination)
    
    def toString(self):
        return "ally"

class Empty:
    def check(self, origin, destination):
        return destination.isEmpty()

    def toString(self):
        return "empty"

class Not:
    def __init__(self, condition):
        self.condition = condition

    def inverted(self, axis=0):
        return Not(self.condition.inverted(axis))

    def check(self, origin, destination):
        return not self.condition.check(origin, destination)

    def toString(self):
        return "not " + self.condition.toString()

class MoveCondition:
    def __init__(self, selector, checker, targetsDestination):
        self.selector = selector
        self.checker = checker
        self.targetsDestination = targetsDestination
        self.getTarget = self.targetDestination if targetsDestination else self.targetOrigin

    def inverted(self, axis=0):
        selector = self.selector.inverted(axis)
        condition = MoveCondition(selector, self.checker, self.targetsDestination)
        return condition

    def check(self, board, move):
        target = self.selector.get(board, self.getTarget(move))
        return self.checker.check(board[move.origin], board[target])

    def targetOrigin(self, move):
        return move.origin

    def targetDestination(self, move):
        return move.destination

    def toString(self):
        return ("destination " if self.targetsDestination else "origin ") + self.selector.toString() + " " + self.checker.toString()

import random
from game_definitions.vector import Vector

class SimpleMoveConditionGenerator:
    def generateCondition(self):
        checker, direction, selector, target = self.getParams()
        while not self.validCondition(checker, direction, selector, target):
            checker, direction, selector, target = self.getParams()
        condition = MoveCondition(selector(direction), checker(), target)
        if random.random() > 0.8:
            return Not(condition)
        return condition

    def getParams(self):
        checker = random.choice([Ally, Enemy, Empty])
        direction = random.choice([Vector(a-1,b-1) for a in range(3)for b in range(3)])
        selector = random.choice([At, Facing])
        target = random.choice([True, False])
        return checker, direction, selector, target
 
    def validCondition(self, checker, direction, selector, targetsDestination):
        if selector == Facing and direction == Vector(0,0): #no direction to be facing at
            return False
        if targetsDestination and checker == Ally: #move ending on a square taken by a piece of the same player is invalid
            return False
        if not targetsDestination and direction == Vector(0,0): #origin at (0,0) will always be ally (itself)
            return False
        return True

def conditionFromString(conditionString):
    negative = conditionString.startswith("not")
    if negative:
        conditionString = conditionString[4:]
    strTarget, strSelector, strDirection, strChecker = conditionString.split(" ")
    target = targetFromString(strTarget)
    selector = selectorFromString(strSelector)
    direction = directionFromString(strDirection)
    checker = checkerFromString(strChecker)
    condition = MoveCondition(selector(direction), checker(), target)
    if negative:
        condition = Not(condition)
    return condition

def targetFromString(string):
    if string == 'destination':
        return True
    return False

def selectorFromString(string):
    if string == 'facing':
        return Facing
    return At

def directionFromString(string):
    return Vector.fromDirection(string)

def checkerFromString(string):
    if string == 'enemy':
        return Enemy
    if string == 'ally':
        return Ally
    return Empty

def fromDict(conditionDict):
    return None #TODO