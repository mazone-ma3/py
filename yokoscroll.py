import pyxel
import random

PAT_JIKI_N = 0
PAT_JIKI_R = 1
PAT_JIKI_L = 2
PAT_JIKI_J = 3

class Game:
	# 文字列表示
	def put_strings(self, x, y, str):
		chr = str.encode("UTF-8")
		for i in range(len(str)):
			a = chr[i]
			if(a < 0x30):
				a = 0x40
			a = a - 0x30
			pyxel.blt((x + i) * 8, y * 8, 1, (a % 16) * 8, int(a / 16) * 8, 8, 8, 0)

	# 数字表示
	def put_numd(self, j, digit):
		i = 0 #digit
		self.str_temp = ""
		k = 0
		l = b""
		while (i < digit):
			i = i + 1
			k = int(j / (10**(digit-i))) % 10
			l += str(k).encode('UTF-8')
		self.str_temp = l.decode("UTF-8")

	def init_ground(self):
		# 地形データ（穴復活）
		olda = 80
		self.ground_heights = [100] * 100
		for i in range(5, 100, 5):  # 5マスごとにランダム
			while True:
				a = random.choice([70, 80, 90, 100, 130])
				if(olda == 130):
					if(a == 130):
						continue
				break

			self.ground_heights[i:i+5] = [a] * 5
			olda = a

	def __init__(self):
		pyxel.init(160, 120, fps=60, title="Yoko Scroll")
		pyxel.load("rain.pyxres")
		self.player_x = 20
		self.player_y = 80
		self.player_vy = 0
		self.camera_x = 0
		self.player_type = PAT_JIKI_N
		self.player_type2 = PAT_JIKI_N
		self.wake_count = 0
		self.xx = 0
		self.restart = True
		self.fallout = False

		self.init_ground()

		# 効果音
		pyxel.sounds[0].set("c3", "t", "7", "n", 5)  # ジャンプ
		pyxel.sounds[1].set("a2", "s", "5", "f", 10)  # ミス
		pyxel.run(self.update, self.draw)

	def wakecount(self):
#		if(self.player_vy == 0):
		if(self.wake_count >= 8):
			self.player_type2 = PAT_JIKI_L
		else:
			self.player_type2 = PAT_JIKI_R
		self.wake_count += 1;
		self.wake_count %= 16;
#		else:
#			self.player_type2 = PAT_JIKI_N
		return self.player_type2

	def update(self):
#		self.player_type2 = self.player_type
#		elif(self.player_vy > 0):
#			self.player_type2 = PAT_JIKI_N

		# 横移動（壁判定）
		new_x = self.player_x
		if(self.player_vy == 0):
			self.restart = False;

		if(self.restart == False):
#			self.xx = 0
#			if self.can_move_to(new_x+10+1, self.player_y):
			if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
				self.xx = 1
#			elif self.can_move_to(new_x-1, self.player_y):
			elif pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
				self.xx = -1
			else:
				self.xx = 0
#		if(old_xx == -2):
#			xx = 0
#		else:
#			old_xx =xx

		if(self.xx != 0):
			if(self.fallout == False):
				self.player_type2 = self.wakecount()
			new_x += self.xx
			if not self.can_move_to(new_x+10, self.player_y):
				new_x = self.player_x
#			self.player_type2 = self.wakecount()
#			new_x -= 1
			if not self.can_move_to(new_x, self.player_y):
				new_x = self.player_x
		if(new_x >= 0):
			self.player_x = new_x

		if(int(self.camera_x / 10) >= (self.player_x)):
			self.player_x = int(self.camera_x / 10) #+= 0.1
#			self.camera_x = max(0, self.player_x) * 10

#		elif((self.player_x + 10) < self.camera_x / 10):
#			self.camera_x = max(10, self.player_x - 80) * 10

		if((self.player_x - 80) > self.camera_x / 10):
			self.camera_x = max(0, self.player_x - 80) * 10

#		else:
#			self.player_x = 500*5


		# ジャンプ（地上のみ）
		if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_B)) and self.is_on_ground() and self.player_vy > 0:
			self.player_vy = -25
			pyxel.play(0, 0)

		# 重力と着地

#		self.player_y += self.player_vy
		old_player_vy = self.player_vy
		self.player_vy += 1

		# 落下中
		if((old_player_vy < 0) and (self.player_vy == 0)):
			self.player_type2 = PAT_JIKI_N
			self.fallout = True

		if(self.player_vy >= 0):
#			self.player_type2 = PAT_JIKI_N
			ground_y = self.get_ground_height(self.player_x + 10)
			if self.player_y > ground_y - 1:
				self.player_y = ground_y - 1
				self.player_vy = 0
				self.fallout = False
#				self.player_type2 = PAT_JIKI_N
			ground_y = self.get_ground_height(self.player_x)
			if self.player_y > ground_y - 1:
				self.player_y = ground_y - 1
				self.player_vy = 0
				self.fallout = False
#				self.player_type2 = PAT_JIKI_N


		self.player_y += (self.player_vy / 10)


		# 穴ミス
		if self.player_y > 120:
			pyxel.play(1, 1)
			self.player_x -= 5*8
			self.player_y = 0 #80
			self.player_vy = 0.1
			self.camera_x = max(0, self.player_x - 40) * 10
			self.xx = 0
			self.restart = True
#			self.init_ground()

		# カメラ
		self.camera_x += 1

		if(self.player_vy < 0):
			self.player_type2 = PAT_JIKI_J
#		if(self.player_vy > 0):
#			self.player_type2 = PAT_JIKI_N
		self.player_type = self.player_type2

	def can_move_to(self, x, y):
		index = int((x) // 8) % len(self.ground_heights)
		next_ground_y = self.ground_heights[index]
		return next_ground_y >= y - 8

	def is_on_ground(self):
		return ((self.player_y >= self.get_ground_height(self.player_x) - 1) or (self.player_y >= self.get_ground_height(self.player_x + 10) - 1))

	def get_ground_height(self, x):
		index = int((x) // 8) % len(self.ground_heights)
		return self.ground_heights[index]

	def draw(self):
		pyxel.cls(12)
		camera = self.camera_x / 10
		# 豆腐地形
		for x in range(-1, 22):
			index = (x + int((camera) // 8)) % len(self.ground_heights)
			ground_y = self.ground_heights[index]
			pyxel.blt(x * 8 - int(camera) % 8, ground_y, 2, 0, 3 * 16, 8, 8, 0)
#			pyxel.rect(x * 8 - (camera) % 8, ground_y, 8, 8, 7)
		# プレイヤー（○△）
		pyxel.blt(self.player_x - int(camera) - 2, self.player_y - 4 - 11, 2, self.player_type * 16, 0, 16, 16, 0)
#		pyxel.circ(self.player_x - camera, self.player_y - 4, 2, 8)
#		pyxel.tri(
#			self.player_x - camera - 3, self.player_y,
#			self.player_x - camera + 3, self.player_y,
#			self.player_x - amera, self.player_y - 3, 9
#		)

		self.put_strings(0, 0, "DISTANCE")
		self.put_numd((self.player_x), 10);
		self.put_strings(9, 0, self.str_temp);
#		self.put_strings(0, 1, "VY")
#		self.put_numd((abs(self.player_vy * 10)), 10);
#		self.put_strings(9, 1, self.str_temp);


Game()

#yokoscroll.py by m@3 with Grok
