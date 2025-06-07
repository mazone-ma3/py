import pyxel
import random
import math
import csv
import time

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

#自機弾クラス
class PlayerBullet:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.w = 4
		self.h = 4
		self.speed = 6

	def update(self):
		self.y -= self.speed

	def draw(self):
		pyxel.blt(self.x, self.y, 2, 0, 16, 8, 8, 0)
#		pyxel.rect(self.x, self.y, self.w, self.h, 13)
#		pyxel.rectb(self.x, self.y, self.w, self.h, 0)


#敵弾クラス
class EnemyBullet:
	def __init__(self, x, y, dx, dy, speed):
		self.x = x
		self.y = y
		self.w = 2
		self.h = 2
		self.dx = dx
		self.dy = dy
		self.speed = speed

	def update(self):
		self.x += self.dx * self.speed
		self.y += self.dy * self.speed

	def draw(self):
		pyxel.blt(self.x, self.y, 2, 8, 16, 8, 8, 0)
#		pyxel.rect(self.x, self.y, self.w, self.h, 8)
#		pyxel.rectb(self.x, self.y, self.w, self.h, 0)


# 敵クラス
class Enemy:
	def __init__(self, x, y, player_x, player_y, hp, type, chr, speed):
		self.x = x
		self.y = y
		self.speed = speed
		self.shoot_timer = 0
		self.hp = hp
		self.type = type
		self.dmgtime = 0

		# キャラデータを変換
		if(type == "PAT_TEKI3"):
			pat = 4
		elif(type == "PAT_TEKI2"):
			pat = 3
		elif(type == "PAT_TEKI4"):
			pat = 5
		elif(type == "PAT_BOSS1"):
			pat = 0
		else:
			pat = 0

		self.pat = pat

		self.chr = chr

		self.dmg = False

	def update(self, player_x, player_y, enemy_bullets, shot_c):
		self.y += self.speed
		self.shoot_timer += 1

		if(self.chr == 0):
			if(self.dmgtime == 0):
				self.pat = 0
			elif(self.dmgtime ==5):
				self.pat = 1
			elif(self.dmgtime ==10):
				self.pat = 2
#			elif(self.dmgtime ==13):
			elif(self.dmgtime ==15):
				self.hp = 0


		if self.shoot_timer >= shot_c: #(6 << 3): #30:
			player_center_x = player_x + 8
			player_center_y = player_y + 8
			enemy_center_x = self.x + 8
			enemy_center_y = self.y + 8
			dx = player_center_x - enemy_center_x
			dy = player_center_y - enemy_center_y
			dist = math.sqrt(dx**2 + dy**2)
			if dist > 0:
				dx /= dist
				dy /= dist
				enemy_bullets.append(EnemyBullet(enemy_center_x, enemy_center_y, dx, dy, 1))
			self.shoot_timer = 0


	def draw(self):
		if(self.dmg == True):
			for i in range(1,15):
				pyxel.pal(i,8)
		pyxel.blt(self.x, self.y, 2, self.pat * 16, 32, 16, 16, 0) #14)
		pyxel.pal()
#		self.dmg = False

# ゲームクラス#################################################################

class App:
	def __init__(self):
		pyxel.init(256, 256, fps=60, title="Core Crashers")
		pyxel.load("cc.pyxres")

		self.schedule = self.load_schedule('cc.csv')
		self.schedule_index = 0
		self.current_time = 0
		self.message = ""
		self.message_x = 0
		self.message_y = 0
		self.stage = 0

		self.old_colors = pyxel.colors.to_list()
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


	# スケジュールデータを読み込む
	def load_schedule(self, file_path):
		schedule = []
		with open(file_path, mode='r', encoding='utf-8') as file:
			reader = csv.DictReader(file)
			for row in reader:
				schedule.append({
#					'time': float(row['time']),
					'event_type': row['event_type'],
					'event_0' : row['event_0'],
					'event_1' : row['event_1'],
					'event_2' : row['event_2'],
					'event_3' : row['event_3'],
					'event_4' : row['event_4'],
					'event_5' : row['event_5'],
					'event_6' : row['event_6'],
					'event_7' : row['event_7'],
#					'details': row['details']
				})
		return schedule #sorted(schedule, key=lambda x: x['time'])  # 時間順にソート

	# イベントを処理する関数
	def process_event(self, event):
#		print(f"Time: {event['time']}s, Event: {event['event_type']}, Details: {event['details']}")

		message = "                 ","     WARNING     ","STAGE "

		print(f"Event: {event['event_type']}, 0: {event['event_0']}, 1: {event['event_1']}, 2: {event['event_2']}, 3: {event['event_3']} ")

		com = event['event_type']
		self.com = com
		if(com == "COM_WAITCOUNT"):
			count = event['event_0']
			print(f"時間待ち {count}カウント")
			self.current_time = int(count)
			print(self.current_time)

		elif(com == "COM_TKALLDEL"):
			print(f"敵消去待ち")
			self.current_time = 1
		elif(com == "COM_TKAPPEND"):
			print(f"敵追加")
			type = (event['event_0'])
			chr = int(event['event_1'])
			x = int(event['event_2'])*256/144-16
			y = int(event['event_3'])-16
			hp = int(event['event_4'])
			self.enemies.append(Enemy(x, y, self.player_x, self.player_y, hp, type, chr, 1.5))
		elif(com == "COM_BGMCHANGE"):
			print(f"曲変更")
		elif(com == "COM_BGMFADEOUT"):
			print(f"曲終了")
		elif(com == "COM_PUTMESSAGE"):
			a = event['event_2'].encode("UTF-8")
			x = int(event['event_0'])
			y = int(event['event_1'])
			b = int(event['event_2'])
			print(f"メッセージ X={x} Y={y} {message[int(b)]}")
			self.message_x = x
			self.message_y = y
			self.message = message[int(b)]
		elif(com == "COM_STAGEADD"):
			if(self.stage < 99):
				self.stage = self.stage + 1
			x = int(event['event_0'])
			y = int(event['event_1'])
			self.message = message[2] + str(self.stage)
			self.message_x = x
			self.message_y = y
			self.my_hp = 7
			self.shot_c = self.shot_c / 2

			print(f"次のステージへ")
		elif(com == "COM_END"):
			self.current_time = 1
			self.schedule_index = -1
			print(f"終了")
		elif(com == "COM_SE"):
			x = int(event['event_0'])
			pyxel.play(2,15,0,False,True)
			print(f"SE再生 {x}")
		elif(com == "COM_BGPALFADEOUT"):
			print(f"画面フェードアウト")
		elif(com == "COM_JIKIMOVE"):
			print(f"自機移動")
		elif(com == "COM_DUMMY"):
			self.current_time = 1
			print(f"ダミー")

	# 文字列表示
	def put_strings(self, y, x, str):
		y = 28-y
		chr = str.encode("UTF-8")
		for i in range(len(str)):
			a = chr[i]
			if(a < 0x30):
				a = 0x40
			a = a - 0x30
			pyxel.blt((x + i) * 8, y * 8, 1, (a % 16) * 8, int(a / 16) * 8, 8, 8, 0)

	# タイトル表示
	def put_title(self):
		self.put_strings(9, 14, "START")
		self.put_strings(7, 14, "EXIT")
		self.put_strings(4, 10, "      ij k   ")
		self.put_strings(3, 10, "a2025 bcdefgh")
		self.score_displayall()
		self.hiscore_display()

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
#			self.str_temp[i] = k.decode(UTF-8)
#			j /= 10
#		self.str_temp[digit] = '\0'
#		k = str(j).encode('UTF-8')
		self.str_temp = l.decode("UTF-8")

	# スコア表示
	def score_display(self):
		self.put_numd(self.score, 8)
		self.put_strings(28, 2 + 6, self.str_temp)
		if(self.score >= self.hiscore):
			if((self.score % 10) == 0):
				self.hiscore = self.score
				self.put_strings(28, 0, "HI")
		else:
			self.put_strings(28, 0, "  ")

	# スコア全表示
	def score_displayall(self):
		self.put_strings(28, 2, "SCORE")
		self.score_display()

	# ハイスコア表示
	def hiscore_display(self):
		if(self.score > self.hiscore):
			if((self.score % 10) == 0):
				self.hiscore = self.score

		self.put_numd(self.hiscore, 8)

		self.put_strings(13, 10, "HIGH")
		self.put_strings(13, 10 + 5, self.str_temp)

	# シールドゲージ表示
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
#				str_temp[j++] = ' '
#		str_temp[j] = '\0'

		self.put_strings(-3, 7, str_temp)

#		self.my_hp_flag = TRUE

	# パレット設定
	def changepal(self, value):
		for palno in range(16):
			r = (self.old_colors[palno] >> 16) % 256
			g = (self.old_colors[palno] >> 8) % 256
			b = (self.old_colors[palno]) % 256

#			pal[k] = org_pal[j][k] + value
			if(value >= 0):
				r2  = int(r * ((255 - value)) / 255)
				g2  = int(g * ((255 - value)) / 255)
				b2  = int(b * ((255 - value)) / 255)
			else:
				r2  = int(r - value)
				if(r2 < 0):
					r2 = 0
				if(r2 > 255):
					r2 = 255
				g2  = int(g - value)
				if(g2 < 0):
					g2 = 0
				if(g2 > 255):
					g2 = 255
				b2  = int(b - value)
				if(b2 < 0):
					b2 = 0
				if(b2 > 255):
					b2 = 255

			pyxel.colors[palno] =((r2) << 16) | (((g2) << 8)) | (( b2))

	# データ初期化 ############################################################
	def initdata(self):
		self.player_x = 128 - 16
		self.player_y = 120 #- 16

		self.player_xx = 0
		self.player_yy = 0
		self.player_type = 0

		self.player_bullets = []
		self.enemies = []
		self.enemy_bullets = []

		self.score = 0
#		self.game_over = True

		self.stage = 0
		self.schedule_index = 0
		self.current_time = 0
		self.com = "COM_DUMMY"
		self.my_hp = 7
		self.my_dmg = False
		self.mypal_dmgtime = 0

		self.shot_c = 6 << 4 #3

	# メインループ
	def update(self):
		if pyxel.btnp(pyxel.KEY_ESCAPE):
# or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
			pyxel.quit()

		if self.scene == "GAMEOVER":
#			self.changepal(self.colorvalue)
			self.colorvalue -= 1
			if(self.colorvalue < -255):
				self.colorvalue = 255
				self.scene = "OPENING"
				pyxel.stop()

		elif self.scene == "OPENING":
			self.colorvalue = self.colorvalue - 1
			if(self.colorvalue == 0):
				self.scene = "TITLE"
#			self.changepal(self.colorvalue)

		elif self.scene == "TITLE":
			if pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START): # or pyxel.btnv(GAMEPAD1_AXIS_TRIGGERLEFT) != 0:
				self.initdata()
				self.logox = 0
				self.scene = "DEMO"
				pyxel.playm(0, 0,True)

		elif self.scene == "PAUSE":

			if pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B):
				self.scene = "GAME"
			elif pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
				self.scene = "OPENING"
				self.colorvalue = 255
#				self.changepal(self.colorvalue)
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

				if(self.player_xx > 0):
					self.player_type = 1
				elif(self.player_xx < 0):
					self.player_type = 2
				else:
					self.player_type = 0

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


				# 敵の更新
				for enemy in self.enemies[:]:
					enemy.update(self.player_x, self.player_y, self.enemy_bullets, self.shot_c)
					if enemy.y > 256:
						self.enemies.remove(enemy)

				# 敵の弾更新
				for bullet in self.enemy_bullets[:]:
					bullet.update()
					if bullet.y > 256 or bullet.y < 0 or bullet.x < 0 or bullet.x > 256:
						self.enemy_bullets.remove(bullet)

				# 当たり判定（プレイヤーの弾と敵）
				for enemy in self.enemies[:]:
					if(enemy.hp > 2):
						for bullet in self.player_bullets[:]:
							if (enemy.x < bullet.x + bullet.w and
								enemy.x + 16 > bullet.x and
									enemy.y < bullet.y + bullet.h and
									enemy.y + 16 > bullet.y):

								enemy.hp = enemy.hp - 1
								self.score += 10
								enemy.dmgtime = 1
								enemy.dmg = True
								self.player_bullets.remove(bullet)
								break

				for enemy in self.enemies[:]:
					# 敵消滅→爆発パターンへ
					if(enemy.hp == 0):
						self.enemies.remove(enemy)
						break
					elif(enemy.hp == 2):
#						self.enemies.remove(enemy)
						enemy.hp = 1
						self.score += 100
						pyxel.play(3,16,0,False,True)
						enemy.dmg = False
						enemy.chr = 0
						enemy.type = "TEKI_BOMB"

						break
					elif(enemy.dmgtime > 0):
						enemy.dmgtime = enemy.dmgtime + 1
						if(enemy.dmgtime > 3):
#							enemy.hp = 0
							enemy.dmg = False
#						else:
#							enemy.hp = 0

				if(self.mypal_dmgtime == 0):
					# 当たり判定（プレイヤーと敵）
					for enemy in self.enemies[:]:
						if (enemy.x < self.player_x + 9+1 and
							enemy.x + 16 > self.player_x+9 and
							enemy.y < self.player_y + 9+1 and
							enemy.y + 16 > self.player_y+9):
							self.my_dmg = True
#							pyxel.play(3,16,0,False,True)
#							if(self.mypal_dmgtime == 0):
#							self.my_hp = self.my_hp - 1

					# 当たり判定（プレイヤーと敵の弾）
					for bullet  in self.enemy_bullets[:]:
						if (self.player_x < bullet.x + bullet.w and
							self.player_x + 16 > bullet.x and
							self.player_y < bullet.y + bullet.h and
							self.player_y + 16 > bullet.y):
							self.enemy_bullets.remove(bullet)
							self.my_dmg = True
#							self.my_hp = self.my_hp - 1
#							pyxel.play(3,16,0,False,True)

					if(self.my_dmg == True):
						pyxel.play(3,16,0,False,True)
						self.mypal_dmgtime = 12 #DMGTIME * 4;
						self.my_dmg = False
						self.my_hp = self.my_hp - 1

						if(self.my_hp < 0):
							self.scene = "GAMEOVER" #game_over = True
							self.colorvalue = 0

#				(self.mypal_dmgtime > 0):
				else:
					self.mypal_dmgtime = self.mypal_dmgtime - 1
#					if(self.mypal_dmgtime <= 0):
#						self.my_dmg = False


				self.do_schedule()

	def	do_schedule(self):
		# スケジュール処理実行
		while(1):
			if(self.current_time != 0):
#				if(self.current_time > 0):
#					com = self.schedule[self.schedule_index].event['event_type']
				if(self.com == "COM_WAITCOUNT"):
					self.current_time = self.current_time - 1
					return
				elif(self.com == "COM_TKALLDEL"):
#					print(len(self.enemies))
					if(len(self.enemies[:]) == 0):
						self.current_time = 0
					return
				elif(self.com == "COM_DUMMY"):
					return
				elif(self.com == "COM_END"):
					self.current_time = self.current_time - 1

			self.event = self.schedule[self.schedule_index]
#			self.com = event.
			self.process_event(self.event)
			self.schedule_index = self.schedule_index + 1
			if self.schedule_index >= len(self.schedule):
				self.schedule_index = 0

			print(self.current_time)

#			if(self.current_time > 0):
#				self.current_time = self.current_time - 1

	# 画面の更新
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

			self.changepal(self.colorvalue)
			pyxel.blt(128 - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)

		elif self.scene == "DEMO":
			# タイトルロゴアニメーション
			self.score_displayall()

			if(self.logox % 8):
				pyxel.blt(128 + self.logox - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)
			else:
				pyxel.blt(128 - self.logox - 48 - 16, 48 - 16, 0, 0, 0, 128, 64, 0)

		elif self.scene == "GAME" or self.scene == "PAUSE" or self.scene == "GAMEOVER":
			# 敵の弾描画
			for bullet in self.enemy_bullets:
				bullet.draw()

			# 敵の描画
			for enemy in self.enemies:
				enemy.draw()

			# プレイヤーの弾描画
			for bullet in self.player_bullets:
				bullet.draw()

			# 自機描画
			if(self.mypal_dmgtime != 0  or self.scene == "GAMEOVER"):
				for i in range(1,15):
					pyxel.pal(i,15)

			pyxel.blt(self.player_x, self.player_y, 2, self.player_type * 24, 0, 24, 16, 0)
			pyxel.pal()
#			self.my_dmg = False

#			pyxel.tri(self.player_x, self.player_y, 
#					 self.player_x + 8, self.player_y + 8, 
#					 self.player_x - 8, self.player_y + 8, 13)
#			pyxel.rect(self.player_x - 2, self.player_y + 8, 4, 4, 5)

			# 一時停止表示
			if self.scene == "PAUSE":
#				pyxel.text(110, 120, "PAUSE", 7)
				self.put_strings(14, 13, "PAUSE")

			# イベント文字表示
			self.put_strings(self.message_x, self.message_y, self.message)

			# 各種ゲージ表示
			self.put_strings(-3, 0, "SHIELD")
			self.score_displayall()
			self.put_my_hp_dmg()

		if(self.scene == "GAMEOVER"):
			self.put_strings(14, 10, " GAME OVER ")
#			self.changepal(0)
			self.changepal(self.colorvalue)

App()
