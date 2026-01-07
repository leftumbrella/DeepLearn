from enum import Enum


class PawnType(Enum):
    TNone = 0
    TWhite = 1
    TBlack = 2

class Coord:
    def __init__(self, arg_x = 0, arg_y=0):
        self.x:int = arg_x
        self.y:int = arg_y

    def __eq__(self, other):
        return isinstance(other, Coord) and \
               self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))