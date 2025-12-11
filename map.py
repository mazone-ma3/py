import pyxel

X_SIZE = 16
Y_SIZE = 16

MAP_X_SIZE = 256
MAP_Y_SIZE = 256 - 16

OFS_X = 16
OFS_Y = 16

chr_tbl = [
		[0, 1, 0 + 16, 1 + 16],
		[2, 3, 2 + 16, 3 + 16],
		[4, 5, 4 + 16, 5 + 16],
		[6, 7, 6 + 16, 7 + 16],
		[8, 9, 8 + 16, 9 + 16],
		[10, 11, 10 + 16, 11 + 16],
		[12, 13, 12 + 16, 13 + 16],
		[14, 15, 14 + 16, 15 + 16],
]

class Game:

	def __init__(self):
		pyxel.init(256, 212, fps=30, title="map")
		pyxel.load("map.pyxres")

		f = open('ELMSTMAP.MDT', 'rb')
		self.mapdata = f.read()
		f.close()

		self.x = 165;
		self.y = 30;

		self.old_x = self.x
		self.old_y = self.y

		self.my_x = int((X_SIZE - 2) / 2)
		self.my_y = int((Y_SIZE - 2) / 2)

		self.map = [[0 for j in range(X_SIZE + 2)] for i in range(Y_SIZE + 2)]

		self.dir = 2
		self.dir2 = 0

		pyxel.run(self.update, self.draw)


	def update(self):
		self.player_xx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)) - (pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT))

		self.player_yy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)) - (pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP))

		if(self.y > 0 and self.player_yy < 0):
			self.y += self.player_yy;
			self.dir = 0

		if(self.x < MAP_X_SIZE - X_SIZE and self.player_xx > 0):
			self.x += self.player_xx;
			self.dir = 1

		if(self.y < MAP_Y_SIZE - Y_SIZE and self.player_yy > 0):
			self.y += self.player_yy;
			self.dir = 2

		if(self.x > 0 and self.player_xx < 0):
			self.x += self.player_xx;
			self.dir = 3

		if(self.old_x != self.x) or (self.old_y != self.y):
			self.dir2 = 1 - self.dir2

		self.old_x = self.x
		self.old_y = self.y


	def draw(self):
		pyxel.blt(0, 0, 0, 0, 0, 256, 212, 0)

		xx = self.x % 2;
		yy = self.y % 2;

		for y in range(0, int(Y_SIZE / 2) + 1):
			for x in range(0, int(X_SIZE / 2) + 1):
				chr = self.mapdata[7 + x + int(self.x / 2) + (y + int(self.y / 2)) * 128]
				chr_x = chr % 16
				chr_y = int(chr / 16)
				chr = chr_x * 16 + chr_y
				data = 7 + 0x3c00 + chr * 4
				self.map[x * 2][y * 2] = self.mapdata[data]
				self.map[x * 2 + 1][y * 2] = self.mapdata[data+ 1]
				self.map[x * 2][y * 2 + 1] = self.mapdata[data + 2]
				self.map[x * 2 + 1][y * 2 + 1] = self.mapdata[data + 3]

		for y in range(0, Y_SIZE):
			for x in range(0, X_SIZE):
				chr = self.map[x + xx][y + yy]
				chr_x = chr % 16
				chr_y = int(chr / 16)
				pyxel.blt(x * 8 + OFS_X, y * 8 + OFS_Y, 1, chr_x * 8, (chr_y) * 8, 8, 8, 0)

		no2 = chr_tbl[self.dir * 2 + self.dir2][0]
#[(i - CHR_X) + (j - CHR_Y) * 2];

		pyxel.blt(self.my_x * 8 + OFS_X, self.my_y * 8 + OFS_Y, 1, 128 + no2 * 8, 0, 16, 16, 0)

Game()

#map.py by m@3 2025
