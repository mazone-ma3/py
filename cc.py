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

# ゲームループ #################################################################

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
		if(com == "COM_WAITCOUNT"):
			count = event['event_0']
			print(f"時間待ち {count}カウント")
			self.current_time = int(count)
			print(self.current_time)

		elif(com == "COM_TKALLDEL"):
			print(f"敵消去待ち")
		elif(com == "COM_TKAPPEND"):
			print(f"敵追加")
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
			self.stage = self.stage + 1
			x = int(event['event_0'])
			y = int(event['event_1'])
			self.message = message[2] + str(self.stage)
			self.message_x = x
			self.message_y = y
			print(f"次のステージへ")
		elif(com == "COM_END"):
			self.schedule_index = -1
			print(f"終了")
		elif(com == "COM_SE"):
			x = int(event['event_0'])
			print(f"SE再生 {x}")
		elif(com == "COM_BGPALFADEOUT"):
			print(f"画面フェードアウト")
		elif(com == "COM_JIKIMOVE"):
			print(f"自機移動")


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

	# データ初期化
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

		self.stage = 0
		self.schedule_index = 0

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

				# スケジュール
				if(self.current_time == 0):
#				while self.schedule_index < len(self.schedule):
					if self.schedule_index < len(self.schedule): #and current_time >= schedule[schedule_index]['time']:
						self.process_event(self.schedule[self.schedule_index])
#						++self.schedule_index
						self.schedule_index = self.schedule_index + 1

					else:
						self.schedule_index = 0

				if(self.current_time > 0):
					self.current_time = self.current_time - 1
#					print(self.current_time)

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

			self.put_strings(self.message_x, self.message_y, self.message);

			self.put_strings(-3, 0, "SHIELD");
			self.score_displayall()
			self.put_my_hp_dmg()

App()
