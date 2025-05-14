import pyxel

class SquashGame:
    def __init__(self):
        # 画面サイズを設定（160x120はレトロ感に最適）
        pyxel.init(160, 120, title="Squash Game")
        # リソースファイルの読み込み（ラケットやボールのスプライト）
        pyxel.load("squash.pyxres")
        
        # プレイヤー（ラケット）の初期位置
        self.paddle_x = 70
        self.paddle_y = 100
        self.paddle_width = 16
        self.paddle_height = 4
        
        # ボールの初期位置と速度
        self.ball_x = 80
        self.ball_y = 60
        self.ball_speed_x = 2
        self.ball_speed_y = -2
        self.ball_size = 4
        
        # スコア
        self.score = 0
        
        # ゲームループ開始
        pyxel.run(self.update, self.draw)

    def update(self):
        # プレイヤーの移動（左右キーでラケットを動かす）
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

        # ラケットとの衝突判定
        if (self.ball_y + self.ball_size >= self.paddle_y and
            self.paddle_x <= self.ball_x <= self.paddle_x + self.paddle_width):
            self.ball_speed_y = -self.ball_speed_y
            self.score += 1

        # ボールが下に落ちた場合（ゲームオーバーまたはリセット）
        if self.ball_y >= pyxel.height:
            self.ball_x = 80
            self.ball_y = 60
            self.ball_speed_x = 2
            self.ball_speed_y = -2
            self.score = 0

    def draw(self):
        # 画面をクリア
        pyxel.cls(0)
        
        # コートの壁を描画（シンプルな線で表現）
        pyxel.rectb(0, 0, pyxel.width, pyxel.height, 7)  # 白い枠
        
        # ラケットを描画（スプライトまたは矩形で）
        pyxel.rect(self.paddle_x, self.paddle_y, self.paddle_width, self.paddle_height, 11)
        
        # ボールを描画
        pyxel.rect(self.ball_x, self.ball_y, self.ball_size, self.ball_size, 9)
        
        # スコアを表示
        pyxel.text(10, 10, f"Score: {self.score}", 7)

# ゲームの実行
SquashGame()
