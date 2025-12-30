# dragon_sword1_pyxel_s_vram.py
# Sパネルも仮想VRAMで管理（配列不要）

import pyxel

TILE = 16
W, H = 12, 12
MAX_STAGES = 3

LEVELS = [
	"############"
	"#....PB....#"
	"##SSS.SHS.##"
	"##..S.S.#.##"
	"##....S.#.##"
	"##....S.#.##"
	"##.SS.S.#.##"
	"##..S.S.#.##"
	"##..S.S.#..#"
	"##SSS.SHS.##"
	"#.........##"
	"######G#####",

	"############"
	"#.#..PB.#..#"
	"#####.#.#..#"
	"#.S.S...#..#"
	"#.S.SSSH...#"
	"#..........#"
	"#..##...#.S#"
	"#.S.#.S.#.H#"
	"#.SS#...#.##"
	"#S..#.##...#"
	"#..S......##"
	"######G#####",

	"############"
	"###..PB..#.#"
	"#..#S#S..#.#"
	"#.......#.S#"
	"#..#..##...#"
	"#...##.....#"
	"##....S.S..#"
	"#.S###.S.S##"
	"#..........#"
	"###H###SSSS#"
	"#..........#"
	"######G#####",
]

LEVEL_THRESHOLD = [0, 20, 50, 90, 140, 200, 270, 350, 440, 540]

class Game:
    def __init__(self):
        pyxel.init(W * TILE, H * TILE + 32, title="Dragon Sword 1 - S VRAM", fps=30)
        pyxel.sound(0).set("c3e3", "s", "64", "n", 10)	  # 射撃: ピコピコ
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.stage = 0
        self.mode = 0
        self.hp = 20
        self.atk = 5
        self.exp = 0
        self.level = 1
        self.parse_map()
#        self.fall_counter = 0  # 落下カウンタ追加
#        self.fall_delay = 1  # 1フレーム待機でスロー

    def parse_map(self):
        lvl = LEVELS[self.stage]
        self.vram = [list(lvl[y*W:y*W+W]) for y in range(H)]
        self.px = self.py = 0
        self.gx = self.gy = -1
        self.goal_x = self.goal_y = 0
        for y in range(H):
            for x in range(W):
                c = self.vram[y][x]
                if c == 'P':
                    self.px, self.py = x, y
                    self.vram[y][x] = '.'
                elif c == 'B':
                    self.gx, self.gy = x, y
                    self.vram[y][x] = '.'
                elif c == 'G':
                    self.goal_x, self.goal_y = x, y

    def can_move(self, x, y):
        if not (0 <= x < W and 0 <= y < H): return False
        c = self.vram[y][x]
        if c in '#HS': return False  # #壁, H残存, Sパネルは通れない
        if self.gx == x and self.gy == y: return False
        return True

    def try_move(self, dx, dy):
        nx, ny = self.px + dx, self.py + dy
        moved = False

        # 重力パネル押す
        if self.gx == nx and self.gy == ny:
            gnx, gny = nx + dx, ny + dy
            if self.can_move(gnx, gny):
                self.gx, self.gy = gnx, gny
#                self.px, self.py = nx, ny
#                moved = True

        # Sパネル押す
        elif self.vram[ny][nx] == 'S':
            pnx, pny = nx + dx, ny + dy
            if self.can_move(pnx, pny):
                self.vram[ny][nx] = '.'
                self.vram[pny][pnx] = 'S'
#                self.px, self.py = nx, ny
#                moved = False

        # 通常移動
        elif self.can_move(nx, ny):
            if self.vram[ny][nx] != 'G':
                self.px, self.py = nx, ny
                moved = True

        if moved:
            pyxel.play(0, 0)
            return True
        return False

    def gravity_fall(self):
        if self.gx == -1: return
#        if self.fall_counter > 0:
#            self.fall_counter -= 1
#            return  # 待機中

#        self.fall_counter = self.fall_delay  # 次落下まで待機
        if self.gy + 1 < H:
            nx, ny = self.gx, self.gy + 1
            c = self.vram[ny][nx]
            if c != '#':
                if c == 'H':
                    self.vram[ny][nx] = '.'  # H消す
                if not self.can_move(nx, ny): return False
                self.gy += 1
                pyxel.play(0, 1)
                if self.gx == self.goal_x and self.gy == self.goal_y:
                    pyxel.play(0, 2)
                    self.stage = (self.stage + 1) % MAX_STAGES
                    self.hp = 20 + 5 * self.level
                    self.parse_map()
                    return True
        return False

    def update(self):
        if self.mode == 0:
            moved = False
            if self.gravity_fall():
                moved= True

            if pyxel.btnp(pyxel.KEY_LEFT): moved = self.try_move(-1, 0)
            if pyxel.btnp(pyxel.KEY_RIGHT): moved = self.try_move(1, 0)
            if pyxel.btnp(pyxel.KEY_UP): moved = self.try_move(0, -1)
            if pyxel.btnp(pyxel.KEY_DOWN): moved = self.try_move(0, 1)
            if pyxel.btnp(pyxel.KEY_G):  # ギブアップ
                self.hp = 20 + 5 * self.level
                self.parse_map()
                moved = True

            if moved and pyxel.rndi(0, 99) < 3:
                self.mode = 1
                self.enemy_hp = 10 + self.level * 5
                self.enemy_atk = 3 + self.level * 2

        else:
            if pyxel.btnp(pyxel.KEY_A):  # 攻撃
                self.enemy_hp -= self.atk
                if self.enemy_hp <= 0:
                    self.exp += 10
                    if self.level < len(LEVEL_THRESHOLD) and self.exp >= LEVEL_THRESHOLD[self.level]:
                        self.level += 1
                        self.hp = 20 + 5 * self.level
                        self.atk += 2
                    self.mode = 0
                else:
                    self.hp -= self.enemy_atk
                    if self.hp <= 0:
                        self.hp = 20 + 5 * self.level
                        self.mode = 0
                        self.parse_map()

            if pyxel.btnp(pyxel.KEY_B):  # 逃げる
                if pyxel.rndi(0, 255) < 192:  # 75%成功
                    self.mode = 0
                else:
                    self.hp -= self.enemy_atk
                    if self.hp <= 0:
                        self.hp = 20 + 5 * self.level
                        self.mode = 0
                        self.parse_map()

    def draw(self):
        pyxel.cls(0)

        for y in range(H):
            for x in range(W):
                tx, ty = x * TILE, y * TILE
                c = self.vram[y][x]
                col = 1  # 床
                if c == '#': col = 0
                if c == 'G': col = 10
                if c == 'H': col = 13
                if c == 'S': col = 11  # Sパネル
                pyxel.rect(tx, ty, TILE, TILE, col)

        # プレイヤー
        pyxel.rect(self.px * TILE + 2, self.py * TILE + 2, 12, 12, 8)

        # 重力パネル
        if self.gx != -1:
            gx, gy = self.gx * TILE, self.gy * TILE
            pyxel.rect(gx + 2, gy + 2, 12, 12, 9)
            pyxel.tri(gx + 4, gy + 10, gx + 12, gy + 10, gx + 8, gy + 14, 8)

        # ステータス
        pyxel.text(2, H * TILE + 2, f"STAGE:{self.stage+1} LV:{self.level} HP:{self.hp} EXP:{self.exp}", 7)

        pyxel.text(2, H * TILE + 16, "GIVE UP - 'G'", 7)

        if self.mode == 1:
            pyxel.rect(30, 40, 100, 64, 0)
            pyxel.rectb(30, 40, 100, 64, 7)
            pyxel.circ(80, 60, 20, 13)
            pyxel.text(40, 90, "Slime appeared!", 7)
            pyxel.text(40, 100, "A:Attack B:Escape", 7)

Game()