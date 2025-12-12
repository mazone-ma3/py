import pyxel
import random

class Reversi:
    def __init__(self):
        pyxel.init(160, 160, title="リバーシ", fps=60)
        pyxel.mouse(True)
        self.new_game()
        pyxel.run(self.update, self.draw)

    def new_game(self):
        self.board = [[0]*8 for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 1
        self.board[3][4] = self.board[4][3] = 2
        self.turn = 1
        self.game_over = False
        self.waiting_cpu = False
        self.black = 0
        self.white = 0
        self.result = ""

    def valid(self, x, y, player, flip=False):
        if not (0<=x<8 and 0<=y<8) or self.board[y][x] != 0:
            return False
        opp = 3 - player
        dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        found = False
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if 0<=nx<8 and 0<=ny<8 and self.board[ny][nx] == opp:
                nx += dx; ny += dy
                while 0<=nx<8 and 0<=ny<8 and self.board[ny][nx] == opp:
                    nx += dx; ny += dy
                if 0<=nx<8 and 0<=ny<8 and self.board[ny][nx] == player:
                    found = True
                    if flip:
                        nx, ny = x + dx, y + dy
                        while self.board[ny][nx] == opp:
                            self.board[ny][nx] = player
                            nx += dx; ny += dy
        return found

    def get_moves(self, player):
        return [(x,y) for y in range(8) for x in range(8) if self.valid(x,y,player)]

    def cpu_move(self):
        moves = self.get_moves(2)
        if not moves: return False
        # 隅最優先
        corners = [(0,0),(0,7),(7,0),(7,7)]
        for pos in corners:
            if pos in moves:
                x,y = pos
                self.valid(x, y, 2, True)
                self.board[y][x] = 2
                return True
        x,y = random.choice(moves)
        self.valid(x, y, 2, True)
        self.board[y][x] = 2
        return True

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                if 40 <= pyxel.mouse_x <= 120 and 100 <= pyxel.mouse_y <= 130:
                    self.new_game()
            return

        if self.turn == 1 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            x = pyxel.mouse_x // 20
            y = pyxel.mouse_y // 20
            if 0<=x<8 and 0<=y<8 and self.valid(x, y, 1, True):
                self.board[y][x] = 1
                self.turn = 2
                self.waiting_cpu = True

        if self.waiting_cpu:
            self.cpu_move()
            self.turn = 1
            self.waiting_cpu = False

        if not self.get_moves(self.turn):
#        if self.get_moves(self.turn):
            self.turn = 3 - self.turn
            if not self.get_moves(self.turn):
                self.black = sum(sum(1 for c in row if c==1) for row in self.board)
                self.white = 64 - self.black
                if self.black > self.white:
                    self.result = "黒の勝ち！"
                elif self.white > self.black:
                    self.result = "白の勝ち！"
                else:
                    self.result = "引き分け"
#                pyxel.rect(40, 120, 80, 30, 8)
#                pyxel.text(30, 70, f"ゲーム終了", 0)
#                pyxel.text(35, 85, f"黒 {black} － 白 {white}", 0)
#                pyxel.text(45, 100, result, 0)
                self.game_over = True

    def draw(self):
        pyxel.cls(3)  # 緑の盤面
        # グリッド
        for i in range(9):
            pyxel.line(i*20,0,i*20,160,1)
            pyxel.line(0,i*20,160,i*20,1)
        # 石
        for y in range(8):
            for x in range(8):
                if self.board[y][x] == 1:
                    pyxel.circ(x*20+10, y*20+10, 9, 0)  # 黒
                elif self.board[y][x] == 2:
                    pyxel.circ(x*20+10, y*20+10, 9, 7)  # 白
        # 置ける場所（点滅）
        for x,y in self.get_moves(self.turn):
            if pyxel.frame_count % 30 < 15:
                pyxel.rect(x*20+6, y*20+6, 8, 8, 10 if self.turn==1 else 11)
        # 手番表示
#        if not self.game_over:
#            if self.turn:
#                pyxel.text(5, 5,  "Turn Black", 7)
#            else:
#                pyxel.text(5, 5,  "Turn White", 7)
        # リトライボタン
        if self.game_over:
            pyxel.rect(45, 65, 80, 30, 8)
            pyxel.text(50, 70, "Game Over", 7)
            pyxel.text(50, 85, f"Black {self.black} － White {self.white}", 7)
            pyxel.text(50, 100, self.result, 7)
            pyxel.text(50, 130, "Retry?", 8)

Reversi()