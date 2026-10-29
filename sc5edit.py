import os
import pyxel

# MSX2の標準16色パレット（24ビットRGB）
MSX2_PALETTE = [
    0x000000,
    0x010101,
    0x33CC33,
    0x66FF66,
    0x3333FF,
    0x6666FF,
    0xCC3333,
    0x33CCCC,
    0xFF3333,
    0xFF6666,
    0xCCCC33,
    0xFFFF66,
    0x228822,
    0xCC33CC,
    0x888888,
    0xFFFFFF,
]


class MSX2OriginalEditor:

  def __init__(self):
    pyxel.init(256, 248, title="MSX2 SCREEN5 Editor (Pyxel)", fps=60)
    for i, col in enumerate(MSX2_PALETTE):
      pyxel.colors[i] = col

    self.si = 16  # サイズ (8, 16, 32)
    self.sz = 8  # 拡大表示時のドットサイズ
    self.update_zoom()

    self.current_color = 15  # 初期カラー: 白
    self.cursor_x = 0
    self.cursor_y = 0

    self.filename = ""
    self.message = "READY"
    self.msg_timer = 0

    # モード管理: "EDIT", "PUT", "GET", "SWAP_1", "SWAP_2", "PROMPT_SAVE", "PROMPT_LOAD"
    self.mode = "EDIT"
    self.screen_x = 0
    self.screen_y = 0
    self.swap_x1 = 0
    self.swap_y1 = 0

    self.input_lock = 0

    pyxel.run(self.update, self.draw)

  def update_zoom(self):
    if self.si == 8:
      self.sz = 16
    elif self.si == 16:
      self.sz = 8
    else:
      self.sz = 4

  def update(self):
    if self.input_lock > 0:
      self.input_lock -= 1

    # --- ファイル名入力プロンプトモードの処理 ---
    if self.mode in ["PROMPT_SAVE", "PROMPT_LOAD"]:
      if pyxel.btnp(pyxel.KEY_ESCAPE):
        self.mode = "EDIT"
        self.input_lock = 15
        self.set_message("CANCELLED")
        return

      if pyxel.btnp(pyxel.KEY_BACKSPACE):
        if len(self.filename) > 0:
          self.filename = self.filename[:-1]

      elif pyxel.btnp(pyxel.KEY_RETURN):
        if len(self.filename) == 0:
          self.mode = "EDIT"
          self.input_lock = 15
          self.set_message("CANCELLED")
        else:
          target_file = self.filename + ".sc5"
          if self.mode == "PROMPT_SAVE":
            self.save_sc5(target_file)
            self.set_message(f"SAVED: {target_file}")
          else:
            self.load_sc5(target_file)
            self.set_message(f"LOADED: {target_file}")

          self.mode = "EDIT"
          self.input_lock = 15
        return

      else:
        for key, char in [
            (pyxel.KEY_A, "A"),
            (pyxel.KEY_B, "B"),
            (pyxel.KEY_C, "C"),
            (pyxel.KEY_D, "D"),
            (pyxel.KEY_E, "E"),
            (pyxel.KEY_F, "F"),
            (pyxel.KEY_G, "G"),
            (pyxel.KEY_H, "H"),
            (pyxel.KEY_I, "I"),
            (pyxel.KEY_J, "J"),
            (pyxel.KEY_K, "K"),
            (pyxel.KEY_L, "L"),
            (pyxel.KEY_M, "M"),
            (pyxel.KEY_N, "N"),
            (pyxel.KEY_O, "O"),
            (pyxel.KEY_P, "P"),
            (pyxel.KEY_Q, "Q"),
            (pyxel.KEY_R, "R"),
            (pyxel.KEY_S, "S"),
            (pyxel.KEY_T, "T"),
            (pyxel.KEY_U, "U"),
            (pyxel.KEY_V, "V"),
            (pyxel.KEY_W, "W"),
            (pyxel.KEY_X, "X"),
            (pyxel.KEY_Y, "Y"),
            (pyxel.KEY_Z, "Z"),
            (pyxel.KEY_0, "0"),
            (pyxel.KEY_1, "1"),
            (pyxel.KEY_2, "2"),
            (pyxel.KEY_3, "3"),
            (pyxel.KEY_4, "4"),
            (pyxel.KEY_5, "5"),
            (pyxel.KEY_6, "6"),
            (pyxel.KEY_7, "7"),
            (pyxel.KEY_8, "8"),
            (pyxel.KEY_9, "9"),
            (pyxel.KEY_PERIOD, "."),
            (pyxel.KEY_MINUS, "-"),
        ]:
          if pyxel.btnp(key):
            if len(self.filename) < 12:
              self.filename += char
      return

    # --- 1. サイズ変更 ([1]?[3]キー) ---
    if pyxel.btnp(pyxel.KEY_1):
      self.si = 8
      self.update_zoom()
      self.cursor_x = min(self.cursor_x, self.si - 1)
      self.cursor_y = min(self.cursor_y, self.si - 1)
      self.set_message("SIZE: 8x8")
    elif pyxel.btnp(pyxel.KEY_2):
      self.si = 16
      self.update_zoom()
      self.cursor_x = min(self.cursor_x, self.si - 1)
      self.cursor_y = min(self.cursor_y, self.si - 1)
      self.set_message("SIZE: 16x16")
    elif pyxel.btnp(pyxel.KEY_3):
      self.si = 32
      self.update_zoom()
      self.cursor_x = min(self.cursor_x, self.si - 1)
      self.cursor_y = min(self.cursor_y, self.si - 1)
      self.set_message("SIZE: 32x32")

    # --- 2. カラー選択 (< / > キー：Comma / Period) ---
    if pyxel.btnp(pyxel.KEY_PERIOD):
      self.current_color = (self.current_color + 1) % 16
    elif pyxel.btnp(pyxel.KEY_COMMA):
      self.current_color = (self.current_color - 1) % 16

    if self.mode == "EDIT":
      # 3. 拡大エディタ内の操作
      if pyxel.btnp(pyxel.KEY_LEFT, hold=5, repeat=5):
        self.cursor_x = max(0, self.cursor_x - 1)
      if pyxel.btnp(pyxel.KEY_RIGHT, hold=5, repeat=5):
        self.cursor_x = min(self.si - 1, self.cursor_x + 1)
      if pyxel.btnp(pyxel.KEY_UP, hold=5, repeat=5):
        self.cursor_y = max(0, self.cursor_y - 1)
      if pyxel.btnp(pyxel.KEY_DOWN, hold=5, repeat=5):
        self.cursor_y = min(self.si - 1, self.cursor_y + 1)

      if self.input_lock == 0:
        if pyxel.btn(pyxel.KEY_SPACE):
          pyxel.images[0].pset(self.cursor_x, self.cursor_y, self.current_color)

      if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        limit = self.si * self.sz
        if 0 <= mx < limit and 0 <= my < limit:
          self.cursor_x = mx // self.sz
          self.cursor_y = my // self.sz
          pyxel.images[0].pset(self.cursor_x, self.cursor_y, self.current_color)

    else:
      # 4. 全画面選択モード（PUT / GET / SWAP）
      step = 8 if pyxel.btn(pyxel.KEY_SHIFT) else self.si

      if pyxel.btnp(pyxel.KEY_LEFT, hold=5, repeat=5):
        self.screen_x = max(0, self.screen_x - step)
      if pyxel.btnp(pyxel.KEY_RIGHT, hold=5, repeat=5):
        self.screen_x = min(256 - self.si, self.screen_x + step)
      if pyxel.btnp(pyxel.KEY_UP, hold=5, repeat=5):
        self.screen_y = max(0, self.screen_y - step)
      if pyxel.btnp(pyxel.KEY_DOWN, hold=5, repeat=5):
        self.screen_y = min(212 - self.si, self.screen_y + step)

      # RETURNでキャンセル
      if pyxel.btnp(pyxel.KEY_RETURN):
        self.mode = "EDIT"
        self.input_lock = 15
        self.set_message("CANCELLED")

      # SPACEで決定・実行
      elif pyxel.btnp(pyxel.KEY_SPACE) and self.input_lock == 0:
        if self.mode == "PUT":
          # CTRLキーが押されていれば「TPSET（カラー0を透過）」、押されていなければ通常PUT
          is_transparent = pyxel.btn(pyxel.KEY_CTRL)
          for y in range(self.si):
            for x in range(self.si):
              col = pyxel.images[0].pget(x, y)
              if is_transparent and col == 0:
                continue  # 透過時はカラー0を上書きしない
              pyxel.images[1].pset(self.screen_x + x, self.screen_y + y, col)
          
          mode_str = "TPSET (TRANS)" if is_transparent else "PUT"
          self.set_message(f"{mode_str} STAMPED! (SPACE:CONT / RET:EXIT)")

        elif self.mode == "GET":
          for y in range(self.si):
            for x in range(self.si):
              col = pyxel.images[1].pget(self.screen_x + x, self.screen_y + y)
              pyxel.images[0].pset(x, y, col)
          self.set_message("GET COMPLETED!")
          self.mode = "EDIT"
          self.input_lock = 15

        elif self.mode == "SWAP_1":
          self.swap_x1 = self.screen_x
          self.swap_y1 = self.screen_y
          self.mode = "SWAP_2"
          self.input_lock = 10
          self.set_message("SELECT 2nd POS (SPACE:SWAP / RET:CANCEL)")

        elif self.mode == "SWAP_2":
          for y in range(self.si):
            for x in range(self.si):
              c1 = pyxel.images[1].pget(self.swap_x1 + x, self.swap_y1 + y)
              c2 = pyxel.images[1].pget(self.screen_x + x, self.screen_y + y)
              pyxel.images[1].pset(self.swap_x1 + x, self.swap_y1 + y, c2)
              pyxel.images[1].pset(self.screen_x + x, self.screen_y + y, c1)
          self.set_message("SWAP COMPLETED! (SELECT NEXT)")
          self.mode = "SWAP_1"
          self.input_lock = 10

    # --- ファンクションキー割当 ---
    if pyxel.btnp(pyxel.KEY_F1):  # BOX
      for y in range(self.si):
        for x in range(self.si):
          pyxel.images[0].pset(x, y, self.current_color)
      self.set_message("<BOX> FILLED")

    elif pyxel.btnp(pyxel.KEY_F2):  # PUT (GRPH代わりのCTRL+SPACEで透過PUT可能)
      self.mode = "PUT"
      self.input_lock = 10
      self.set_message("<PUT> SPACE:STAMP (CTRL+SPACE:TPSET)")

    elif pyxel.btnp(pyxel.KEY_F3):  # GET
      self.mode = "GET"
      self.input_lock = 10
      self.set_message("<GET> SPACE:CAPTURE / RET:EXIT")

    elif pyxel.btnp(pyxel.KEY_F4):  # SAVE
      self.filename = ""
      self.mode = "PROMPT_SAVE"
      self.set_message("INPUT FILENAME & HIT ENTER (EMPTY=CANCEL)")

    elif pyxel.btnp(pyxel.KEY_F5):  # LOAD
      self.filename = ""
      self.mode = "PROMPT_LOAD"
      self.set_message("INPUT FILENAME & HIT ENTER (EMPTY=CANCEL)")

    elif pyxel.btnp(pyxel.KEY_F6):  # R-L TURN
      for y in range(self.si):
        row = [pyxel.images[0].pget(x, y) for x in range(self.si)]
        for x in range(self.si):
          pyxel.images[0].pset(x, y, row[self.si - 1 - x])
      self.set_message("<R-L TURN>")

    elif pyxel.btnp(pyxel.KEY_F7):  # U-D TURN
      for x in range(self.si):
        col = [pyxel.images[0].pget(x, y) for y in range(self.si)]
        for y in range(self.si):
          pyxel.images[0].pset(x, y, col[self.si - 1 - y])
      self.set_message("<U-D TURN>")

    elif pyxel.btnp(pyxel.KEY_F8):  # SWAP
      self.mode = "SWAP_1"
      self.input_lock = 10
      self.set_message("<SWAP> SELECT 1st POS (SPACE:DECIDE)")

    if self.msg_timer > 0:
      self.msg_timer -= 1

  def set_message(self, text):
    self.message = text
    self.msg_timer = 120

  def save_sc5(self, filename):
    data = bytearray([0xFE, 0x00, 0x00, 0xFF, 0x69, 0x00, 0x00])
    for y in range(212):
      for x in range(0, 256, 2):
        c1 = pyxel.images[1].pget(x, y) & 0x0F
        c2 = pyxel.images[1].pget(x + 1, y) & 0x0F
        data.append((c1 << 4) | c2)
    with open(filename, "wb") as f:
      f.write(data)

  def load_sc5(self, filename):
    if not os.path.exists(filename):
      self.set_message("FILE NOT FOUND")
      return
    with open(filename, "rb") as f:
      header = f.read(7)
      pixel_data = f.read()
      if header[0] != 0xFE:
        f.seek(0)
        pixel_data = f.read()
      idx = 0
      for y in range(212):
        for x in range(0, 256, 2):
          if idx < len(pixel_data):
            b = pixel_data[idx]
            idx += 1
            pyxel.images[1].pset(x, y, (b >> 4) & 0x0F)
            if x + 1 < 256:
              pyxel.images[1].pset(x + 1, y, b & 0x0F)

  def draw(self):
    pyxel.cls(0)

    limit = self.si * self.sz

    if self.mode == "EDIT":
      for y in range(self.si):
        for x in range(self.si):
          col = pyxel.images[0].pget(x, y)
          
          # カラー0（透明色）の場合は市松模様を描画
          if col == 0:
            for py_sub in range(self.sz):
              for px_sub in range(self.sz):
                c_check = 1 if ((x * self.sz + px_sub) // 2 + (y * self.sz + py_sub) // 2) % 2 == 0 else 0
                draw_c = 14 if c_check == 1 else 1
                pyxel.pset(x * self.sz + px_sub, y * self.sz + py_sub, draw_c)
          else:
            pyxel.rect(x * self.sz, y * self.sz, self.sz, self.sz, col)

      for i in range(self.si + 1):
        pyxel.line(0, i * self.sz, limit, i * self.sz, 13)
        pyxel.line(i * self.sz, 0, i * self.sz, limit, 13)

      pyxel.rectb(
          self.cursor_x * self.sz,
          self.cursor_y * self.sz,
          self.sz,
          self.sz,
          7,
      )

      # 右側原寸プレビュー
      rx, ry = 160, 16
      pyxel.rectb(rx - 1, ry - 1, self.si + 2, self.si + 2, 7)
      pyxel.text(rx, ry - 10, "ACTUAL SIZE", 13)

      for y in range(self.si):
        for x in range(self.si):
          c = pyxel.images[0].pget(x, y)
          pyxel.pset(rx + x, ry + y, c)

    else:
      # 全画面（256x212）を表示
      pyxel.blt(0, 0, 1, 0, 0, 256, 212)
      box_col = (
          11
          if self.mode == "PUT"
          else (7 if self.mode == "GET" else (8 if self.mode == "SWAP_1" else 9))
      )
      pyxel.rectb(self.screen_x, self.screen_y, self.si, self.si, box_col)

    # --- 下部ステータス（212?248ドット目） ---
    pyxel.rect(0, 212, 256, 36, 1)

    for i in range(16):
      px = i * 12
      py = 214
      if i == 0:
        for sub_y in range(8):
          for sub_x in range(10):
            c_check = 1 if (sub_x // 2 + sub_y // 2) % 2 == 0 else 0
            d_col = 14 if c_check == 1 else 1
            pyxel.pset(px + sub_x, py + sub_y, d_col)
        pyxel.text(px + 2, py + 1, "0", 7)
      else:
        pyxel.rect(px, py, 10, 8, i)

    pyxel.rectb(self.current_color * 12, 214, 10, 8, 7)

    pyxel.text(
        2,
        225,
        f"MODE:{self.mode} COL:{self.current_color:X} (<,>)",
        7,
    )
    pyxel.text(
        2,
        237,
        self.message,
        11
        if "SAVED" in self.message or "COMPLETED" in self.message
        else 13,
    )

    pyxel.text(130, 225, "F1:BOX F2:PUT F3:GET F4:SAV F5:LOD", 6)
    pyxel.text(130, 237, "F6:R-L F7:U-D F8:SWAP [1-3]SIZE", 6)

    # --- プロンプト表示（ファイル名入力中） ---
    if self.mode in ["PROMPT_SAVE", "PROMPT_LOAD"]:
      pyxel.rect(40, 90, 176, 40, 1)
      pyxel.rectb(40, 90, 176, 40, 7)
      title_str = "SAVE FILE NAME:" if self.mode == "PROMPT_SAVE" else "LOAD FILE NAME:"
      pyxel.text(48, 96, title_str, 11)
      pyxel.text(48, 110, f"> {self.filename}_", 7)


MSX2OriginalEditor()