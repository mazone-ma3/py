import pyxel
from pyxel import *
import random
import math

class App:
    def __init__(self):
        # ウィンドウの初期化
        pyxel.init(160, 250, title="Vertical Shooting Game")
        pyxel.load("shooting.pyxres")
        
        self.initdata()
        pyxel.run(self.update, self.draw)

    def initdata(self):
        # プレイヤーの初期設定
        self.player_pos = [72, 200]
        self.player_speed = 2
        self.player_bullets = []
        self.enemies = []
        self.enemy_bullets = []
        self.score = 0
        self.game_over = True #False
        
        # 星の初期化（20個の星を生成）
        self.stars = [Star() for _ in range(20)]
        

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_Q):
                pyxel.quit()
            if btnp(KEY_SPACE):
                self.initdata()
                self.game_over = False  # ゲームオーバーフラグ
            return

        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_LEFT) and self.player_pos[0] > 0:
            self.player_pos[0] -= self.player_speed
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_pos[0] < 160 - 16:
            self.player_pos[0] += self.player_speed
        if pyxel.btn(pyxel.KEY_UP) and self.player_pos[1] > 0:
            self.player_pos[1] -= self.player_speed
        if pyxel.btn(pyxel.KEY_DOWN) and self.player_pos[1] < 250 - 16:
            self.player_pos[1] += self.player_speed

        # プレイヤーの弾発射
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.player_bullets.append(PlayerBullet(self.player_pos[0] + 6, self.player_pos[1]))

        # 敵の生成
        if pyxel.frame_count % 60 == 0:
            self.enemies.append(Enemy(random.randint(0, 160 - 16), -16, self.player_pos))

        # 星の更新
        for star in self.stars:
            star.update()

        # プレイヤーの弾更新
        for bullet in self.player_bullets[:]:
            bullet.update()
            if bullet.y < 0:
                self.player_bullets.remove(bullet)

        # 敵の更新
        for enemy in self.enemies[:]:
            enemy.update(self.player_pos, self.enemy_bullets)
            if enemy.y > 250:
                self.enemies.remove(enemy)

        # 敵の弾更新
        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if bullet.y > 250 or bullet.y < 0 or bullet.x < 0 or bullet.x > 160:
                self.enemy_bullets.remove(bullet)

        # 当たり判定（プレイヤーの弾と敵）
        for enemy in self.enemies[:]:
            for bullet in self.player_bullets[:]:
                if (enemy.x < bullet.x + bullet.w and
                    enemy.x + 16 > bullet.x and
                    enemy.y < bullet.y + bullet.h and
                    enemy.y + 16 > bullet.y):
                    self.enemies.remove(enemy)
                    self.player_bullets.remove(bullet)
                    self.score += 100
                    play(0,0)
                    break

        # 当たり判定（プレイヤーと敵）
        for enemy in self.enemies[:]:
            if (enemy.x < self.player_pos[0] + 16 and
                enemy.x + 16 > self.player_pos[0] and
                enemy.y < self.player_pos[1] + 16 and
                enemy.y + 16 > self.player_pos[1]):
                self.game_over = True

        # 当たり判定（プレイヤーと敵の弾）
        for bullet in self.enemy_bullets[:]:
            if (self.player_pos[0] < bullet.x + bullet.w and
                self.player_pos[0] + 16 > bullet.x and
                self.player_pos[1] < bullet.y + bullet.h and
                self.player_pos[1] + 16 > bullet.y):
                self.game_over = True

    def draw(self):
        pyxel.cls(0)

        # 星の描画（背景）
        for star in self.stars:
            star.draw()

        if self.game_over:
            pyxel.text(50, 120, "Game Over", 7)
            pyxel.text(40, 130, "Press Q to Quit", 7)
            return

        # プレイヤーの描画
        pyxel.blt(self.player_pos[0], self.player_pos[1], 0, 0, 0, 16, 16, 14)

        # プレイヤーの弾描画
        for bullet in self.player_bullets:
            bullet.draw()

        # 敵の描画
        for enemy in self.enemies:
            enemy.draw()

        # 敵の弾描画
        for bullet in self.enemy_bullets:
            bullet.draw()

        # スコア表示
        pyxel.text(5, 5, f"Score: {self.score}", 7)

class Star:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = random.randint(0, 160)  # ランダムなx座標
        self.y = random.randint(0, 250)  # ランダムなy座標（画面全体に初期配置）
        self.speed = random.uniform(1, 3)  # 速度（1?3ピクセル/フレーム）
        self.size = random.choice([1, 2])  # 星のサイズ（1x1または2x2）

    def update(self):
        self.y += self.speed  # 下に移動
        if self.y > 250:  # 画面外に出たら上部でリスポーン
            self.x = random.randint(0, 160)
            self.y = -self.size
            self.speed = random.uniform(1, 3)
            self.size = random.choice([1, 2])

    def draw(self):
        pyxel.rect(self.x, self.y, self.size, self.size, 7)  # 白い星

class PlayerBullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 3
        self.h = 3
        self.speed = 5

    def update(self):
        self.y -= self.speed

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 13)
        pyxel.rectb(self.x, self.y, self.w, self.h, 0)

class EnemyBullet:
    def __init__(self, x, y, dx, dy):
        self.x = x
        self.y = y
        self.w = 3
        self.h = 3
        self.dx = dx
        self.dy = dy
        self.speed = 3

    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def draw(self):
        pyxel.rect(self.x, self.y, self.w, self.h, 8)
        pyxel.rectb(self.x, self.y, self.w, self.h, 0)

class Enemy:
    def __init__(self, x, y, player_pos):
        self.x = x
        self.y = y
        self.speed = 2
        self.shoot_timer = 0

    def update(self, player_pos, enemy_bullets):
        self.y += self.speed
        self.shoot_timer += 1
        if self.shoot_timer >= 20:
            player_center_x = player_pos[0] + 8
            player_center_y = player_pos[1] + 8
            enemy_center_x = self.x + 8
            enemy_center_y = self.y + 8
            dx = player_center_x - enemy_center_x
            dy = player_center_y - enemy_center_y
            dist = math.sqrt(dx**2 + dy**2)
            if dist > 0:
                dx /= dist
                dy /= dist
                enemy_bullets.append(EnemyBullet(enemy_center_x, enemy_center_y, dx, dy))
            self.shoot_timer = 0

    def draw(self):
        pyxel.blt(self.x, self.y, 0, 16, 0, 16, 16, 14)

# ゲーム開始
App()