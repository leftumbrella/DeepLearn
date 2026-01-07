import pygame

EMPTY, BLACK, WHITE = 0, 1, 2

class Game:
    def __init__(self, n=20, cell=30, margin=40):
        pygame.init()
        self.n = n
        self.cell = cell
        self.margin = margin
        w = margin * 2 + cell * (n - 1)
        h = margin * 2 + cell * (n - 1)
        self.screen = pygame.display.set_mode((w, h))
        pygame.display.set_caption("20x20 Board (Click to place)")
        self.clock = pygame.time.Clock()

        self.grid = [[EMPTY for _ in range(n)] for _ in range(n)]
        self.history = []
        self.turn = BLACK  # 黑先

    def reset(self):
        self.grid = [[EMPTY for _ in range(self.n)] for _ in range(self.n)]
        self.history.clear()
        self.turn = BLACK

    def undo(self):
        if not self.history:
            return
        x, y = self.history.pop()
        self.grid[y][x] = EMPTY
        self.turn = BLACK if self.turn == WHITE else WHITE

    def pixel_to_cell(self, px, py):
        # 将鼠标像素坐标映射到最近的格点
        x0, y0 = self.margin, self.margin
        fx = (px - x0) / self.cell
        fy = (py - y0) / self.cell
        x = int(round(fx))
        y = int(round(fy))
        if 0 <= x < self.n and 0 <= y < self.n:
            # 需要离格点足够近才算点击有效
            cx = x0 + x * self.cell
            cy = y0 + y * self.cell
            if (px - cx) ** 2 + (py - cy) ** 2 <= (self.cell * 0.35) ** 2:
                return x, y
        return None

    def place(self, x, y):
        if self.grid[y][x] != EMPTY:
            return
        self.grid[y][x] = self.turn
        self.history.append((x, y))
        self.turn = WHITE if self.turn == BLACK else BLACK

    def draw(self):
        self.screen.fill((245, 222, 179))  # 棋盘底色（木色）
        # 画网格线
        x0, y0 = self.margin, self.margin
        for i in range(self.n):
            x = x0 + i * self.cell
            pygame.draw.line(self.screen, (0, 0, 0), (x, y0), (x, y0 + (self.n - 1) * self.cell), 1)
            y = y0 + i * self.cell
            pygame.draw.line(self.screen, (0, 0, 0), (x0, y), (x0 + (self.n - 1) * self.cell, y), 1)

        # 画棋子
        for y in range(self.n):
            for x in range(self.n):
                v = self.grid[y][x]
                if v == EMPTY:
                    continue
                cx = x0 + x * self.cell
                cy = y0 + y * self.cell
                r = int(self.cell * 0.40)
                if v == BLACK:
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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.undo()
                    elif event.key == pygame.K_r:
                        self.reset()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = self.pixel_to_cell(*event.pos)
                    if pos:
                        self.place(*pos)

            self.draw()
            self.clock.tick(60)

        pygame.quit()
