import pyxel
import random

PAT_JIKI_N = 0
PAT_JIKI_R = 1
PAT_JIKI_L = 2
PAT_JIKI_J = 3


class PlusTaker:
	def __init__(self):
		pyxel.init(160, 120, title="Plus Taker 2 Plus", fps=60)
		pyxel.mouse(False)
		pyxel.load("plustaker2p.pyxres")
		
		# サウンド定義 (c4までで安全)
		pyxel.sound(0).set("c3e3", "s", "64", "n", 10)	  # 射撃: ピコピコ
		pyxel.sound(1).set("g3c4e4", "t", "765", "f", 15)	# 撃破: ドンッ
		pyxel.sound(2).set("c4e4g4c4", "p", "7777", "n", 12) # Plus: キラキラ
		
		self.high_score = 5000
		self.reset_game()
		pyxel.run(self.update, self.draw)

	def reset_game(self):
		self.player_x = 80
		self.player_y = 9 * 8
		self.bullets = []
		self.enemies = []
		self.pluses = []
		self.score = 0
		self.combo = 0
		self.combo_timer = 0
		self.wave = 1
		self.kills = 0
		self.spawn_timer = 0
		self.game_over = False
		self.player_type = PAT_JIKI_N
		self.trgcount = 0
		self.num_enemies = 0
		self.enemycount = 0

	# 文字列表示
	def put_strings(self, x, y, str):
		chr = str.encode("UTF-8")
		for i in range(len(str)):
			a = chr[i]
			if(a < 0x30):
				a = 0x40
			a = a - 0x30
			pyxel.blt((x + i) * 8, y * 8, 1, (a % 16) * 8, int(a / 16) * 8, 8, 8, 0)

	def update(self):
		if self.score > self.high_score:
			self.high_score = self.score
		if self.game_over:
			if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
				self.reset_game()
			return

		# コンボタイマー
		self.combo_timer += 1
		if self.combo_timer > 60:
			self.combo = 0
			self.combo_timer = 0

		# 移動 (WASD/矢印)
		if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
			self.player_x = max(8, self.player_x - 3)
		if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
			self.player_x = min(152, self.player_x + 3)
		if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
			self.player_y = max(16, self.player_y - 3)
		if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
			self.player_y = min(104, self.player_y + 3)

		# 射撃
		if pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.KEY_Z)  or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
			if(self.trgcount > 0):
				self.trgcount = self.trgcount - 1
			elif(len(self.bullets) < 3):
				self.trgcount = 10
				self.bullets.append([self.player_x, self.player_y - 8])
				pyxel.play(0, 0)

		# 弾移動
		for b in self.bullets[:]:
			b[1] -= 5
			if b[1] < 0:
				self.bullets.remove(b)

		# 敵生成 (3体スタート)
		self.spawn_timer += 1
		spawn_interval = max(100 - self.wave * 8, 40)
		if self.spawn_timer > spawn_interval:
			self.spawn_timer = 0
			self.num_enemies = min(2 + self.wave, 6)  # wave1:3体, wave2:4体...
#			for _ in range(num_enemies):

		if(self.enemycount > 0):
			self.enemycount -= 1
		elif(self.num_enemies > 0):
			self.num_enemies -= 1
			self.enemycount = 16
			self.enemies.append([random.randint(10, 150), -10])

		# 敵移動 (waveで速く)
		enemy_speed = 1.5 + self.wave * 0.2
		for e in self.enemies[:]:
			e[1] += enemy_speed
			if e[1] > 120:
				self.enemies.remove(e)

		# 衝突: 弾 vs 敵
		for b in self.bullets[:]:
			for e in self.enemies[:]:
				if abs(b[0] - e[0]) < 12 and abs(b[1] - e[1]) < 12:
					self.bullets.remove(b)
					self.enemies.remove(e)
					self.pluses.append([e[0], e[1]])
					self.combo += 1
					self.kills += 1
					self.score += 20 * self.combo
					self.combo_timer = 0
					pyxel.play(1, 1)
					if self.kills % 5 == 0:
						self.wave += 1
					break

		# Plus移動&取得
		for p in self.pluses[:]:
			p[1] += 1.5
			if p[1] > 120:
				self.pluses.remove(p)
				self.combo_timer = 60  # 取り逃しで即リセット
			elif abs(p[0] - self.player_x) < 12 and abs(p[1] - self.player_y) < 12:
				self.pluses.remove(p)
				self.score += 50 * self.combo
				self.combo_timer = 0
				pyxel.play(2, 2)

		# ゲームオーバー (敵接触)
		for e in self.enemies:
			if abs(e[0] - self.player_x) < 16 and abs(e[1] - self.player_y) < 16:
				self.game_over = True

	def draw(self):
		pyxel.cls(1)


		# UI
#		pyxel.bltm(0, 0, 0, 0, 0, 256, 256, 0, 0, 1)
		for i in range(0, 10):
			pyxel.blt(i * 16, 10 * 8, 2, 8 * 16, 0, 16, 8, 0)

		if not self.game_over:
			if self.score < self.high_score:
				self.put_strings(4, 12, f"SCORE: {self.score:06d}") #, 7)
			else:
				self.put_strings(4, 12, f"HIGH:  {self.high_score:06d}") #, 7 if self.score < self.high_score else 11)
#			self.put_strings(4, 13, f"WAVE: {self.wave}") #, 9)
			if self.combo:
				self.put_strings(4, 14, f"COMBO: x{self.combo}") #, 11 if self.combo > 0 else 7)
#			pyxel.text(5, 110, "ARROW/WASD: MOVE  SPACE/Z: SHOOT  R:RETRY", 6)

		# プレイヤー (青三角)
#		pyxel.blt(self.player_x - 2, self.player_y - 4 - 11, 2, self.player_type * 16, 0, 16, 16, 0)
		pyxel.blt(self.player_x - 8, self.player_y - 8, 2, self.player_type * 16, 0, 16, 16, 0)
#		pyxel.tri(self.player_x-8, self.player_y+8, self.player_x, self.player_y-8, self.player_x+8, self.player_y+8, 12)

		# 弾 (白長方形)
		for b in self.bullets:
			pyxel.rect(b[0]-2, b[1]-4, 4, 8, 7)

		# 敵 (黄四角、waveで点滅?)
		for e in self.enemies:
			blink = 10 if (pyxel.frame_count + int(e[0])) % 20 < 10 else 11
			pyxel.rect(e[0]-8, e[1]-8, 16, 16, blink)

		# Plus (黄+、輝き)
		for p in self.pluses:
			glow = 10 + (pyxel.frame_count % 4)
#			pyxel.text(p[0]-4, p[1]-4, "+", glow)
			pyxel.blt(p[0] - 8, p[1] - 8, 2, self.player_type * 16, 0, 16, 16, 0)

		if self.game_over:
			self.put_strings(55, 5, "GAME OVER") #, pyxel.frame_count % 16 < 8 and 8 or 10)
			self.put_strings(3, 4, f"SCORE: {self.score:06d}") #, 7)
			self.put_strings(3, 6, f"HIGH:  {self.high_score:06d}") #, 7 if self.score < self.high_score else 11)
			self.put_strings(3, 8, f"WAVE REACHED: {self.wave}") #, 7)
			self.put_strings(2, 10, "PRESS R TO RETRY") #, 7)
#			return


PlusTaker()