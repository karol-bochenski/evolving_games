import random
from game_definitions.vector import Vector
from game_definitions.moves import Hop,Leap,Slide
from game_definitions.move_conditions import SimpleMoveConditionGenerator

class HopGenerator:
    possibleFields = {(x - 3,y - 3) for x in range(7) for y in range(7) if (((x-3)*(x-3)) + ((y-3)*(y-3))) < 10}

    @staticmethod
    def generateMove():
        conditions = generateCondition() # TODO generate conditions method
        distance = random.randint(1,3)
        x = random.randint(0,distance)
        y = distance - x
        x,y = x,  random.choice([-1,1]) * y
        can_attack = random.choice([True, False])

        return Hop(Vector(x,y), can_attack, conditions), {(x,y)}

class LeapGenerator:
    @staticmethod
    def generateMove():
        condition = generateCondition() # TODO generate conditions method
        x,y = random.choice([(0,1),(1,0),(1,1)])
        x,y = x,  random.choice([-1,1]) * y
        return Leap(Vector(x,y), condition=condition), {(x*2, y*2)}

class SlideGenerator:
    @staticmethod
    def generateMove():
        condition = generateCondition() # TODO generate conditions method
        x,y = random.choice([(0,1),(1,0),(1,1)])
        x,y = x,  random.choice([-1,1]) * y
        return Slide(Vector(x,y), condition=condition), {(x*n,y*n) for n in range(1,10)}
        
def generateCondition():
    if random.random() < 0.1:
        return SimpleMoveConditionGenerator().generateCondition()
    return None

def generateMoveSet():
    moves = []
    takenDestinations = set()
    for _ in range(random.randint(1, 5)):
        generator = random.choices([HopGenerator, LeapGenerator, SlideGenerator], weights=[0.58, 0.28, 0.28])[0]
        move,destinations = generator.generateMove()
        if (takenDestinations.intersection(destinations)):
            continue
        moves.append(move)
        takenDestinations |= destinations
        if(move.direction.x != 0):
          moves.append(move.inverted(axis=0))
    return moves