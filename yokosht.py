import pyxel
import math
import random
import json
import os

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-4, 4)
        self.vy = random.uniform(-4, 4)
        self.life = 35 + random.randint(0, 20)
        self.color = random.choice([8, 9, 10, 14])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pyxel.pset(int(self.x), int(self.y), self.color)
            if self.life > 20:
                pyxel.pset(int(self.x + 1), int(self.y), 7)

class Option:
    def __init__(self, offset_y):
        self.offset_y = offset_y
        self.x = 0
        self.y = 0

    def update(self, player_x, player_y):
        self.x += ((player_x + 8) - self.x) * 0.25
        self.y += ((player_y + self.offset_y) - self.y) * 0.25

    def draw(self):
        pyxel.tri(self.x-4, self.y, self.x+4, self.y-4, self.x+4, self.y+4, 11)
        pyxel.tri(self.x-4, self.y, self.x-4, self.y-4, self.x-4, self.y+4, 11)

class ChainItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 240

    def update(self):
        self.x -= 1.6
        self.timer -= 1

    def draw(self):
        c = 10 if self.timer % 8 < 4 else 9
        pyxel.tri(self.x, self.y-7, self.x+7, self.y, self.x, self.y+7, c)
        pyxel.tri(self.x-7, self.y, self.x, self.y-4, self.x, self.y+4, 7)

class OptionItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 300

    def update(self):
        self.x -= 1.4
        self.timer -= 1

    def draw(self):
        c = 12 if self.timer % 10 < 5 else 6
        pyxel.tri(self.x, self.y-8, self.x+8, self.y, self.x, self.y+8, c)
        pyxel.tri(self.x-6, self.y, self.x+2, self.y-5, self.x+2, self.y+5, 7)

class ShieldItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 280

    def update(self):
        self.x -= 1.5
        self.timer -= 1

    def draw(self):
        c = 7 if self.timer % 6 < 3 else 12
        pyxel.circ(self.x + 4, self.y + 4, 7, c)
        pyxel.circb(self.x + 4, self.y + 4, 7, 6)

class BombItem:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.timer = 270

    def update(self):
        self.x -= 1.5
        self.timer -= 1

    def draw(self):
        c = 8 if self.timer % 7 < 4 else 9
        pyxel.circ(self.x + 5, self.y + 5, 6, c)
        pyxel.pset(self.x + 5, self.y + 2, 7)
        pyxel.pset(self.x + 5, self.y + 8, 7)

class App:
    def __init__(self):
        pyxel.init(256, 192, title="Simple Shmup - Bomb Item", fps=60)

        # 効果音（チャンネル4は使えないので3に変更）
        pyxel.sounds[0].set("c3e3g3", tones="t", volumes="4", effects="f", speed=10)   # 通常ショット
        pyxel.sounds[1].set("c2c2c1", tones="p", volumes="6", effects="n", speed=15)   # 撃破
        pyxel.sounds[2].set("g2e2", tones="s", volumes="5", effects="f", speed=8)      # 敵射撃
        pyxel.sounds[3].set("c2a1f1", tones="p", volumes="7", effects="n", speed=20)   # ゲームオーバー
        pyxel.sounds[4].set("c2c2c3c2", tones="t", volumes="7", effects="n", speed=8)  # ボム使用音（修正済み）

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
        self.options = []
        self.chain_items = []
        self.option_items = []
        self.shield_items = []
        self.bomb_items = []
        self.bomb_stock = 0
        self.shield_active = False

        self.chain_count = 0
        self.chain_timer = 0

        self.enemies = []
        self.enemy_spawn_timer = 0
        self.kill_count = 0

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

        # 射撃
        self.shoot_timer += 1
        if (pyxel.btn(pyxel.KEY_SPACE) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A)) and self.shoot_timer > 8:
            self.bullets.append([self.player_x + 16, self.player_y + 6])
            for opt in self.options:
                self.bullets.append([opt.x + 4, opt.y])
            self.shoot_timer = 0
            pyxel.play(0, 0)

        # ボム使用（Bキー or ゲームパッド Bボタン）
        if (pyxel.btnp(pyxel.KEY_B) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)) and self.bomb_stock > 0:
            self.use_bomb()

        for b in self.bullets[:]:
            b[0] += 6
            if b[0] > pyxel.width:
                self.bullets.remove(b)

        # 敵出現
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer > max(20, 50 - (self.score // 150)):
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

        # 自機弾 vs 敵
        for b_idx in range(len(self.bullets)-1, -1, -1):
            b = self.bullets[b_idx]
            for e_idx in range(len(self.enemies)-1, -1, -1):
                e = self.enemies[e_idx]
                if (b[0] < e[0] + 16 and b[0] + 8 > e[0] and
                    b[1] < e[1] + 16 and b[1] + 4 > e[1]):

                    ex = e[0] + 8
                    ey = e[1] + 8
                    for _ in range(18):
                        self.particles.append(Particle(ex, ey))

                    del self.enemies[e_idx]
                    del self.bullets[b_idx]

                    self.score += 100
                    self.kill_count += 1
                    pyxel.play(1, 1)

                    if random.random() < 0.40:
                        self.chain_items.append(ChainItem(ex, ey))
                    if random.random() < 0.15 and len(self.options) < 2:
                        self.option_items.append(OptionItem(ex, ey))
                    if random.random() < 0.12 and not self.shield_active:
                        self.shield_items.append(ShieldItem(ex, ey))
                    if random.random() < 0.10 and self.bomb_stock < 3:
                        self.bomb_items.append(BombItem(ex, ey))

                    break

        # チェインアイテム処理
        for item in self.chain_items[:]:
            item.update()
            if abs(self.player_x + 8 - item.x) < 20 and abs(self.player_y + 8 - item.y) < 20:
                self.chain_count += 1
                self.chain_timer = 240
                self.score += 100 * self.chain_count
                pyxel.play(1, 1)
                self.chain_items.remove(item)
                continue
            if item.x < -20 or item.timer <= 0:
                self.chain_count = 0
                self.chain_items.remove(item)

        if self.chain_count > 0:
            self.chain_timer -= 1
            if self.chain_timer <= 0:
                self.chain_count = 0

        # オプションアイテム処理
        for item in self.option_items[:]:
            item.update()
            if abs(self.player_x + 8 - item.x) < 22 and abs(self.player_y + 8 - item.y) < 22:
                if len(self.options) < 2:
                    offset = 25 if len(self.options) == 0 else -25
                    self.options.append(Option(offset))
                self.option_items.remove(item)
                pyxel.play(1, 1)
                continue
            if item.x < -20 or item.timer <= 0:
                self.option_items.remove(item)

        # シールドアイテム処理
        for item in self.shield_items[:]:
            item.update()
            if abs(self.player_x + 8 - item.x) < 22 and abs(self.player_y + 8 - item.y) < 22:
                self.shield_active = True
                self.shield_items.remove(item)
                pyxel.play(1, 1)
                continue
            if item.x < -20 or item.timer <= 0:
                self.shield_items.remove(item)

        # ボムアイテム処理
        for item in self.bomb_items[:]:
            item.update()
            if abs(self.player_x + 8 - item.x) < 22 and abs(self.player_y + 8 - item.y) < 22:
                self.bomb_stock = min(3, self.bomb_stock + 1)
                self.bomb_items.remove(item)
                pyxel.play(1, 1)
                continue
            if item.x < -20 or item.timer <= 0:
                self.bomb_items.remove(item)

        # オプション更新
        for opt in self.options:
            opt.update(self.player_x, self.player_y)

        # 当たり判定
        ph_x = self.player_x
        ph_y = self.player_y + 3
        ph_w = 16
        ph_h = 10

        for eb_idx in range(len(self.enemy_bullets)-1, -1, -1):
            eb = self.enemy_bullets[eb_idx]
            if (ph_x < eb[0] + 4 and ph_x + ph_w > eb[0] and
                ph_y < eb[1] + 4 and ph_y + ph_h > eb[1]):
                if self.shield_active:
                    self.shield_active = False
                    for _ in range(12):
                        self.particles.append(Particle(self.player_x + 8, self.player_y + 8))
                else:
                    self.game_over = True
                    pyxel.play(3, 3)
                self.enemy_bullets.pop(eb_idx)
                break

        for e_idx in range(len(self.enemies)-1, -1, -1):
            e = self.enemies[e_idx]
            if (ph_x < e[0] + 16 and ph_x + ph_w > e[0] and
                ph_y < e[1] + 16 and ph_y + ph_h > e[1]):
                if self.shield_active:
                    self.shield_active = False
                    for _ in range(12):
                        self.particles.append(Particle(self.player_x + 8, self.player_y + 8))
                else:
                    self.game_over = True
                    pyxel.play(3, 3)
                self.enemies.pop(e_idx)
                break

        # パーティクル更新
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        if self.game_over and self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def use_bomb(self):
        if self.bomb_stock <= 0:
            return
        self.bomb_stock -= 1
        pyxel.play(3, 4)        # ← ここを修正（チャンネル3を使用）

        # 大きな爆発エフェクト
        for _ in range(90):
            self.particles.append(Particle(random.randint(20, 236), random.randint(20, 172)))

        # 全敵・全敵弾消滅
        self.enemies.clear()
        self.enemy_bullets.clear()

        self.score += 200

    def draw(self):
        pyxel.cls(0)

        for star in self.stars:
            star[0] -= star[2]
            if star[0] < 0:
                star[0] = pyxel.width
            pyxel.pset(int(star[0]), int(star[1]), 7)

        pyxel.tri(self.player_x + 16, self.player_y + 8,
                  self.player_x, self.player_y + 4,
                  self.player_x, self.player_y + 12, 10)

        if self.shield_active:
            alpha = 7 if pyxel.frame_count % 8 < 4 else 12
            pyxel.circb(self.player_x + 8, self.player_y + 8, 13, alpha)

        for b in self.bullets:
            pyxel.rect(b[0], b[1], 8, 4, 9)

        for e in self.enemies:
            pyxel.rect(e[0], e[1], 16, 16, 8)
            pyxel.rect(e[0] + 4, e[1] + 4, 8, 8, 14)

        for eb in self.enemy_bullets:
            pyxel.rect(eb[0], eb[1], 5, 5, 8)

        for opt in self.options:
            opt.draw()

        for item in self.chain_items:
            item.draw()

        for item in self.option_items:
            item.draw()

        for item in self.shield_items:
            item.draw()

        for item in self.bomb_items:
            item.draw()

        for p in self.particles:
            p.draw()

        # UI
        pyxel.text(4, 4, f"SCORE: {self.score}", 7)
        pyxel.text(4, 14, f"HIGH: {self.high_score}", 7)
        pyxel.text(180, 4, f"OPTIONS: {len(self.options)}", 7)
        pyxel.text(200, 14, f"BOMB: {self.bomb_stock}", 8)

        if self.chain_count > 0:
            pyxel.text(95, 8, f"CHAIN x{self.chain_count}", 10)

        if self.game_over:
            pyxel.text(72, 70, "GAME OVER", 8)
            pyxel.text(55, 85, f"FINAL SCORE: {self.score}", 7)
            if self.score == self.high_score and self.score > 0:
                pyxel.text(65, 100, "NEW HIGH SCORE!", 10)
            pyxel.text(55, 120, "PRESS R or A TO RESTART", 7)

App()