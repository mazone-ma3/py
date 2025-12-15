import pyxel
import math

PLAYER_SIZE = 8
ENEMY_SIZE = 6
ITEM_SIZE = 8
MAX_ENEMIES = 4

class PlusTaker:
    def __init__(self):
        pyxel.init(128, 128, title="Plus Taker - Pyxel版", fps=30)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player_x = 64.0
        self.player_y = 100.0
        self.enemies = []
        self.items = []
        self.score = 0
        self.frame = 0

    def update(self):
        self.frame += 1

        # プレイヤー移動
        speed = 2.0
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x -= speed
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x += speed
        if pyxel.btn(pyxel.KEY_UP):
            self.player_y -= speed
        if pyxel.btn(pyxel.KEY_DOWN):
            self.player_y += speed

        # 画面境界
        self.player_x = max(PLAYER_SIZE / 2, min(128 - PLAYER_SIZE / 2, self.player_x))
        self.player_y = max(PLAYER_SIZE / 2, min(128 - PLAYER_SIZE / 2, self.player_y))

        # 敵生成 (60フレームに1回、30%確率)
        if len(self.enemies) < MAX_ENEMIES and self.frame % 60 == 0 and pyxel.rndi(0, 10) < 3:
            side = pyxel.rndi(0, 4)
            if side == 0:  # 左
                ex, ey = -ENEMY_SIZE, pyxel.rndi(0, 128)
            elif side == 1:  # 右
                ex, ey = 128 + ENEMY_SIZE, pyxel.rndi(0, 128)
            elif side == 2:  # 上
                ex, ey = pyxel.rndi(0, 128), -ENEMY_SIZE
            else:  # 下
                ex, ey = pyxel.rndi(0, 128), 128 + ENEMY_SIZE
            self.enemies.append([float(ex), float(ey)])

        # 敵更新 & 衝突
        for e in self.enemies[:]:
            dx = self.player_x - e[0]
            dy = self.player_y - e[1]
            dist = math.sqrt(dx * dx + dy * dy) + 1  # ゼロ除算回避
            e[0] += dx * 0.6 / dist  # 追尾速度調整
            e[1] += dy * 0.6 / dist

            # プレイヤー衝突
            if (abs(self.player_x - e[0]) < (PLAYER_SIZE + ENEMY_SIZE) / 2 and
                abs(self.player_y - e[1]) < (PLAYER_SIZE + ENEMY_SIZE) / 2):
                pyxel.quit()

        # アイテム生成 (90フレームに1回)
        if self.frame % 90 == 0:
            ix = pyxel.rndi(4, 124)
            iy = pyxel.rndi(4, 40)
            self.items.append([float(ix), float(iy)])

        # アイテム更新 & 収集
        for i in self.items[:]:
            i[1] += 0.8  # 下移動
            if i[1] > 128 + ITEM_SIZE:
                self.items.remove(i)
                continue

            # プレイヤー収集
            if (abs(self.player_x - i[0]) < ITEM_SIZE / 2 + PLAYER_SIZE / 2 and
                abs(self.player_y - i[1]) < ITEM_SIZE / 2 + PLAYER_SIZE / 2):
                self.score += 10
                self.items.remove(i)
                break

    def draw(self):
        # 虹グラデ背景
        for y in range(0, 128, 4):
            hue = (y // 4) % 16
            pyxel.rect(0, y, 128, 4, hue)

        # プレイヤー女の子
        pyxel.circ(self.player_x, self.player_y - 5, 3, 0)  # 頭影
        pyxel.circ(self.player_x, self.player_y - 5, 3, 7)  # 頭
        pyxel.rect(self.player_x - 3, self.player_y - 1, 6, 6, 9)  # 体
        pyxel.rect(self.player_x - 2, self.player_y + 4, 4, 4, 12)  # スカート

        # 敵 (点滅)
        for e in self.enemies:
            col = 8 + (self.frame // 5) % 8
            pyxel.circ(e[0], e[1], ENEMY_SIZE // 2, col)

        # +アイテム
        for i in self.items:
            pyxel.rect(i[0] - 3, i[1] - 1, 6, 2, 11)  # 横
            pyxel.rect(i[0] - 1, i[1] - 3, 2, 6, 11)  # 縦

        # UI
        pyxel.text(2, 2, f"Score:{self.score:4d}", 0)
        pyxel.text(2, 12, "Arrow Keys", 0)
        pyxel.text(2, 22, "Avoid Red!", 0)

PlusTaker()
