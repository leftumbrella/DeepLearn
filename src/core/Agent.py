from src.base.SrcIndex import PawnType, Coord
from src.core.Action import Action
from src.core.Status import Status
import numpy as np

class Agent:
    def __init__(self):
        pass
    def next_action(self,now_status:Status) -> tuple[Action,float]:
        guess = self._next_move_win_prob_map(now_status.status,PawnType.TWhite)
        idx = np.argmax(guess)
        x, y = np.unravel_index(idx, guess.shape)
        return Action(PawnType.TWhite,Coord(x,y)),guess.max()

    def _next_move_win_prob_map(self,board: np.ndarray, pawn_type: PawnType, win_len: int = 5) -> np.ndarray:
        """
        board: ndarray, shape (H,W), 0=空, 1=白, 2=黑
        color: 1 或 2，表示“我方”颜色
        return: prob ndarray, shape (H,W), 0~1，非空点为0
        """
        color = pawn_type.value
        board = np.asarray(board, dtype=np.int8)
        H, W = board.shape
        assert color in (1, 2)
        opp = 3 - color
        empty = (board == 0)

        # 评分矩阵（越大越好）
        scores = np.zeros((H, W), dtype=np.float32)

        # 你可以按需求调这些权重（越大越“敏感”）
        # key = (落下这一子后，该 5 连窗里我方棋子数)
        MY_WEIGHTS = {5: 1_000_000.0, 4: 50_000.0, 3: 2_000.0, 2: 80.0, 1: 5.0}
        OPP_WEIGHTS = {5: 900_000.0, 4: 40_000.0, 3: 1_500.0, 2: 60.0, 1: 3.0}  # 挡对手稍弱一点也行

        def weight_after_place(n_after: np.ndarray, table: dict) -> np.ndarray:
            # n_after 取值 1..5
            out = np.zeros_like(n_after, dtype=np.float32)
            for k, v in table.items():
                out = np.where(n_after == k, v, out)
            return out

        def process_line(ys: np.ndarray, xs: np.ndarray):
            """对一条线（给出该线每个格子的坐标数组 ys/xs）做滑窗评分，并散射回 scores"""
            line = board[ys, xs]  # shape (L,)
            L = line.size
            if L < win_len:
                return

            # 1D 滑窗：shape (L-4, 5)
            windows = np.lib.stride_tricks.sliding_window_view(line, win_len)

            my_cnt = (windows == color).sum(axis=-1)
            opp_cnt = (windows == opp).sum(axis=-1)
            emp_m = (windows == 0)

            # 在这个 5 连窗里，如果双方都有子 => 这窗对任何一方都基本没价值
            both = (my_cnt > 0) & (opp_cnt > 0)

            # 我方进攻潜力：对手在该窗里为 0 时才有意义
            my_pot = np.where((opp_cnt == 0) & (~both),
                              weight_after_place(my_cnt + 1, MY_WEIGHTS),
                              0.0)

            # 防守（挡对手）潜力：我方在该窗里为 0 时才有意义
            opp_pot = np.where((my_cnt == 0) & (~both),
                               weight_after_place(opp_cnt + 1, OPP_WEIGHTS),
                               0.0)

            seg_score = my_pot + opp_pot  # shape (L-4,)

            # 把 seg_score 分配给每个窗口中的“空位格”
            starts = np.arange(L - win_len + 1)[:, None]  # (L-4,1)
            ks = np.arange(win_len)[None, :]  # (1,5)
            cell_i = starts + ks  # (L-4,5)  每个窗对应线上的 index

            contrib = seg_score[:, None] * emp_m  # 只给空位格加分
            flat = contrib.ravel()
            if np.all(flat == 0):
                return

            yi = ys[cell_i].ravel()
            xi = xs[cell_i].ravel()
            np.add.at(scores, (yi, xi), flat)

        # 横线
        for y in range(H):
            ys = np.full(W, y, dtype=np.int32)
            xs = np.arange(W, dtype=np.int32)
            process_line(ys, xs)

        # 竖线
        for x in range(W):
            ys = np.arange(H, dtype=np.int32)
            xs = np.full(H, x, dtype=np.int32)
            process_line(ys, xs)

        # 主对角线 "\"
        for sy in range(H):
            ys = np.arange(sy, H, dtype=np.int32)
            xs = np.arange(0, H - sy, dtype=np.int32)
            process_line(ys, xs)
        for sx in range(1, W):
            ys = np.arange(0, W - sx, dtype=np.int32)
            xs = np.arange(sx, W, dtype=np.int32)
            process_line(ys, xs)

        # 副对角线 "/"
        for sy in range(H):
            ys = np.arange(sy, -1, -1, dtype=np.int32)
            xs = np.arange(0, sy + 1, dtype=np.int32)
            process_line(ys, xs)
        for sx in range(1, W):
            ys = np.arange(H - 1, -1, -1, dtype=np.int32)
            xs = np.arange(sx, W, dtype=np.int32)
            # 只取能对应到棋盘内的部分
            L = min(ys.size, xs.size)
            process_line(ys[:L], xs[:L])

        # 非空点不可落子：概率设为0
        scores[~empty] = 0.0

        # ---- 归一化到 0~1 ----
        # 由于 scores 动态范围很大，用 log1p 压缩一下再 min-max
        s = np.log1p(np.maximum(scores, 0.0))
        mask = empty
        prob = np.zeros_like(s, dtype=np.float32)
        if np.any(mask):
            mn = float(s[mask].min())
            mx = float(s[mask].max())
            if mx > mn:
                prob[mask] = (s[mask] - mn) / (mx - mn)
            else:
                prob[mask] = 0.0  # 所有空位同分
        return prob