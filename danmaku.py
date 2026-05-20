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
        self.reset_game()
        pyxel.run(self.update, self.draw)

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
        self.player_speed = 2.5
        self.score = 0
        self.lives = 3
        self.bombs = 2
        self.power = 0
        self.combo = 0
        self.combo_timer = 0
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
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return

        self.frame += 1
        if self.combo > 0:
            self.combo_timer += 1
            if self.combo_timer > 110:
                self.combo = 0

        diff = self.get_difficulty()

        # プレイヤー移動
        speed = self.player_speed
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A): self.player_x -= speed
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D): self.player_x += speed
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W): self.player_y -= speed
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S): self.player_y += speed

        self.player_x = max(4, min(self.player_x, pyxel.width - 12))
        self.player_y = max(20, min(self.player_y, pyxel.height - 12))

        # ショット
        if pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_SPACE):
            if self.frame % 5 == 0:
                self.shoot_player_bullets()

        # ボム
        if pyxel.btnp(pyxel.KEY_X) and self.bombs > 0:
            self.use_bomb()

        # 敵出現
        spawn_interval = max(36 - diff * 6, 22)
        if self.frame % spawn_interval == 0:
            etype = random.choices([0,1,2,3], weights=[40,25,20,15])[0]
            hp = 3 + diff
            self.enemies.append([random.randint(20, pyxel.width-25), -20, etype, 0, hp])

        # 敵更新
        for e in self.enemies[:]:
            e[3] += 1
            etype = e[2]
            if etype == 0: e[1] += 1.1 + diff*0.1
            elif etype == 1: 
                e[1] += 0.95 + diff*0.08
                e[0] += math.sin(e[3]*0.22) * (1.8 + diff*0.4)
            elif etype == 2: e[1] += 2.2 + diff*0.3
            elif etype == 3: e[1] += 0.65 + diff*0.1

            interval = max(34 - diff*5, 22)
            if e[3] % interval == 0 and e[1] < 130:
                if etype in (0,1):
                    self.fire_spread(e[0]+8, e[1]+8, 5 + diff, 0.55 + diff*0.1)
                elif etype == 2:
                    self.fire_aimed(e[0]+8, e[1]+8, 1.2 + diff*0.15)
                elif etype == 3:
                    self.fire_spread(e[0]+8, e[1]+8, 7 + diff*2, 0.5 + diff*0.08)

            if e[1] > pyxel.height + 30:
                self.enemies.remove(e)

        # 更新処理（自弾・敵弾・アイテム・パーティクル）
        for b in self.bullets[:]:
            b[0] += b[2]
            b[1] += b[3]
            if b[1] < -10: self.bullets.remove(b)

        for eb in self.enemy_bullets[:]:
            eb[0] += eb[2]
            eb[1] += eb[3]
            if not (-30 < eb[0] < pyxel.width+30 and -30 < eb[1] < pyxel.height+30):
                self.enemy_bullets.remove(eb)

        for item in self.items[:]:
            item[1] += 1.0
            if item[1] > pyxel.height + 10:
                self.items.remove(item)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        # 当たり判定（省略）
        px, py = self.player_x + 8, self.player_y + 6
        hitbox = 3

        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if abs(b[0]-(e[0]+8)) < 9 and abs(b[1]-(e[1]+8)) < 9:
                    e[4] -= 1
                    if b in self.bullets: self.bullets.remove(b)
                    if e[4] <= 0:
                        self.enemies.remove(e)
                        self.score += 300
                        self.create_explosion(e[0]+8, e[1]+8)
                        self.drop_bonus_item(e[0], e[1])
                    break

        for e in self.enemies[:]:
            if abs(px - (e[0]+8)) < 13 and abs(py - (e[1]+8)) < 13:
                self.power_down()
                self.lives -= 1
                if self.lives <= 0: self.game_over = True
                break

        for eb in self.enemy_bullets[:]:
            if abs(eb[0]-px) < hitbox and abs(eb[1]-py) < hitbox:
                self.power_down()
                self.lives -= 1
                if eb in self.enemy_bullets: self.enemy_bullets.remove(eb)
                if self.lives <= 0: self.game_over = True
                break

        for item in self.items[:]:
            if abs(item[0]-px) < 10 and abs(item[1]-py) < 10:
                if item[2] == 0: self.power = min(2, self.power+1)
                elif item[2] == 1: self.bombs = min(5, self.bombs+1)
                else:
                    self.combo += 1
                    self.combo_timer = 0
                    self.score += (self.combo + 2) * 45
                self.items.remove(item)

        # ゲームオーバー時のハイスコア更新
        if self.game_over and self.score > self.high_score:
            self.high_score = self.score
            self.new_record = True
            self.save_highscore()

    def create_explosion(self, x, y):
        for _ in range(18):
            self.particles.append(Particle(x, y))

    def fire_spread(self, cx, cy, n, speed):
        for i in range(n):
            angle = i * (360 / n) + self.frame * 1.8
            rad = math.radians(angle)
            self.enemy_bullets.append([cx, cy, math.cos(rad)*speed, math.sin(rad)*speed])

    def fire_aimed(self, cx, cy, speed):
        dx = self.player_x + 8 - cx
        dy = self.player_y + 6 - cy
        dist = math.hypot(dx, dy) or 1
        self.enemy_bullets.append([cx, cy, dx/dist*speed, dy/dist*speed])

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
        else:
            for a in [-30, -15, 0, 15, 30]:
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

    def drop_bonus_item(self, x, y):
        if random.random() < 0.16:
            t = 0 if random.random() < 0.55 else 1
            self.items.append([x+8, y+8, t])
        else:
            self.items.append([x+8, y+8, 2])

    def power_down(self):
        if self.power > 0:
            self.power -= 1

    def draw(self):
        pyxel.cls(0)

        # 背景
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
            pyxel.rect(eb[0]-1, eb[1]-1, 3, 3, 10)

        for item in self.items:
            if item[2] == 0: pyxel.text(item[0]-3, item[1]-3, "P", 11)
            elif item[2] == 1: pyxel.text(item[0]-3, item[1]-3, "B", 14)
            else: pyxel.text(item[0]-3, item[1]-3, "S", 7)

        for p in self.particles:
            p.draw()

        pyxel.tri(self.player_x, self.player_y+12,
                  self.player_x+8, self.player_y,
                  self.player_x+16, self.player_y+12, 11)

        # UI
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