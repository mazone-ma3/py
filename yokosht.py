import pyxel
import math
import random
import json
import os

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30 + random.randint(0, 15)
        self.color = random.choice([8, 9, 10, 14])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pyxel.pset(int(self.x), int(self.y), self.color)
            if self.life > 15 and self.life % 3 == 0:
                pyxel.pset(int(self.x + 1), int(self.y), 7)

class Option:
    def __init__(self, offset_y):
        self.offset_y = offset_y   # +25（上） or -25（下）
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y):
        # 自機に遅れて追従
        target_x = player_x + 8
        target_y = player_y + self.offset_y
        self.x += (target_x - self.x) * 0.25
        self.y += (target_y - self.y) * 0.25

    def draw(self):
        # オプションの見た目（小さな菱形）
        pyxel.tri(self.x-4, self.y, self.x+4, self.y-4, self.x+4, self.y+4, 11)
        pyxel.tri(self.x-4, self.y, self.x-4, self.y-4, self.x-4, self.y+4, 11)

class App:
    def __init__(self):
        pyxel.init(256, 192, title="Simple Shmup - With Options", fps=60)

        # 効果音
        pyxel.sounds[0].set("c3e3g3", tones="t", volumes="4", effects="f", speed=10)   # 自機ショット
        pyxel.sounds[1].set("c2c2c1", tones="p", volumes="6", effects="n", speed=15)   # 敵撃破
        pyxel.sounds[2].set("g2e2", tones="s", volumes="5", effects="f", speed=8)      # 敵射撃
        pyxel.sounds[3].set("c2a1f1", tones="p", volumes="7", effects="n", speed=20)   # ゲームオーバー

        self.high_score = self.load_high_score()
        self.particles = []
        self.reset()
        pyxel.run(self.update, self.draw)

    def load_high_score(self):
        if os.path.exists("highscore.json"):
            try:
                with open("highscore.json", "r") as f:
                    return json.load(f).get("high_score", 0)
            except:
                return 0
        return 0

    def save_high_score(self):
        try:
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass

    def reset(self):
        self.player_x = 30
        self.player_y = 80
        self.player_speed = 2.0

        self.bullets = []
        self.enemy_bullets = []
        self.particles = []
        self.options = []           # Optionオブジェクトのリスト
        self.option_item = None     # 画面上のアイテム [x, y]

        self.enemies = []
        self.enemy_spawn_timer = 0
        self.kill_count = 0         # オプション出現用カウンタ

        self.shoot_timer = 0
        self.score = 0
        self.game_over = False

        self.stars = []
        for _ in range(80):
            self.stars.append([random.randint(0, pyxel.width),
                               random.randint(0, pyxel.height),
                               random.uniform(0.8, 1.8)])

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.reset()
            return

        # 移動
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT): self.player_x -= self.player_speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT): self.player_x += self.player_speed
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP): self.player_y -= self.player_speed
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN): self.player_y += self.player_speed
        if pyxel.btn(pyxel.KEY_A): self.player_x -= self.player_speed
        if pyxel.btn(pyxel.KEY_D): self.player_x += self.player_speed
        if pyxel.btn(pyxel.KEY_W): self.player_y -= self.player_speed
        if pyxel.btn(pyxel.KEY_S): self.player_y += self.player_speed

        self.player_x = max(0, min(self.player_x, pyxel.width - 20))
        self.player_y = max(0, min(self.player_y, pyxel.height - 16))

        # 自機 + オプションからの射撃
        self.shoot_timer += 1
        if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)) and self.shoot_timer > 8:
            # 自機弾
            self.bullets.append([self.player_x + 16, self.player_y + 6])
            # オプション弾（上と下から同時に発射）
            for opt in self.options:
                self.bullets.append([opt.x + 4, opt.y])
            self.shoot_timer = 0
            pyxel.play(0, 0)

        # 自機弾更新
        for b in self.bullets[:]:
            b[0] += 6
            if b[0] > pyxel.width:
                self.bullets.remove(b)

        # 敵出現
        self.enemy_spawn_timer += 1
        spawn_interval = max(20, 50 - (self.score // 150))
        if self.enemy_spawn_timer > spawn_interval:
            self.enemies.append([pyxel.width, pyxel.rndi(10, pyxel.height - 20), pyxel.rndi(60, 100)])
            self.enemy_spawn_timer = 0

        # 敵移動 + 射撃
        for e in self.enemies[:]:
            e[0] -= 2
            e[2] += 1
            min_interval = max(35, 75 - (self.score // 200))

            if e[2] > min_interval:
                sx, sy = e[0] + 8, e[1] + 8
                px, py = self.player_x + 8, self.player_y + 8
                dx = px - sx
                dy = py - sy
                dist = math.hypot(dx, dy) or 1

                base_speed = 3.05
                direction_factor = dx / dist
                speed = base_speed * (1.0 - 0.22 * direction_factor)

                vx = (dx / dist) * speed
                vy = (dy / dist) * speed

                self.enemy_bullets.append([sx, sy, vx, vy])
                e[2] = pyxel.rndi(-15, 10)
                pyxel.play(2, 2)

            if e[0] < -16:
                self.enemies.remove(e)

        # 敵弾更新
        for eb in self.enemy_bullets[:]:
            eb[0] += eb[2]
            eb[1] += eb[3]
            if eb[0] < -10 or eb[0] > pyxel.width + 10 or eb[1] < -10 or eb[1] > pyxel.height + 10:
                self.enemy_bullets.remove(eb)

        # 当たり判定：自機弾 vs 敵
        for b_idx in range(len(self.bullets)-1, -1, -1):
            b = self.bullets[b_idx]
            for e_idx in range(len(self.enemies)-1, -1, -1):
                e = self.enemies[e_idx]
                if (b[0] < e[0] + 16 and b[0] + 8 > e[0] and
                    b[1] < e[1] + 16 and b[1] + 4 > e[1]):
                    # 爆発
                    ex, ey = e[0] + 8, e[1] + 8
                    for _ in range(18):
                        self.particles.append(Particle(ex, ey))
                    del self.enemies[e_idx]
                    del self.bullets[b_idx]
                    self.score += 100
                    self.kill_count += 1
                    pyxel.play(1, 1)

                    # 10体倒すごとにオプションアイテム出現
                    if self.kill_count % 10 == 0 and self.option_item is None:
                        self.option_item = [pyxel.width, pyxel.rndi(40, pyxel.height - 40)]
                    break

        # オプションアイテムの移動と取得
        if self.option_item:
            self.option_item[0] -= 1.5
            if self.option_item[0] < -16:
                self.option_item = None

            # 取得判定
            if self.option_item:
                ix, iy = self.option_item
                if (abs(self.player_x + 8 - ix) < 18 and abs(self.player_y + 8 - iy) < 18):
                    if len(self.options) < 2:
                        offset = 25 if len(self.options) == 0 else -25
                        self.options.append(Option(offset))
                    self.option_item = None

        # オプション更新
        for opt in self.options:
            opt.update(self.player_x, self.player_y)

        # 当たり判定：敵弾 vs プレイヤー / プレイヤー vs 敵
        for eb in self.enemy_bullets[:]:
            if (self.player_x < eb[0] + 4 and self.player_x + 16 > eb[0] and
                self.player_y < eb[1] + 4 and self.player_y + 16 > eb[1]):
                self.game_over = True
                pyxel.play(3, 3)
                break

        for e in self.enemies[:]:
            if (self.player_x < e[0] + 16 and self.player_x + 16 > e[0] and
                self.player_y < e[1] + 16 and self.player_y + 16 > e[1]):
                self.game_over = True
                pyxel.play(3, 3)
                break

        # パーティクル更新
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        if self.game_over and self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def draw(self):
        pyxel.cls(0)

        # 背景星
        for star in self.stars:
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = pyxel.width
            pyxel.pset(int(star[0]), int(star[1]), 7)

        # 自機
        pyxel.tri(self.player_x + 16, self.player_y + 8,
                  self.player_x, self.player_y + 4,
                  self.player_x, self.player_y + 12, 10)

        # 自機弾
        for b in self.bullets:
            pyxel.rect(b[0], b[1], 8, 4, 9)

        # 敵
        for e in self.enemies:
            pyxel.rect(e[0], e[1], 16, 16, 8)
            pyxel.rect(e[0] + 4, e[1] + 4, 8, 8, 14)

        # 敵弾
        for eb in self.enemy_bullets:
            pyxel.rect(eb[0], eb[1], 5, 5, 8)

        # オプション
        for opt in self.options:
            opt.draw()

        # オプションアイテム（光る菱形）
        if self.option_item:
            ix, iy = self.option_item
            pyxel.tri(ix, iy-6, ix+8, iy, ix, iy+6, 10)
            pyxel.tri(ix-4, iy, ix+4, iy-4, ix+4, iy+4, 7)

        # 爆発
        for p in self.particles:
            p.draw()

        # UI
        pyxel.text(4, 4, f"SCORE: {self.score}", 7)
        pyxel.text(4, 14, f"HIGH: {self.high_score}", 7)
        pyxel.text(180, 4, f"OPTIONS: {len(self.options)}", 7)

        if self.game_over:
            pyxel.text(72, 70, "GAME OVER", 8)
            pyxel.text(55, 85, f"FINAL SCORE: {self.score}", 7)
            if self.score == self.high_score and self.score > 0:
                pyxel.text(65, 100, "NEW HIGH SCORE!", 10)
            pyxel.text(55, 120, "PRESS R or A TO RESTART", 7)

App()