# dragon_sword1_pyxel_s_vram.py
# Sパネルも仮想VRAMで管理（配列不要）

import pyxel

MODE_PUZZLE = 0
MODE_BATTLE = 1
MODE_TITLE = 2
MODE_RETURN = 3
MODE_OVER = 4
MODE_GIVE = 5
MODE_GIVE2 = 6
MODE_CLEAR = 7
MODE_CLEAR2 = 8
MODE_RETURN = 9
MODE_ESCAPE = 10
MODE_WIN = 11
MODE_END = 12

TILE = 32
W, H = 12, 12
MAX_STAGES = 12

LEVELS = [
	"############"	# 1
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

	"############"	# 2
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

	"############"	# 3
	"###..PB....#"
	"##.........#"
	"#.S.#.#.####"
	"##S..##.#.##"
	"#..........#"
	"###...S.#.##"
	"##.#.S.#####"
	"##.S.###.S.#"
	"##S..#.#.S.#"
	"#..........#"
	"######G#####",

	"############"	# 4
	"#....PB....#"
	"#....##....#"
	"#........S##"
	"#.........##"
	"#....#...S##"
	"#...SSS....#"
	"#..S...S...#"
	"#..SS.SS...#"
	"#.#...S.#..#"
	"###.##HHH###"
	"######G#####",

	"############"	# 5
	"#....PB....#"
	"#..SSSSSS..#"
	"#.S......S.#"
	"#.S..SS..S.#"
	"#.S.S..S.S.#"
	"#.S.S..S.S.#"
	"#.S..SS..S.#"
	"#.S......S.#"
	"#..SSSSSS..#"
	"#..........#"
	"######G#####",

	"############"	# 6
	"#....PB....#"
	"#..........#"
	"#..........#"
	"#.....S...H#"
	"#...S.#.S.H#"
	"#.S.S.#.S.H#"
	"#.S.S.#.S.H#"
	"#.S.S###S.H#"
	"#.SSSSSSSSH#"
	"#........###"
	"######G#####",

	"############" # 7
	"#.###PB###.#"
	"###...H...##"
	"##..#SS#S.##"
	"##SS....S.##"
	"#.....#S..##"
	"#.....S..H.#"
	"#....SHS#..#"
	"#..........#"
	"#....#H#...#"
	"#....#H#...#"
	"######G#####",

	"############"	# 8
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

	"############"	# 9
	"#....PB....#"
	"#.S.S.H.S.S#"
	"#.S.S.S.S.S#"
	"#..S.S.#.S.#"
	"#..S.#.S.S.#"
	"#...S.S.S..#"
	"#...S.#.S..#"
	"#....S.S...#"
	"#....S.S...#"
	"#.....H....#"
	"######G#####",

	"############"	# 10
	"#....PBH...#"
	"#...SSHSS..#"
	"#..SS.H.SS.#"
	"#.S.S.H.S.S#"
	"#.SSSHSHSSS#"
	"#.SS.S.S.SS#"
	"#..SS...SS.#"
	"#...SS.SS..#"
	"#....SSS...#"
	"#..........#"
	"######G#####",

	"############"	# 11
	"#....PB....#"
	"#.....H....#"
	"#...#.H.#..#"
	"#...#.S.#.H#"
	"#...S.S.#.H#"
	"#.H.#.S.#.H#"
	"#.HHSH#SSSH#"
	"#.HH......H#"
	"#.HHS.SSSHH#"
	"#..##H...H.#"
	"######G#####",

	"############"	# 12
	"#.S..PB##..#"
	"#.S...H.H..#"
	"#.S...SSS..#"
	"#.H##.#.#..#"
	"#..........#"
	"##SH.#####.#"
	"##.....#...#"
	"####...S...#"
	"#..#...S...#"
	"####...S...#"
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
		self.mode = MODE_TITLE
		self.hp = 20
		self.atk = 5
		self.exp = 0
		self.level = 1
		self.parse_map()
#		self.fall_counter = 0  # 落下カウンタ追加
#		self.fall_delay = 1  # 1フレーム待機でスロー
		self.count = 0
		self.failed = False
		self.attacked = False
		self.levelup = False

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
					self.mode = MODE_CLEAR
					self.count = 30
					return True
		return False

	def update(self):
		pyxel.rndi(0, 255)
		if self.mode == MODE_TITLE:
			if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A): 
				self.mode = MODE_PUZZLE

		elif self.mode == MODE_GIVE2:
			self.hp = 20 + 5 * self.level
			self.parse_map()
			moved = True
			self.mode = MODE_PUZZLE

		elif self.mode == MODE_CLEAR2:
			self.stage = (self.stage + 1)
			if self.stage == MAX_STAGES:
				self.stage = 0
				self.count = 300
				self.mode = MODE_END
			else:
				self.hp = 20 + 5 * self.level
				self.parse_map()
				self.mode = MODE_PUZZLE

		elif self.mode == MODE_PUZZLE:
			self.attacked = False
			self.failed = False
			moved = False
			if self.gravity_fall():
				moved= False #True

			if(self.count == 0):
				left = pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
				right = pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
				up = pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
				down = pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
			else:
				left = right = up = down = 0
			count = int(left) + int(right) + int(up) + int(down)

			if(count == 1):
				if left: moved = self.try_move(-1, 0)
				elif right: moved = self.try_move(1, 0)
				elif up: moved = self.try_move(0, -1)
				elif down: moved = self.try_move(0, 1)
				self.count = 5
			if pyxel.btnp(pyxel.KEY_G) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):  # ギブアップ
				self.mode = MODE_GIVE
				self.count = 30

			if moved and pyxel.rndi(0, 99) < 3:
				self.mode = MODE_BATTLE
				self.enemy_hp = 10 + self.level * 5
				self.enemy_atk = 3 + int(self.level * 3 / 2)

		elif self.mode == MODE_BATTLE:
			if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):  # 攻撃
				self.failed = False
				self.enemy_hp -= self.atk
				if self.enemy_hp <= 0:
					self.attacked = False
					self.exp += 10
					self.count = 30
					self.mode = MODE_WIN
					if self.level < len(LEVEL_THRESHOLD) and self.exp >= LEVEL_THRESHOLD[self.level]:
						self.level += 1
						self.hp = 20 + 5 * self.level
						self.atk += 2
						self.levelup = True
					else:
						self.levelup = False

				else:
					self.hp -= self.enemy_atk
					if self.hp <= 0:
						self.count = 60
						self.mode = MODE_OVER
						self.parse_map()
					else:
						self.attacked = True
						self.count = 60

			if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):  # 逃げる
				if pyxel.rndi(0, 255) < 153:  # 60%成功
					self.failed = False
					self.count = 30
					self.mode = MODE_ESCAPE
				else:
					self.failed = True
					self.hp -= self.enemy_atk
					self.count = 60
					if self.hp <= 0:
						self.count = 60
						self.mode = MODE_OVER
						self.parse_map()

	def draw(self):
		pyxel.cls(0)
		if(self.count > 0):
			self.count -= 1

		if self.mode == MODE_PUZZLE or self.mode == MODE_GIVE or self.mode == MODE_CLEAR:
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
		if self.mode != MODE_TITLE and self.mode != MODE_GIVE and self.mode != MODE_END:
			self.put_strings(2, H * TILE + 2, f"STAGE:{self.stage+1} LV:{self.level} HP:{self.hp}")
			self.put_strings(2, H * TILE + 16, f"EXP:{self.exp} GIVE UP G")

#			self.put_strings(50+60, 90+100, f"{self.count}")

		if self.mode == MODE_TITLE:
			self.put_strings(5*16, 15*16, "      i  k   ")
			self.put_strings(5*16, 16*16, " 2026 bcdefgh")
			self.put_strings(3*16, 8*16, "DRAGON SWORD PART 1")
			self.put_strings(3*16, 20*16, "HIT Z KEY TO START")

		if self.mode == MODE_END:
			self.put_strings(8*16, 10*16, "ALL CLEAR")
			self.put_strings(5*16, 12*16,"CONGRATULATIONS")
			if self.count == 0:
				self.reset()
#				self.mode = MODE_TITLE

		if self.mode == MODE_GIVE:
			self.put_strings(0, 24*16, "GIVE UP")
			if self.count == 0:
				self.mode = MODE_GIVE2

		if self.mode == MODE_CLEAR:
			self.put_strings(6*16, 10*16, "STAGE CLEAR")
			if self.count == 0:
				self.mode = MODE_CLEAR2

		if self.mode == MODE_ESCAPE:
			self.put_strings(60+60, 150+100, "ESCAPED")
			if self.count == 0:
				self.mode = MODE_PUZZLE

		if self.mode == MODE_WIN:
			self.put_strings(5*16, 10*16, "ENEMY DEFEATED")
			if self.levelup == True:
				self.put_strings(5*16, 16*16, "LEVEL UP")
			if self.count == 0:
				self.mode = MODE_PUZZLE

		if self.mode == MODE_BATTLE or  self.mode == MODE_ESCAPE:
#			pyxel.rect(30, 40, 100, 64, 0)
#			pyxel.rectb(30, 40, 100, 64, 7)
			pyxel.circ(80+120-4, 60+100, 20, 13)
			pyxel.blt(60+120, 40+100, 0, 7 * 32, 0, 32, 32, 0)
			self.put_strings(20+60, 90+100, "SLIME APPEARED")
			self.put_strings(20+40, 120+100, "Z:ATTACK X:ESCAPE")
			if self.failed == True:
				if self.count > 0:
					self.put_strings(60+60, 150+100, "FAILED")
			elif self.attacked == True:
				if self.count > 0:
					self.put_strings(60+60, 150+100, "HIT")
				else:
					self.attacked = False

		if self.mode == MODE_OVER:
			if self.count == 0:
				self.mode = MODE_PUZZLE
				self.hp = 20 + 5 * self.level
			else:
				self.put_strings(50+60, 90+100, "YOU DEAD")

Game()