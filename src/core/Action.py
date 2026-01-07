from src.base.SrcIndex import *
class Action:
    def __init__(self ,arg_pawn_type:PawnType=PawnType.TNone,arg_coord:Coord=Coord(0,0)):
        self.pawn_type:PawnType = arg_pawn_type
        self.coord:Coord = arg_coord