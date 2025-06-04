import pyxel
import random

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

class Game:
	def __init__(self):
		pyxel.init(256, 256, fps=60, title="Core Crashers")
		pyxel.load("cc.pyxres")

		self.scene = "TITLE"
		self.starnums = 64

		# 星の初期化
		self.stars = [Star(i * (256 / self.starnums)) for i in range(self.starnums)]
		self.trgcount = 0

		self.player_bullets = []
		self.enemies = []
		self.enemy_bullets = []

		pyxel.run(self.update, self.draw)

	def initdata(self):
		self.player_x = 128 - 16
		self.player_y = 120 - 16

		self.player_xx = 0
		self.player_yy = 0

		self.score = 0
		self.game_over = True

	def update(self):
		if pyxel.btnp(pyxel.KEY_ESCAPE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
			pyxel.quit()
		if self.scene == "TITLE":
			if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): # or pyxel.btnv(GAMEPAD1_AXIS_TRIGGERLEFT) != 0:
				self.initdata()
				self.scene = "GAME"
		elif self.scene == "GAME":
			# 自機移動
			self.player_xx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))
 #  or (pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) > 0 ))
 # or (pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTX) < 0 ))
			self.player_yy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))
# or (pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) > 0 ))
#  or (pyxel.btnv(pyxel.GAMEPAD1_AXIS_LEFTY) < 0 ))

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

			# 自弾発射
#			if((pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_A)) and ((max_myshot - trgnum) >= 2))):
#				if(!trgcount):
#					trgcount = 5

#					if(myshot_free)

		# プレイヤーの弾発射
		if(self.trgcount > 0):
			self.trgcount = self.trgcount - 1
		if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
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
		if self.scene == "TITLE":

			# 星の更新
			for star in self.stars:
				star.update()

			for star in self.stars:
				star.draw()

			# タイトル画面
			pyxel.text(100, 160, "CORE CRASHERS", 7)
			pyxel.text(96, 200, "Press SPACE KEY", 7)

			pyxel.blt(128 - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)

		elif self.scene == "GAME":
			# 星の更新
			for star in self.stars:
				star.update()

			for star in self.stars:
				star.draw()

			# 自機
			pyxel.blt(self.player_x, self.player_y, 2, 0, 0, 24, 16, 0)

#			pyxel.tri(self.player_x, self.player_y, 
#					 self.player_x + 8, self.player_y + 8, 
#					 self.player_x - 8, self.player_y + 8, 13)
#			pyxel.rect(self.player_x - 2, self.player_y + 8, 4, 4, 5)

		# プレイヤーの弾描画
		for bullet in self.player_bullets:
			bullet.draw()


Game()
