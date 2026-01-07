import warnings

from src.base.SrcIndex import Coord
from src.core.Action import Action
from src.core.Agent import Agent

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API"
)
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
from src.tools.Game import Game


if __name__ == "__main__":
    main_game = Game(arg_w=10,arg_h=10)
    main_agent = Agent()
    while True:
        main_game.run()
        agent_action,win_guess = main_agent.next_action(main_game.look_status())
        main_game.place(agent_action.coord.x,agent_action.coord.y,agent_action.pawn_type)