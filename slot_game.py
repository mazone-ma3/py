import pyxel
import random

class SlotGame:
    def __init__(self):
        # 画面初期化（160x120ピクセル）
        pyxel.init(160, 120, title="Pyxel Slot Game")
        # リソースファイルの読み込み（スプライトやサウンド）
        pyxel.load("slot_game.pyxres")
        # リールの状態（0: チェリー, 1: 7, 2: BAR）
        self.reels = [0, 0, 0]
        # スピンの状態
        self.is_spinning = False
        self.spin_timer = 0
        # プレイヤーのコイン
        self.coins = 100
        # ゲームループ開始
        pyxel.run(self.update, self.draw)

    def update(self):
        # スピンボタン（スペースキー）
        if pyxel.btnp(pyxel.KEY_SPACE) and not self.is_spinning and self.coins >= 10:
            self.is_spinning = True
            self.spin_timer = 30  # スピンの長さ（フレーム数）
            self.coins -= 10  # ベット

        # スピン中の処理
        if self.is_spinning:
            self.spin_timer -= 1
            if self.spin_timer % 5 == 0:  # 高速でシンボルを変更
                self.reels = [random.randint(0, 2) for _ in range(3)]
            if self.spin_timer <= 0:
                self.is_spinning = False
                # 勝利判定
                if self.reels[0] == self.reels[1] == self.reels[2]:
                    self.coins += 50  # 同じシンボルなら報酬
                    pyxel.play(0, 0)  # 勝利サウンド

    def draw(self):
        # 画面クリア
        pyxel.cls(0)
        # リールの描画（スプライトを仮定）
        for i, symbol in enumerate(self.reels):
            # シンボルに応じたスプライトを描画（仮のUV座標）
            uv = [(0, 0), (16, 0), (32, 0)][symbol]  # チェリー, 7, BAR
            pyxel.blt(40 + i * 32, 40, 0, uv[0], uv[1], 16, 16, 0)
        # コインとUIの表示
        pyxel.text(10, 10, f"Coins: {self.coins}", 7)
        pyxel.text(10, 100, "Press SPACE to spin!", 7)
        # スピン中のアニメーション（簡易）
        if self.is_spinning:
            pyxel.text(50, 80, "Spinning...", 10)

# ゲーム開始
SlotGame()
