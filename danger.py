import pyxel
import random
import math

class Game:
    def __init__(self):
        pyxel.init(160, 120, title="危険な階段 岩増加版", fps=30)
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.player_x = 80
        self.player_y = 100
        self.player_vy = 0
        self.player_vx = 0
        self.scroll_y = 0.0
        self.speed = 1.2
        self.gravity = 0.4
        self.jump_power = -7.5
        self.on_ground = True
        self.rocks = []
        self.rock_timer = 0
        self.rock_interval = 60  # 約2秒ごと
        self.gameover = False
        self.score = 0
        self.level = 1

    def update(self):
        if self.gameover:
            if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_RETURN):
                self.reset()
            return

        # 左右移動
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.player_vx = max(-3.0, self.player_vx - 0.4)
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.player_vx = min(3.0, self.player_vx + 0.4)
        self.player_x += self.player_vx
        self.player_vx *= 0.85
        self.player_x = max(8, min(152, self.player_x))

        # ジャンプ
        if (pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_UP)) and self.on_ground:
            self.player_vy = self.jump_power
            self.on_ground = False

        self.player_vy += self.gravity
        self.player_y += self.player_vy
        if self.player_y >= 100:
            self.player_y = 100
            self.player_vy = 0
            self.on_ground = True

        self.scroll_y += self.speed
        self.score = int(self.scroll_y / 10)

        # レベルを50スコアごとに上げる
        if self.score >= self.level * 50:
            self.level += 1

        l = self.level - 1
        self.speed = 1.2 + l * 0.1  # 緩やかに加速

        # 岩生成: レベルに応じて生成数が増える（1→2→3…最大5）
        num_rocks_this_level = min(l + 1, 5)  # レベル1=1個、レベル2=2個…レベル5以降=5個
        self.rock_timer += 1
        if self.rock_timer >= self.rock_interval and len(self.rocks) < 6:  # 最大6個制限
            for _ in range(num_rocks_this_level):
                rock_x = random.randint(20, 140)
                self.rocks.append({
                    "x": rock_x,
                    "y": random.uniform(-25, -5),
                    "vx": random.uniform(-1.0, 1.0),
                    "vy": self.speed * 1.4 + random.uniform(0.6, 1.8),
                    "size": random.randint(7, 13),
                    "roll": 0
                })
            self.rock_timer = 0

        # 岩更新
        for rock in self.rocks[:]:
            rock["x"] += rock["vx"]
            rock["y"] += rock["vy"]
            rock["vy"] += 0.12
            rock["roll"] += 1
            if rock["y"] > 140:
                self.rocks.remove(rock)
                continue

            px = self.player_x + 6
            py = self.player_y + 8
            if math.hypot(px - rock["x"], py - rock["y"]) < 10 + rock["size"]:
                self.gameover = True

    def draw(self):
        pyxel.cls(12)

        for i in range(0, 120, 20):
            c = 12 if i < 40 else 11 if i < 80 else 10
            pyxel.rect(0, i, 160, 20, c)

        offset = int(self.scroll_y) % 24
        for i in range(-3, 7):
            y = (i * 24 + offset) % 120 - 20
            if y < -24 or y > 120: continue
            pyxel.rect(0, y, 160, 6, 6)
            pyxel.rect(0, y - 3, 160, 3, 7)
            pyxel.rect(0, y + 6, 160, 2, 9)
            pyxel.rect(0, y - 3, 12, 27, 9)

        pyxel.rect(0, 110, 160, 10, 8)

        px, py = self.player_x, self.player_y
        pyxel.rect(px, py, 12, 16, 8)
        pyxel.rect(px+3, py+4, 2, 2, 0)
        pyxel.rect(px+7, py+4, 2, 2, 0)

        frame = int(self.scroll_y * 0.3) % 4
        if frame == 0 or frame == 2:
            pyxel.rect(px+1, py+11, 4, 5, 0)
            pyxel.rect(px+7, py+12, 4, 4, 0)
        else:
            pyxel.rect(px+2, py+12, 3, 4, 0)
            pyxel.rect(px+6, py+11, 4, 5, 0)

        for rock in self.rocks:
            r = rock["size"]
            pyxel.circ(rock["x"], rock["y"], r, 13)
            pyxel.circb(rock["x"], rock["y"], r, 7)
            pyxel.circ(rock["x"]+2, rock["y"]+2, r-2, 9)

        pyxel.text(4, 4, f"SCORE:{self.score:>6}", 0)
        pyxel.text(4, 14, f"LEVEL:{self.level}", 0)
        pyxel.text(4, 24, f"ROCKS:{len(self.rocks)}", 0)

        if self.gameover:
            pyxel.rect(30, 40, 100, 45, 0)
            pyxel.text(48, 50, "GAME OVER", 8)
            pyxel.text(45, 65, f"SCORE:{self.score}", 7)
            pyxel.text(40, 80, "SPACE to retry", 7)

Game()