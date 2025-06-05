import pyxel
import random
import math

class Star:
	def __init__(self, i):
		self.reset(i)

	def reset(self, i):
		self.x = i;  # x座標
		self.y = random.randint(0, 256)  # ランダムなy座標（画面全体に初期配置）
		self.speed = random.uniform(1, 3)  # 速度（1-3ピクセル/フレーム）
		self.size = 1 #random.choice([1, 2])  # 星のサイズ（1x1）
		self.color = random.randint(0, 16)

	def update(self):
		self.y += self.speed  # 下に移動
		if self.y > 256:  # 画面外に出たら上部でリスポーン
			self.y = -self.size

	def draw(self):
#		pyxel.rect(self.x, self.y, self.size, self.size, self.color)  # 星
		pyxel.pset(self.x, self.y, self.color)  # 星

class PlayerBullet:
	def __init__(self, x, y):
		self.x = x
		self.y = y
#		self.w = 3
#		self.h = 3
		self.speed = 6

	def update(self):
		self.y -= self.speed

	def draw(self):
		pyxel.blt(self.x, self.y, 2, 0, 16, 8, 8, 0)
#		pyxel.rect(self.x, self.y, self.w, self.h, 13)
#		pyxel.rectb(self.x, self.y, self.w, self.h, 0)

# ゲームループ

class App:
	def __init__(self):
		pyxel.init(256, 256, fps=60, title="Core Crashers")
		pyxel.load("cc.pyxres")
		self.old_colors = pyxel.colors.to_list();
		self.colorvalue = 255
		self.changepal(self.colorvalue)

		self.scene = "OPENING"
		self.starnums = 64

		self.str_temp = ""
		self.score = 0
		self.hiscore = 5000

		self.my_hp = 7

# pyxel.colors.from_list([0x111111, 0x222222, 0x333333]); pyxel.colors[15] = 0x112233

		# 星の初期化
		self.stars = [Star(i * (256 / self.starnums)) for i in range(self.starnums)]
		self.trgcount = 0


		pyxel.run(self.update, self.draw)

	def put_strings(self, y, x, str):
		y = 28-y
		chr = str.encode("UTF-8")
		for i in range(len(str)):
			a = chr[i]
			if(a < 0x30):
				a = 0x40
			a = a - 0x30
			pyxel.blt((x + i) * 8, y * 8, 1, (a % 16) * 8, int(a / 16) * 8, 8, 8, 0)

	def put_title(self):
		self.put_strings(9, 14, "START")
		self.put_strings(7, 14, "EXIT")
		self.put_strings(4, 10, "      ij k   ")
		self.put_strings(3, 10, "a2025 bcdefgh")
		self.score_displayall()
		self.hiscore_display()

	def put_numd(self, j, digit):
		i = 0 #digit
		self.str_temp = ""
		k = 0
		l = b""
		while (i < digit):
			i = i + 1
			k = int(j / (10**(digit-i))) % 10
			l += str(k).encode('UTF-8')
#			self.str_temp[i] = k.decode(UTF-8)
#			j /= 10
#		self.str_temp[digit] = '\0';
#		k = str(j).encode('UTF-8')
		self.str_temp = l.decode("UTF-8")

	def score_display(self):
		self.put_numd(self.score, 8)
		self.put_strings(28, 2 + 6, self.str_temp)
		if(self.score >= self.hiscore):
			if((self.score % 10) == 0):
				self.hiscore = self.score
				self.put_strings(28, 0, "HI")
		else:
			self.put_strings(28, 0, "  ")

	def score_displayall(self):
		self.put_strings(28, 2, "SCORE")
		self.score_display()

	def hiscore_display(self):
		if(self.score > self.hiscore):
			if((self.score % 10) == 0):
				self.hiscore = self.score

		self.put_numd(self.hiscore, 8)

		self.put_strings(13, 10, "HIGH")
		self.put_strings(13, 10 + 5, self.str_temp)

	def put_my_hp_dmg(self):
		j = 0
		str_temp = ""
		for i in range(self.my_hp):
			++j
			str_temp += '`'
		if(self.my_hp < 10):
			for i in range(self.my_hp, 10): #(i = my_hp; i < HP_MAX; i++)
				++j
				str_temp += ' '
#				str_temp[j++] = ' ';
#		str_temp[j] = '\0';

		self.put_strings(-3, 7, str_temp);

#		self.my_hp_flag = TRUE;


	def changepal(self, value):
		for palno in range(16):
			r = (self.old_colors[palno] >> 16) % 256
			g = (self.old_colors[palno] >> 8) % 256
			b = (self.old_colors[palno]) % 256

#			pal[k] = org_pal[j][k] + value;
			r2  = int(r * ((255 - value)) / 255);
			g2  = int(g * ((255 - value)) / 255);
			b2  = int(b * ((255 - value)) / 255);

			pyxel.colors[palno] =((r2) << 16) | (((g2) << 8)) | (( b2))

	def initdata(self):
		self.player_x = 128 - 16
		self.player_y = 120 #- 16

		self.player_xx = 0
		self.player_yy = 0

		self.player_bullets = []
		self.enemies = []
		self.enemy_bullets = []

		self.score = 0
		self.game_over = True

#		self.value = 0

	def update(self):
		if pyxel.btnp(pyxel.KEY_ESCAPE):
# or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
			pyxel.quit()

		if self.scene == "OPENING":
			self.colorvalue = self.colorvalue - 1
			if(self.colorvalue == 0):
				self.scene = "TITLE"
			self.changepal(self.colorvalue)

		if self.scene == "TITLE":
			if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): # or pyxel.btnv(GAMEPAD1_AXIS_TRIGGERLEFT) != 0:
				self.initdata()
				self.logox = 0;
				self.scene = "DEMO"
				pyxel.playm(0, 0,True)

		elif self.scene == "PAUSE":

			if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
				self.scene = "GAME"
			elif pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
				self.scene = "OPENING"
				self.colorvalue = 255
				self.changepal(self.colorvalue)
				pyxel.stop()

		elif self.scene == "DEMO":
				self.logox = self.logox + 4
				if(self.logox == 256):
					self.scene = "GAME"

		elif self.scene == "GAME":

			if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
				self.scene = "PAUSE"
			else:

				# 自機移動
				self.player_xx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
				self.player_yy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))

				if ((self.player_xx == 0) or (self.player_yy == 0)):
					self.player_xx *= 3
					self.player_yy *= 3
				else:
					self.player_xx *= 2
					self.player_yy *= 2

				self.player_x += self.player_xx
				self.player_x = max(0, min(self.player_x, 256 - 24 + 4))

				self.player_y += self.player_yy
				self.player_y = max(0, min(self.player_y, 256 - 16))

				# プレイヤーの弾発射
				if(self.trgcount > 0):
					self.trgcount = self.trgcount - 1
				if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
					if(self.trgcount == 0):
						self.trgcount = 5
						self.player_bullets.append(PlayerBullet(self.player_x + 1, self.player_y + 4))
						self.player_bullets.append(PlayerBullet(self.player_x + 13, self.player_y + 4))

				# プレイヤーの弾更新
				for bullet in self.player_bullets[:]:
					bullet.update()
					if bullet.y < -8:
						self.player_bullets.remove(bullet)


	def draw(self):
		pyxel.cls(0)

		# 星の更新
		if self.scene != "PAUSE":
			for star in self.stars:
				star.update()

		for star in self.stars:
			star.draw()

		if self.scene == "TITLE" or self.scene == "OPENING":

			# タイトル画面
			if self.scene == "TITLE":
#				pyxel.text(100, 160, "Press SPACE KEY", 7)
#				pyxel.text(100, 200, "(c) ma-Zone 2025", 7)
				self.put_title()
				x = 1
				self.put_strings(7 + x * 2, 11, "?")

			pyxel.blt(128 - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)

		elif self.scene == "DEMO":
			self.score_displayall()

			if(self.logox % 8):
				pyxel.blt(128 + self.logox - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)
			else:
				pyxel.blt(128 - self.logox - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)

		elif self.scene == "GAME" or self.scene == "PAUSE":

			# 自機
			pyxel.blt(self.player_x, self.player_y, 2, 0, 0, 24, 16, 0)

#			pyxel.tri(self.player_x, self.player_y, 
#					 self.player_x + 8, self.player_y + 8, 
#					 self.player_x - 8, self.player_y + 8, 13)
#			pyxel.rect(self.player_x - 2, self.player_y + 8, 4, 4, 5)

		# プレイヤーの弾描画
			for bullet in self.player_bullets:
				bullet.draw()

			if self.scene == "PAUSE":
#				pyxel.text(110, 120, "PAUSE", 7)
				self.put_strings(14, 13, "PAUSE")

			self.put_strings(-3, 0, "SHIELD");
			self.score_displayall()
			self.put_my_hp_dmg()

App()
