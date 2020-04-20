from enum import Enum,auto
from game_definitions.bcolors import bcolors

class Player(Enum):
    P1 = auto()
    P2 = auto()

    def __invert__(self):
        if (self == Player.P1):
            return Player.P2
        return Player.P1

    def color(self):
        if self == Player.P1:
            return (0,100,0)
        return (100,0,0)

    def __repr__(self):
        if self == Player.P1:
            return bcolors.OKGREEN + "1" + bcolors.ENDC
        return bcolors.FAIL + "2" + bcolors.ENDC

    def __str__(self):
        return self.__repr__()