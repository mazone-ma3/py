import pyxel

class BreakoutGame:
    def __init__(self):
        # 画面サイズを設定（160x120）
        pyxel.init(160, 120, title="Breakout")
        # リソースファイルの読み込み（スプライトやサウンド）
        pyxel.load("breakout.pyxres")

        # パドルの初期位置
        self.paddle_x = 60
        self.paddle_y = 110
        self.paddle_width = 24
        self.paddle_height = 4

        # ボールの初期位置と速度
        self.ball_x = 80
        self.ball_y = 60
        self.ball_speed_x = 2
        self.ball_speed_y = -2
        self.ball_size = 4

        # ブロックの設定（例：5行×8列）
        self.blocks = []
        for row in range(5):
            for col in range(8):
                self.blocks.append([col * 20 + 10, row * 10 + 20, True])  # [x, y, alive]

        # スコアとライフ
        self.score = 0
        self.lives = 3

        # ゲームループ開始
        pyxel.run(self.update, self.draw)

    def update(self):
        # パドルの移動（左右キー）
        if pyxel.btn(pyxel.KEY_LEFT) and self.paddle_x > 0:
            self.paddle_x -= 3
        if pyxel.btn(pyxel.KEY_RIGHT) and self.paddle_x < pyxel.width - self.paddle_width:
            self.paddle_x += 3

        # ボールの移動
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y

        # 壁の反射（左右と上）
        if self.ball_x <= 0 or self.ball_x >= pyxel.width - self.ball_size:
            self.ball_speed_x = -self.ball_speed_x
        if self.ball_y <= 0:
            self.ball_speed_y = -self.ball_speed_y

        # パドルとの衝突
        if (self.ball_y + self.ball_size >= self.paddle_y and
            self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_width):
            self.ball_speed_y = -self.ball_speed_y
            # 効果音再生（必要なら）
            pyxel.play(0, 0)

        # ブロックとの衝突
        for block in self.blocks:
            if block[2]:  # ブロックが生きている場合
                bx, by = block[0], block[1]
                if (bx <= self.ball_x <= bx + 20 and
                    by <= self.ball_y <= by + 10):
                    block[2] = False  # ブロックを破壊
                    self.ball_speed_y = -self.ball_speed_y  # ボールを反射
                    self.score += 10
                    pyxel.play(0, 1)  # 破壊音

        # ボールが下に落ちた場合
        if self.ball_y >= pyxel.height:
            self.lives -= 1
            # ボールをリセット
            self.ball_x = 80
            self.ball_y = 60
            self.ball_speed_x = 2
            self.ball_speed_y = -2

        # ゲームオーバーまたはクリア
        if self.lives <= 0:
            pyxel.quit()  # 簡易的に終了（後でゲームオーバー画面を追加可能）
        if all(not block[2] for block in self.blocks):
            pyxel.quit()  # 全てのブロックを壊したら終了

    def draw(self):
        # 画面をクリア
        pyxel.cls(0)

        # パドルを描画
        pyxel.rect(self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height, 11)

        # ボールを描画
        pyxel.rect(self.ball_x, self.ball_y, self.ball_size, self.ball_size, 9)

        # ブロックを描画
        for block in self.blocks:
            if block[2]:  # 生きているブロックのみ
                pyxel.rect(block[0], block[1], 20, 10, 8)

        # スコアとライフを表示
        pyxel.text(10, 10, f"Score: {self.score}", 7)
        pyxel.text(100, 10, f"Lives: {self.lives}", 7)

# ゲームの実行
BreakoutGame()
