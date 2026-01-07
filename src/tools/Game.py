import pygame

from src.core.Action import Action
from src.core.Status import Status
from src.base.SrcIndex import PawnType, Coord


class Game:
    def __init__(self,arg_user_turn:PawnType=PawnType.TBlack, arg_w=20,arg_h=20, cell=30, margin=40):
        pygame.init()
        self.w = arg_w
        self.h = arg_h
        self.cell = cell
        self.margin = margin
        w = margin * 2 + cell * (arg_w - 1)
        h = margin * 2 + cell * (arg_h - 1)
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("20x20 Board (Click to place)")
        self.clock = pygame.time.Clock()

        self.status:Status = Status(arg_w,arg_h)
        self.user_turn = arg_user_turn  # 用户执色

    def look_status(self) -> Status:
        return self.status

    def pixel_to_cell(self, px, py):
        # 将鼠标像素坐标映射到最近的格点
        x0, y0 = self.margin, self.margin
        fx = (px - x0) / self.cell
        fy = (py - y0) / self.cell
        x = int(round(fx))
        y = int(round(fy))
        if 0 <= x < self.w and 0 <= y < self.h:
            # 需要离格点足够近才算点击有效
            cx = x0 + x * self.cell
            cy = y0 + y * self.cell
            if (px - cx) ** 2 + (py - cy) ** 2 <= (self.cell * 0.35) ** 2:
                return x, y
        return None

    def place(self, x, y,turn=None):
        if self.status.pawn(Coord(x,y)) != PawnType.TNone:
            return
        if turn is None:
            turn = self.user_turn
        self.status.action(Action(turn,Coord(x,y)))

    def draw(self):
        self.screen.fill((245, 222, 179))  # 棋盘底色（木色）
        # 画网格线
        x0, y0 = self.margin, self.margin
        for i in range(self.w):
            x = x0 + i * self.cell
            pygame.draw.line(self.screen, (0, 0, 0), (x, y0), (x, y0 + (self.h - 1) * self.cell), 1)
            for j in range(self.h):
                y = y0 + j * self.cell
                pygame.draw.line(self.screen, (0, 0, 0), (x0, y), (x0 + (self.w - 1) * self.cell, y), 1)

        # 画棋子
        for y in range(self.h):
            for x in range(self.w):
                v = self.status.pawn(Coord(x,y))
                if v == PawnType.TNone:
                    continue
                cx = x0 + x * self.cell
                cy = y0 + y * self.cell
                r = int(self.cell * 0.40)
                if v == PawnType.TBlack:
                    pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), r)
                else:
                    pygame.draw.circle(self.screen, (255, 255, 255), (cx, cy), r)
                    pygame.draw.circle(self.screen, (0, 0, 0), (cx, cy), r, 1)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = self.pixel_to_cell(*event.pos)
                    if pos:
                        self.place(*pos)
                        return

            self.draw()
            self.clock.tick(60)

        pygame.quit()
