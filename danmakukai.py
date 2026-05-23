import pyxel
import random
import math
import pickle
import os

class Particle:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2.5, 2.5)
        self.vy = random.uniform(-2.5, 2.5)
        self.life = random.randint(12, 22)
        self.color = random.choice([7, 9, 10, 14])

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1

    def draw(self):
        if self.life > 0:
            pyxel.pset(int(self.x), int(self.y), self.color)

class App:
    def __init__(self):
        pyxel.init(160, 180, title="Simple Danmaku", fps=60)
        self.high_score = self.load_highscore()
        self.setup_sounds()
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def setup_sounds(self):
        pyxel.sound(0).set("a3", "s", "7", "f", 10)      # 射撃
        pyxel.sound(1).set("c2c3c4", "p", "7", "f", 25)  # ボム
        pyxel.sound(2).set("c4", "t", "7", "v", 8)       # 敵撃破
        pyxel.sound(3).set("e4g4", "s", "7", "f", 12)    # アイテム
        pyxel.sound(4).set("f2f1", "n", "7", "f", 15)    # ダメージ

    def load_highscore(self):
        if os.path.exists("highscore.dat"):
            try:
                with open("highscore.dat", "rb") as f:
                    return pickle.load(f)
            except:
                return 0
        return 0

    def save_highscore(self):
        try:
            with open("highscore.dat", "wb") as f:
                pickle.dump(self.high_score, f)
        except:
            pass

    def reset_game(self):
        self.player_x = 72
        self.player_y = 140
        self.player_speed = 2.0
        self.score = 0
        self.lives = 3
        self.bombs = 2
        self.power = 0
        self.combo = 0
        self.combo_timer = 0
        self.invincible = 0
        self.kill_count = 0
        self.game_over = False
        self.new_record = False
        self.frame = 0

        self.bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.items = []
        self.particles = []

    def get_difficulty(self):
        return self.power

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A):
                self.reset_game()
            return

        self.frame += 1
        if self.invincible > 0:
            self.invincible -= 1

        if self.combo > 0:
            self.combo_timer += 1
            if self.combo_timer > 110:
                self.combo = 0

        diff = self.get_difficulty()

        # 入力
        speed = self.player_speed
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT):
            self.player_x -= speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT):
            self.player_x += speed
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_UP):
            self.player_y -= speed
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN):
            self.player_y += speed

        if pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.GAMEPAD1_BUTTON_A):
            if self.frame % 5 == 0:
                self.shoot_player_bullets()
                pyxel.play(0, 0)

        if (pyxel.btnp(pyxel.KEY_X) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_B)) and self.bombs > 0:
            self.use_bomb()
            pyxel.play(1, 1)

        self.player_x = max(4, min(self.player_x, pyxel.width - 12))
        self.player_y = max(20, min(self.player_y, pyxel.height - 12))

        # 敵出現
        spawn_interval = max(38 - diff * 8, 18)
        if self.frame % spawn_interval == 0:
            etype = random.choices([0,1,2,3], weights=[40,25,20,15])[0]
            hp = 3 + diff * 2
            self.enemies.append([random.randint(20, pyxel.width-25), -20, etype, 0, hp])

        # 敵更新
        for e in self.enemies[:]:
            e[3] += 1
            etype = e[2]

            if etype == 0: e[1] += 1.1 + diff*0.1
            elif etype == 1: 
                e[1] += 0.85 + diff*0.05
                e[0] += math.sin(e[3] * 0.15) * 3.2   # ← 振れ幅を大きく
            elif etype == 2: e[1] += 2.2 + diff*0.3
            elif etype == 3: e[1] += 0.65 + diff*0.1

            if e[3] % 45 == 0 and e[1] < 130:
                if etype in (0,1):
                    self.fire_spread(e[0]+8, e[1]+8, 5 + diff, 0.55 + diff*0.1, etype)
                elif etype == 2:
                    self.fire_triple_aimed(e[0]+8, e[1]+8, etype)
                elif etype == 3:
                    self.fire_spread(e[0]+8, e[1]+8, 8 + diff*2, 0.5 + diff*0.08, etype)

            if e[1] > pyxel.height + 30:
                self.enemies.remove(e)

        # 自弾更新
        for b in self.bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[1] < -10:
                self.bullets.remove(b)

        # 敵弾更新
        for eb in self.enemy_bullets[:]:
            eb[0] += eb[2]
            eb[1] += eb[3]
            if not (-30 < eb[0] < pyxel.width+30 and -30 < eb[1] < pyxel.height+30):
                self.enemy_bullets.remove(eb)

        # アイテム・パーティクル
        for item in self.items[:]:
            item[1] += 1.0
            if item[1] > pyxel.height + 10:
                self.items.remove(item)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        # 当たり判定
        px, py = self.player_x + 8, self.player_y + 6
        hitbox = 3

        if self.invincible == 0:
            for b in self.bullets[:]:
                for e in self.enemies[:]:
                    if abs(b[0]-(e[0]+8)) < 9 and abs(b[1]-(e[1]+8)) < 9:
                        e[4] -= 1
                        if b in self.bullets: self.bullets.remove(b)
                        if e[4] <= 0:
                            self.enemies.remove(e)
                            self.score += 300
                            self.kill_count += 1
                            self.create_explosion(e[0]+8, e[1]+8)
                            pyxel.play(2, 2)
                            self.drop_item(e[0], e[1])
                        break

            for e in self.enemies[:]:
                if abs(px - (e[0]+8)) < 13 and abs(py - (e[1]+8)) < 13:
                    self.damage_player()
                    break

            for eb in self.enemy_bullets[:]:
                if abs(eb[0]-px) < hitbox and abs(eb[1]-py) < hitbox:
                    self.damage_player()
                    if eb in self.enemy_bullets: self.enemy_bullets.remove(eb)
                    break

        # アイテム取得
        for item in self.items[:]:
            if abs(item[0]-px) < 10 and abs(item[1]-py) < 10:
                if item[2] == 0: self.power = min(2, self.power+1)
                elif item[2] == 1: self.bombs = min(5, self.bombs+1)
                else:
                    self.combo += 1
                    self.combo_timer = 0
                    self.score += (self.combo + 2) * 45
                pyxel.play(3, 3)
                self.items.remove(item)

        # ハイスコア判定
        if self.game_over and self.score > self.high_score:
            self.high_score = self.score
            self.new_record = True
            self.save_highscore()

    def damage_player(self):
        self.lives -= 1
        self.invincible = 70
        self.power_down()
        pyxel.play(1, 4)
        if self.lives <= 0:
            self.game_over = True

    def create_explosion(self, x, y):
        for _ in range(18):
            self.particles.append(Particle(x, y))

    def fire_spread(self, cx, cy, n, speed, etype):
        for i in range(n):
            angle = i * (360 / n) + self.frame * 1.8
            rad = math.radians(angle)
            self.enemy_bullets.append([cx, cy, math.cos(rad)*speed, math.sin(rad)*speed, etype])

    def fire_triple_aimed(self, cx, cy, etype):
        dx = self.player_x + 8 - cx
        dy = self.player_y + 6 - cy
        dist = math.hypot(dx, dy) or 1
        base_speed = 1.45
        vx = (dx / dist) * base_speed
        vy = (dy / dist) * base_speed

        self.enemy_bullets.append([cx, cy, vx, vy, etype])
        self.enemy_bullets.append([cx, cy + 5, vx*0.95, vy*0.95, etype])
        self.enemy_bullets.append([cx, cy + 10, vx*0.9, vy*0.9, etype])

    def shoot_player_bullets(self):
        x = self.player_x + 8
        y = self.player_y - 2
        speed = 6.5
        if self.power == 0:
            self.bullets.append([x, y, 0, -speed])
        elif self.power == 1:
            for a in [-25, 0, 25]:
                rad = math.radians(a)
                self.bullets.append([x, y, math.sin(rad)*speed, -math.cos(rad)*speed])
        else:  # 5way（角度狭め）
            for a in [-26, -11, 0, 11, 26]:
                rad = math.radians(a)
                self.bullets.append([x, y, math.sin(rad)*speed, -math.cos(rad)*speed])

    def use_bomb(self):
        self.bombs -= 1
        self.enemy_bullets.clear()
        for e in self.enemies[:]:
            e[4] -= 3
            if e[4] <= 0:
                self.enemies.remove(e)
                self.score += 150
                self.create_explosion(e[0]+8, e[1]+8)

    def drop_item(self, x, y):
        if self.kill_count % 10 == 0:
            self.items.append([x + 8, y + 8, 0])  # Power Up確定
        elif random.random() < 0.18:
            if random.random() < 0.5:
                self.items.append([x + 8, y + 8, 1])  # Bomb
            else:
                self.items.append([x + 8, y + 8, 2])  # S

    def power_down(self):
        if self.power > 0:
            self.power -= 1

    def draw_enemy_bullet(self, eb):
        x, y = eb[0], eb[1]
        vx, vy = eb[2], eb[3]
        etype = eb[4] if len(eb) > 4 else 0
        color = 8 if etype == 2 else 10

        angle = math.atan2(vy, vx)
        size = 3.8
        p1x = x + math.cos(angle) * size
        p1y = y + math.sin(angle) * size
        p2x = x + math.cos(angle + 2.5) * size * 0.65
        p2y = y + math.sin(angle + 2.5) * size * 0.65
        p3x = x + math.cos(angle - 2.5) * size * 0.65
        p3y = y + math.sin(angle - 2.5) * size * 0.65
        pyxel.tri(p1x, p1y, p2x, p2y, p3x, p3y, color)

    def draw(self):
        pyxel.cls(0)

        for i in range(40):
            x = (i*7 + self.frame//2) % (pyxel.width + 30) -15
            y = (i*9) % (pyxel.height + 50)
            pyxel.pset(x, y, 7)

        for b in self.bullets:
            pyxel.rect(b[0]-1, b[1], 3, 8, 9)

        for e in self.enemies:
            c = 8 if e[4] >= 4 else 9 if e[4] == 3 else 10
            pyxel.rect(e[0], e[1], 16, 14, c)
            pyxel.rect(e[0]+5, e[1]+4, 6, 6, 7)

        for eb in self.enemy_bullets:
            self.draw_enemy_bullet(eb)

        for item in self.items:
            if item[2] == 0: pyxel.text(item[0]-3, item[1]-3, "P", 11)
            elif item[2] == 1: pyxel.text(item[0]-3, item[1]-3, "B", 14)
            else: pyxel.text(item[0]-3, item[1]-3, "S", 7)

        for p in self.particles:
            p.draw()

        if self.invincible == 0 or (self.frame % 4 < 2):
            pyxel.tri(self.player_x, self.player_y+12,
                      self.player_x+8, self.player_y,
                      self.player_x+16, self.player_y+12, 11)

        pyxel.text(4, 4, f"SCORE {self.score:06d}", 7)
        pyxel.text(4, 14, f"HIGH {self.high_score:06d}", 7)
        pyxel.text(4, 24, f"POWER {self.power+1}WAY", 11)
        if self.combo >= 2:
            pyxel.text(4, 34, f"COMBO x{self.combo}", 10)
        pyxel.text(pyxel.width-72, 4, f"LIVES {self.lives}  BOMB {self.bombs}", 7)

        if self.game_over:
            pyxel.text(48, 60, "GAME OVER", 8)
            if self.new_record:
                pyxel.text(40, 75, "NEW RECORD!", 10)
            pyxel.text(36, 95, "PRESS R TO RESTART", 7)

App()