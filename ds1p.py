# dragon_sword1_pyxel_s_vram.py
# Sパネルも仮想VRAMで管理（配列不要）

import pyxel

TILE = 32
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
		pyxel.init(W * TILE, H * TILE + 32, title="Dragon Sword 1 Plus", fps=30)
		pyxel.mouse(False)
		pyxel.load("ds1p.pyxres")

		pyxel.sounds[0].set("c3e3", "s", "64", "n", 10)	  # 射撃: ピコピコ
		self.reset()
		pyxel.run(self.update, self.draw)

	# 文字列表示
	def put_strings(self, x, y, str):
		chr = str.encode("UTF-8")
		for i in range(len(str)):
			a = chr[i]
			if(a < 0x30):
				a = 0x40
			a = a - 0x30
			pyxel.blt((x + i * 16), y, 1, (a % 16) * 16, int(a / 16) * 16, 16, 16, 0)

	def reset(self):
		self.stage = 0
		self.mode = 0
		self.hp = 20
		self.atk = 5
		self.exp = 0
		self.level = 1
		self.parse_map()
#		self.fall_counter = 0  # 落下カウンタ追加
#		self.fall_delay = 1  # 1フレーム待機でスロー
		self.count = 0
		self.failed = False

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
#				self.px, self.py = nx, ny
#				moved = True

		# Sパネル押す
		elif self.vram[ny][nx] == 'S':
			pnx, pny = nx + dx, ny + dy
			if self.can_move(pnx, pny):
				self.vram[ny][nx] = '.'
				self.vram[pny][pnx] = 'S'
#				self.px, self.py = nx, ny
#				moved = False

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
#		if self.fall_counter > 0:
#			self.fall_counter -= 1
#			return  # 待機中

#		self.fall_counter = self.fall_delay  # 次落下まで待機
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

			left = pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
			right = pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
			up = pyxel.btnp(pyxel.KEY_UP) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
			down = pyxel.btnp(pyxel.KEY_DOWN) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)

			count = int(left) + int(right) + int(up) + int(down)

			if(count == 1):
				if left: moved = self.try_move(-1, 0)
				elif right: moved = self.try_move(1, 0)
				elif up: moved = self.try_move(0, -1)
				elif down: moved = self.try_move(0, 1)
			if pyxel.btnp(pyxel.KEY_G) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):  # ギブアップ
				self.hp = 20 + 5 * self.level
				self.parse_map()
				moved = True

			if moved and pyxel.rndi(0, 99) < 3:
				self.mode = 1
				self.enemy_hp = 10 + self.level * 5
				self.enemy_atk = 3 + self.level * 2

		else:
			if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):  # 攻撃
				self.failed = False
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
						self.count = 60
						self.hp = 20 + 5 * self.level
						self.mode = 2
						self.parse_map()

			if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):  # 逃げる
				if pyxel.rndi(0, 255) < 192:  # 75%成功
					self.failed = False
					self.mode = 0
				else:
					self.failed = True
					self.hp -= self.enemy_atk
					self.count = 60
					if self.hp <= 0:
						self.hp = 20 + 5 * self.level
						self.mode = 2
						self.parse_map()

	def draw(self):
		pyxel.cls(0)
		if(self.count > 0):
			self.count -= 1

		if self.mode == 0:
			for y in range(H):
				for x in range(W):
					tx, ty = x * TILE, y * TILE
					c = self.vram[y][x]
					col = 1  # 床
					if c == '#': col = 0
					if c == 'G': col = 5
					if c == 'H': col = 6
					if c == 'S': col = 3  # Sパネル
#					pyxel.rect(tx, ty, TILE, TILE, col)
					pyxel.blt(tx, ty, 0, col * 32, 0, 32, 32, 0)

			# プレイヤー
#			pyxel.rect(self.px * TILE + 2, self.py * TILE + 2, 12, 12, 8)
			pyxel.blt(self.px * TILE, self.py * TILE, 0, 2 * 32, 0, 32, 32, 0)

			# 重力パネル
			if self.gx != -1:
				gx, gy = self.gx * TILE, self.gy * TILE
				pyxel.blt(gx, gy, 0, 4 * 32, 0, 32, 32, 0)
#				pyxel.rect(gx + 2, gy + 2, 12, 12, 9)
#				pyxel.tri(gx + 4, gy + 10, gx + 12, gy + 10, gx + 8, gy + 14, 8)

		# ステータス
		self.put_strings(2, H * TILE + 2, f"STAGE:{self.stage+1} LV:{self.level} HP:{self.hp}")
		self.put_strings(2, H * TILE + 16, f"EXP:{self.exp} GIVE UP G")

#		self.put_strings(50+60, 90+100, f"{self.count}")

		if self.mode == 1:
#			pyxel.rect(30, 40, 100, 64, 0)
#			pyxel.rectb(30, 40, 100, 64, 7)
			pyxel.circ(80+120-4, 60+100, 20, 13)
			pyxel.blt(60+120, 40+100, 0, 7 * 32, 0, 32, 32, 0)
			self.put_strings(20+60, 90+100, "SLIME APPEARED")
			self.put_strings(20+40, 120+100, "Z:ATTACK X:ESCAPE")
			if self.failed == True:
				if self.count > 0:
					self.put_strings(60+60, 150+100, "FAILED")

		if self.mode == 2:
			if self.count == 0:
				self.mode = 0
			else:
				self.put_strings(50+60, 90+100, "YOU DEAD")

Game()