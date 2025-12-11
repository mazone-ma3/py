import pyxel
import random

class Reversi:
    def __init__(self):
        pyxel.init(160, 160, title="絶対に動くリバーシ（最終）", fps=60)
        pyxel.mouse(True)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.board = [[0]*8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = 2
        self.turn = 1
        self.message = ""

    def valid(self, x, y, player, flip=False):
        if not (0 <= x < 8 and 0 <= y < 8) or self.board[y][x] != 0:
            return False
        opp = 3 - player
        dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        found = False
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 8 and 0 <= ny < 8 and self.board[ny][nx] == opp:
                nx += dx
                ny += dy
                while 0 <= nx < 8 and 0 <= ny < 8 and self.board[ny][nx] == opp:  # ← ここ修正！
                    nx += dx
                    ny += dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[ny][nx] == player:
                    found = True
                    if flip:
                        nx, ny = x + dx, y + dy
                        while self.board[ny][nx] == opp:
                            self.board[ny][nx] = player
                            nx += dx
                            ny += dy
        return found

    def get_moves(self, player):
        return [(x,y) for y in range(8) for x in range(8) if self.valid(x,y,player)]

    def cpu_move(self):
        moves = self.get_moves(2)
        if not moves: return False
        # 隅＞端＞その他 の順で優先
        priority = [(0,0),(0,7),(7,0),(7,7), (0,1),(1,0),(1,1),(6,0),(7,1),(0,6),(1,7),(6,7),(7,6)]
        for px,py in priority:
            if (px,py) in moves:
                x,y = px,py
                break
        else:
            x,y = random.choice(moves)
        self.valid(x, y, 2, True)
        self.board[y][x] = 2
        return True

    def update(self):
        if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x = pyxel.mouse_x // 20
            y = pyxel.mouse_y // 20
            if 0 <= x < 8 and 0 <= y < 8 and self.valid(x, y, 1, True):
                self.board[y][x] = 1
                self.turn = 2

        if self.turn == 2:
            if self.cpu_move():
                self.turn = 1

        if not self.get_moves(self.turn):
            self.turn = 3 - self.turn
            if not self.get_moves(self.turn):
                b = sum(r.count(1) for r in self.board)
                w = 64 - b
                win = "黒の勝ち！" if b > w else "白の勝ち！" if b < w else "引き分け"
                self.message = f"ゲーム終了！ {b}－{w} {win}"

    def draw(self):
        pyxel.cls(3)
        for i in range(9):
            pyxel.line(i*20,0,i*20,160,1)
            pyxel.line(0,i*20,160,i*20,1)
        for y in range(8):
            for x in range(8):
                c = self.board[y][x]
                if c == 1: pyxel.circ(x*20+10, y*20+10, 8, 0)
                if c == 2: pyxel.circ(x*20+10, y*20+10, 8, 7)
        for x,y in self.get_moves(self.turn):
            col = 10 if self.turn==1 else 11
            if pyxel.frame_count % 30 < 15:
                pyxel.rect(x*20+6, y*20+6, 8, 8, col)
        if self.message:
            pyxel.text(10, 75, self.message, 0)

Reversi()