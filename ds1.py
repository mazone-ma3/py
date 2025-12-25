# gravity_rpg_fixed.py
import pyxel

# 10x10ステージ（固定画面用）
LEVEL = [
    "##########",
    "#P.......#",
    "#.###S...#",
    "#.S...B..#",
    "#.###.####",
    "#.S......#",
    "#.###S####",
    "#........#",
    "#........#",
    "#####G####"
]

class GravityRpgFixed:
    def __init__(self):
        pyxel.init(160, 160, title="Dragon Sword 1 Remake")
        self.tile_size = 16
        self.map_w = len(LEVEL[0])
        self.map_h = len(LEVEL)
        self.player_x = self.player_y = 0
        self.gravity_panel = None
        self.panels = []
        self.goal = (0, 0)
        self.cleared = False
        self.mode = "puzzle"
        # RPGステータス
        self.player_hp = 20
        self.player_atk = 5
        self.enemy = None
        self.battle_msg = ""
        
        # マップ解析
        for y in range(self.map_h):
            for x in range(self.map_w):
                c = LEVEL[y][x]
                if c == "P":
                    self.player_x, self.player_y = x, y
                elif c == "B":
                    self.gravity_panel = [x, y]
                elif c == "S":
                    self.panels.append([x, y])
                elif c == "G":
                    self.goal = (x, y)
        
        pyxel.run(self.update, self.draw)

    def can_move(self, x, y):
        if not (0 <= x < self.map_w and 0 <= y < self.map_h):
            return False
        if LEVEL[y][x] == "#":
            return False
        if self.gravity_panel and self.gravity_panel == [x, y]:
            return False
        for p in self.panels:
            if p == [x, y]:
                return False
        return True

    def update(self):
        if self.cleared:
            return
        
        if self.mode == "battle":
            self.update_battle()
            return
        
        # 重力パネル落下
        if self.gravity_panel:
            gx, gy = self.gravity_panel
            if gy + 1 < self.map_h and self.can_move(gx, gy + 1):
                self.gravity_panel[1] += 1
                if self.gravity_panel == list(self.goal):
                    self.cleared = True
        
        # プレイヤー入力
        dx, dy = 0, 0
        if pyxel.btnp(pyxel.KEY_LEFT):  dx = -1
        if pyxel.btnp(pyxel.KEY_RIGHT): dx = 1
        if pyxel.btnp(pyxel.KEY_UP):    dy = -1
        if pyxel.btnp(pyxel.KEY_DOWN):  dy = 1
        
        if dx or dy:
            nx, ny = self.player_x + dx, self.player_y + dy
            # エンカウント（5%）
            if pyxel.rndi(0, 100) < 5:
                self.mode = "battle"
                self.enemy = [10, 3, "Slime"]
                self.battle_msg = f"{self.enemy[2]} appeared!"
                return
            
            # 重力パネル押す
            if self.gravity_panel and self.gravity_panel == [nx, ny]:
                gnx, gny = nx + dx, ny + dy
                if self.can_move(gnx, gny):
                    self.gravity_panel[0], self.gravity_panel[1] = gnx, gny
                    self.player_x, self.player_y = nx, ny
                return
            
            # 通常パネル押す
            for i, p in enumerate(self.panels):
                if p == [nx, ny]:
                    pnx, pny = nx + dx, ny + dy
                    if self.can_move(pnx, pny):
                        self.panels[i] = [pnx, pny]
                        self.player_x, self.player_y = nx, ny
                    return
            
            # 通常移動
            if self.can_move(nx, ny):
                self.player_x, self.player_y = nx, ny

    def update_battle(self):
        if pyxel.btnp(pyxel.KEY_A):  # 攻撃
            self.enemy[0] -= self.player_atk
            self.battle_msg = f"Hit {self.enemy[2]} for {self.player_atk} damage!"
            if self.enemy[0] <= 0:
                self.battle_msg = f"{self.enemy[2]} defeated!"
                self.mode = "puzzle"
                self.enemy = None
                return
            self.player_hp -= self.enemy[1]
            self.battle_msg += f"\n{self.enemy[2]} hits you for {self.enemy[1]} damage!"
            if self.player_hp <= 0:
                self.battle_msg = "Game Over..."
                self.cleared = True

    def draw(self):
        pyxel.cls(0)
        
        if self.mode == "battle":
            pyxel.rect(10, 10, 140, 100, 1)
            pyxel.text(20, 20, self.battle_msg, 7)
            pyxel.text(20, 90, f"HP: {self.player_hp}", 7)
            pyxel.text(20, 100, "A: Attack", 7)
            pyxel.rect(80, 40, 16, 16, 11)  # 敵スプライト
            return
        
        # パズル画面（固定）
        for y in range(self.map_h):
            for x in range(self.map_w):
                tx = x * self.tile_size
                ty = y * self.tile_size
                if LEVEL[y][x] == "#":
                    pyxel.rect(tx, ty, self.tile_size, self.tile_size, 1)
                else:
                    pyxel.rect(tx, ty, self.tile_size, self.tile_size, 7)
                if LEVEL[y][x] == "G":
                    pyxel.rect(tx + 4, ty + 4, 8, 8, 10)
        
        for p in self.panels:
            pyxel.rect(p[0]*self.tile_size + 2, p[1]*self.tile_size + 2, 12, 12, 9)
        
        if self.gravity_panel:
            gx, gy = self.gravity_panel
            pyxel.rect(gx*self.tile_size + 2, gy*self.tile_size + 2, 12, 12, 11)
        
        pyxel.rect(self.player_x*self.tile_size + 2, self.player_y*self.tile_size + 2, 12, 12, 8)
        
        if self.cleared:
            pyxel.text(60, 80, "STAGE CLEAR!!", 10)

GravityRpgFixed()