import numpy as np
from src.base.SrcIndex import Coord, PawnType
from src.core.Action import Action
import copy

class Status:
    def __init__(self,arg_w:int=0,arg_h:int=0):
        if arg_w>0 or arg_h>0:
            self.status:np.ndarray = np.zeros((arg_w, arg_h), dtype=np.int8)
        else:
            self.status: np.ndarray = np.array([])

    def __copy__(self):
        new = self.__class__()
        new.status = self.status.copy()
        return new

    def __deepcopy__(self,memo):
        new = self.__class__()
        new.status = copy.deepcopy(self.status)

    def action_if(self,arg_action:Action) -> "Status":
        new_status = copy.copy(self)
        new_status.action(arg_action)
        return new_status

    def action(self,arg_action:Action) -> "Status":
        self.status[arg_action.coord.x][arg_action.coord.y] = arg_action.pawn_type.value
        return self

    def pawn(self,arg_coord:Coord) -> PawnType:
        return PawnType(self.status[arg_coord.x][arg_coord.y])

    def positions(self,arg_pawn_type:PawnType) -> list[Coord]:
        idx = np.where(arg_pawn_type == self.status)
        return [Coord(x,y) for x,y in zip(idx[0],idx[1])]
