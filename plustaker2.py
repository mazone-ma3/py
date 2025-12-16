import pyxel
import random

class PlusTaker:
    def __init__(self):
        pyxel.init(160, 120, title="Plus Taker - Multi Enemy Ver", fps=60)
        pyxel.mouse(False)
        
        # サウンド定義 (c4までで安全)
        pyxel.sound(0).set("c3e3", "s", "64", "n", 10)      # 射撃: ピコピコ
        pyxel.sound(1).set("g3c4e4", "t", "765", "f", 15)    # 撃破: ドンッ
        pyxel.sound(2).set("c4e4g4c4", "p", "7777", "n", 12) # Plus: キラキラ
        
        self.high_score = 0
        self.reset_game()
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.player_x = 80
        self.player_y = 100
        self.bullets = []
        self.enemies = []
        self.pluses = []
        self.score = 0
        self.combo = 0
        self.combo_timer = 0
        self.wave = 1
        self.kills = 0
        self.spawn_timer = 0
        self.game_over = False
        if self.score > self.high_score:
            self.high_score = self.score

    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return

        # コンボタイマー
        self.combo_timer += 1
        if self.combo_timer > 60:
            self.combo = 0
            self.combo_timer = 0

        # 移動 (WASD/矢印)
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A):
            self.player_x = max(8, self.player_x - 3)
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
            self.player_x = min(152, self.player_x + 3)
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):
            self.player_y = max(16, self.player_y - 3)
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S):
            self.player_y = min(104, self.player_y + 3)

        # 射撃
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.KEY_Z):
            self.bullets.append([self.player_x, self.player_y - 8])
            pyxel.play(0, 0)

        # 弾移動
        for b in self.bullets[:]:
            b[1] -= 5
            if b[1] < 0:
                self.bullets.remove(b)

        # 敵生成 (3体スタート)
        self.spawn_timer += 1
        spawn_interval = max(100 - self.wave * 8, 40)
        if self.spawn_timer > spawn_interval:
            self.spawn_timer = 0
            num_enemies = min(2 + self.wave, 6)  # wave1:3体, wave2:4体...
            for _ in range(num_enemies):
                self.enemies.append([random.randint(10, 150), -10])

        # 敵移動 (waveで速く)
        enemy_speed = 1.5 + self.wave * 0.2
        for e in self.enemies[:]:
            e[1] += enemy_speed
            if e[1] > 120:
                self.enemies.remove(e)

        # 衝突: 弾 vs 敵
        for b in self.bullets[:]:
            for e in self.enemies[:]:
                if abs(b[0] - e[0]) < 12 and abs(b[1] - e[1]) < 12:
                    self.bullets.remove(b)
                    self.enemies.remove(e)
                    self.pluses.append([e[0], e[1]])
                    self.combo += 1
                    self.kills += 1
                    self.score += 20 * self.combo
                    self.combo_timer = 0
                    pyxel.play(1, 1)
                    if self.kills % 5 == 0:
                        self.wave += 1
                    break

        # Plus移動&取得
        for p in self.pluses[:]:
            p[1] += 1.5
            if p[1] > 120:
                self.pluses.remove(p)
                self.combo_timer = 60  # 取り逃しで即リセット
            elif abs(p[0] - self.player_x) < 12 and abs(p[1] - self.player_y) < 12:
                self.pluses.remove(p)
                self.score += 50 * self.combo
                self.combo_timer = 0
                pyxel.play(2, 2)

        # ゲームオーバー (敵接触)
        for e in self.enemies:
            if abs(e[0] - self.player_x) < 16 and abs(e[1] - self.player_y) < 16:
                self.game_over = True

    def draw(self):
        pyxel.cls(0)

        if self.game_over:
            pyxel.text(55, 45, "GAME OVER", pyxel.frame_count % 16 < 8 and 8 or 10)
            pyxel.text(45, 60, f"SCORE: {self.score:06d}", 7)
            pyxel.text(45, 70, f"HIGH: {self.high_score:06d}", 11 if self.score > self.high_score else 7)
            pyxel.text(50, 85, f"WAVE REACHED: {self.wave}", 7)
            pyxel.text(40, 100, "Press R to Retry", 7)
            return

        # プレイヤー (青三角)
        pyxel.tri(self.player_x-8, self.player_y+8, self.player_x, self.player_y-8, self.player_x+8, self.player_y+8, 12)

        # 弾 (白長方形)
        for b in self.bullets:
            pyxel.rect(b[0]-2, b[1]-4, 4, 8, 7)

        # 敵 (赤四角、waveで点滅?)
        for e in self.enemies:
            blink = 9 if (pyxel.frame_count + int(e[0])) % 20 < 10 else 8
            pyxel.rect(e[0]-8, e[1]-8, 16, 16, blink)

        # Plus (黄+、輝き)
        for p in self.pluses:
            glow = 10 + (pyxel.frame_count % 4)
            pyxel.text(p[0]-4, p[1]-4, "+", glow)

        # UI
        pyxel.text(5, 5, f"SCORE: {self.score:06d}", 7)
        pyxel.text(5, 16, f"HIGH: {self.high_score:06d}", 11 if self.score > self.high_score else 7)
        pyxel.text(5, 27, f"WAVE: {self.wave}", 9)
        pyxel.text(5, 38, f"COMBO: x{self.combo}", 11 if self.combo > 0 else 7)
        pyxel.text(5, 110, "ARROW/WASD: MOVE  SPACE/Z: SHOOT  R:RETRY", 6)

PlusTaker()