import pyxel

MAP_WIDTH = 128     # マップの横幅（ブロック単位）
MAP_HEIGHT = 120    # マップの高さ（ブロック単位）
HEADER_SIZE = 7     # ヘッダーサイズ
PATTERN_OFFSET = 7 + 0x3c00  # 2x2パターン定義の開始位置

class CompleteMapEditor:
    def __init__(self):
        pyxel.init(256, 256, fps=30, title="ELMSTMAP Complete Editor")
        pyxel.load("map.pyxres")
        pyxel.mouse(True)  # マウスカーソルを有効化

        try:
            with open('ELMSTMAP.MDT', 'rb') as f:
                self.raw_data = bytearray(f.read())
        except FileNotFoundError:
            total_size = HEADER_SIZE + (MAP_WIDTH * MAP_HEIGHT) + (256 * 4)
            self.raw_data = bytearray(total_size)

        self.mode = 'map'

        # --- マップ編集用変数 ---
        self.cursor_x = 0
        self.cursor_y = 0
        self.cam_x = 0
        self.cam_y = 0
        self.selected_pattern = 0  # 選択中の論理パターンID (0?255)

        # --- パターン定義編集用変数 ---
        self.editing_pattern_id = 0
        self.selected_slot = 0

        # --- 誤作動防止用ウェイトカウンター ---
        self.input_lock_timer = 0

        pyxel.run(self.update, self.draw)

    # 上下4bitを入れ替える関数
    def swap_bits(self, val):
        return ((val & 0x0F) << 4) | ((val & 0xF0) >> 4)

    def update(self):
        if self.input_lock_timer > 0:
            self.input_lock_timer -= 1

        # --- モード切替 (TAB) ---
        if pyxel.btnp(pyxel.KEY_TAB) and self.input_lock_timer == 0:
            if self.mode == 'map':
                self.mode = 'pattern_edit'
                self.input_lock_timer = 10
            elif self.mode == 'pattern_edit':
                self.mode = 'map'
                self.input_lock_timer = 10

        # Sキーで上書き保存
        if pyxel.btnp(pyxel.KEY_S):
            self.save_map()

        if self.mode == 'map':
            self.update_map_mode()
        elif self.mode == 'pattern_edit':
            self.update_pattern_mode()
        elif self.mode == 'catalog_pattern':
            self.update_catalog_pattern_mode()
        elif self.mode == 'catalog_tile':
            self.update_catalog_tile_mode()

    def update_map_mode(self):
        if pyxel.btnp(pyxel.KEY_LEFT, hold=10, repeat=5):
            self.cursor_x = max(0, self.cursor_x - 1)
        if pyxel.btnp(pyxel.KEY_RIGHT, hold=10, repeat=5):
            self.cursor_x = min(MAP_WIDTH - 1, self.cursor_x + 1)
        if pyxel.btnp(pyxel.KEY_UP, hold=10, repeat=5):
            self.cursor_y = max(0, self.cursor_y - 1)
        if pyxel.btnp(pyxel.KEY_DOWN, hold=10, repeat=5):
            self.cursor_y = min(MAP_HEIGHT - 1, self.cursor_y + 1)

        if self.input_lock_timer == 0:
            if pyxel.btn(pyxel.KEY_SPACE):
                idx = HEADER_SIZE + self.cursor_x + self.cursor_y * MAP_WIDTH
                if idx < PATTERN_OFFSET:
                    self.raw_data[idx] = self.swap_bits(self.selected_pattern)

            if pyxel.btn(pyxel.MOUSE_BUTTON_LEFT):
                if pyxel.mouse_y < 208:
                    mx = self.cam_x + pyxel.mouse_x // 16
                    my = self.cam_y + pyxel.mouse_y // 16
                    if 0 <= mx < MAP_WIDTH and 0 <= my < MAP_HEIGHT:
                        self.cursor_x = mx
                        self.cursor_y = my
                        idx = HEADER_SIZE + mx + my * MAP_WIDTH
                        if idx < PATTERN_OFFSET:
                            self.raw_data[idx] = self.swap_bits(self.selected_pattern)

        if pyxel.btnp(pyxel.KEY_F) and self.input_lock_timer == 0:
            self.flood_fill(self.cursor_x, self.cursor_y, self.selected_pattern)

        if pyxel.btnp(pyxel.KEY_P) and self.input_lock_timer == 0:
            self.mode = 'catalog_pattern'
            self.input_lock_timer = 10

        # カメラ追従
        view_w, view_h = 32, 26
        if self.cursor_x < self.cam_x:
            self.cam_x = self.cursor_x
        elif self.cursor_x >= self.cam_x + view_w // 2:
            self.cam_x = self.cursor_x - view_w // 2 + 1
        if self.cursor_y < self.cam_y:
            self.cam_y = self.cursor_y
        elif self.cursor_y >= self.cam_y + view_h // 2:
            self.cam_y = self.cursor_y - view_h // 2 + 1

        self.cam_x = max(0, min(self.cam_x, MAP_WIDTH - view_w // 2))
        self.cam_y = max(0, min(self.cam_y, MAP_HEIGHT - view_h // 2))

    def update_pattern_mode(self):
        if pyxel.btnp(pyxel.KEY_Z, hold=10, repeat=5):
            self.editing_pattern_id = (self.editing_pattern_id - 1) % 256
        if pyxel.btnp(pyxel.KEY_X, hold=10, repeat=5):
            self.editing_pattern_id = (self.editing_pattern_id + 1) % 256

        if pyxel.btnp(pyxel.KEY_SPACE) and self.input_lock_timer == 0:
            self.selected_slot = (self.selected_slot + 1) % 4

        if pyxel.btnp(pyxel.KEY_P) and self.input_lock_timer == 0:
            self.mode = 'catalog_tile'
            self.input_lock_timer = 10

    def update_catalog_pattern_mode(self):
        if self.input_lock_timer == 0 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if 0 <= mx < 256 and 0 <= my < 256:
                gx = mx // 16
                gy = my // 16
                self.selected_pattern = gx + gy * 16
                self.mode = 'map'
                self.input_lock_timer = 15

        if (pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_ESCAPE)) and self.input_lock_timer == 0:
            self.mode = 'map'
            self.input_lock_timer = 10

    def update_catalog_tile_mode(self):
        if self.input_lock_timer == 0 and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            if 0 <= mx < 256 and 0 <= my < 256:
                gx = mx // 16
                gy = my // 16
                chosen_tile = gx + gy * 16

                tiles = self.get_pattern_tiles(self.editing_pattern_id)
                tiles[self.selected_slot] = chosen_tile
                self.set_pattern_tiles(self.editing_pattern_id, tiles)
                self.mode = 'pattern_edit'
                self.input_lock_timer = 15

        if (pyxel.btnp(pyxel.KEY_P) or pyxel.btnp(pyxel.KEY_ESCAPE)) and self.input_lock_timer == 0:
            self.mode = 'pattern_edit'
            self.input_lock_timer = 10

    def get_map_pattern_id(self, x, y):
        idx = HEADER_SIZE + x + y * MAP_WIDTH
        if idx < PATTERN_OFFSET and idx < len(self.raw_data):
            raw_val = self.raw_data[idx]
            return self.swap_bits(raw_val)
        return 0

    def flood_fill(self, start_x, start_y, new_pattern):
        start_idx = HEADER_SIZE + start_x + start_y * MAP_WIDTH
        if start_idx >= PATTERN_OFFSET:
            return
        target_pattern = self.get_map_pattern_id(start_x, start_y)
        if target_pattern == new_pattern:
            return

        stack = [(start_x, start_y)]
        visited = set()

        while stack:
            x, y = stack.pop()
            if (x, y) in visited:
                continue
            if not (0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT):
                continue

            current_pat = self.get_map_pattern_id(x, y)
            if current_pat != target_pattern:
                continue

            idx = HEADER_SIZE + x + y * MAP_WIDTH
            self.raw_data[idx] = self.swap_bits(new_pattern)
            visited.add((x, y))

            stack.append((x + 1, y))
            stack.append((x - 1, y))
            stack.append((x, y + 1))
            stack.append((x, y - 1))

    def get_pattern_tiles(self, pattern_id):
        offset = PATTERN_OFFSET + pattern_id * 4
        if offset + 3 < len(self.raw_data):
            return [self.raw_data[offset], self.raw_data[offset+1], self.raw_data[offset+2], self.raw_data[offset+3]]
        return [0, 0, 0, 0]

    def set_pattern_tiles(self, pattern_id, tiles):
        offset = PATTERN_OFFSET + pattern_id * 4
        if offset + 3 < len(self.raw_data):
            self.raw_data[offset] = tiles[0]
            self.raw_data[offset+1] = tiles[1]
            self.raw_data[offset+2] = tiles[2]
            self.raw_data[offset+3] = tiles[3]

    def save_map(self):
        with open('ELMSTMAP.MDT', 'wb') as f:
            f.write(self.raw_data)
        print("Saved ELMSTMAP.MDT successfully!")

    def draw(self):
        pyxel.cls(0)

        if self.mode == 'map':
            self.draw_map_mode()
        elif self.mode == 'pattern_edit':
            self.draw_pattern_mode()
        elif self.mode == 'catalog_pattern':
            self.draw_catalog_pattern_mode()
        elif self.mode == 'catalog_tile':
            self.draw_catalog_tile_mode()

    def draw_map_mode(self):
        view_w, view_h = 32, 26
        for y in range(view_h // 2 + 1):
            for x in range(view_w // 2 + 1):
                mx, my = self.cam_x + x, self.cam_y + y
                if mx < MAP_WIDTH and my < MAP_HEIGHT:
                    pattern_id = self.get_map_pattern_id(mx, my)
                    tiles = self.get_pattern_tiles(pattern_id)
                    px, py = (mx - self.cam_x) * 16, (my - self.cam_y) * 16
                    for i, t in enumerate(tiles):
                        tx, ty = i % 2, i // 2
                        cx, cy = t % 16, int(t / 16)
                        pyxel.blt(px + tx * 8, py + ty * 8, 1, cx * 8, cy * 8, 8, 8, 0)

        cx = (self.cursor_x - self.cam_x) * 16
        cy = (self.cursor_y - self.cam_y) * 16
        pyxel.rectb(cx, cy, 16, 16, 7)

        pyxel.rect(0, 208, 256, 48, 1)
        pyxel.text(4, 212, "[MODE] MAP EDIT (TAB -> Pattern Edit)", 9)
        pyxel.text(4, 224, f"POS: ({self.cursor_x}, {self.cursor_y})  PATTERN: {self.selected_pattern}", 7)
        pyxel.text(4, 236, "[P] Catalog | [SPACE] Paint | [F] Fill | [S] Save", 11)

        tiles = self.get_pattern_tiles(self.selected_pattern)
        for i, t in enumerate(tiles):
            tx, ty = i % 2, i // 2
            cx, cy = t % 16, int(t / 16)
            pyxel.blt(220 + tx * 8, 216 + ty * 8, 1, cx * 8, cy * 8, 8, 8, 0)
        pyxel.rectb(219, 215, 18, 18, 7)

    def draw_pattern_mode(self):
        pyxel.rect(0, 208, 256, 48, 1)
        pyxel.text(4, 212, "[MODE] PATTERN EDIT (TAB -> Map Edit)", 10)
        pyxel.text(4, 224, f"EDIT PATTERN ID: {self.editing_pattern_id}  SLOT: {['Top-Left', 'Top-Right', 'Bottom-Left', 'Bottom-Right'][self.selected_slot]}", 7)
        pyxel.text(4, 236, "[Z/X] Change ID | [SPACE] Next Slot | [P] Tile Catalog | [S] Save", 11)

        tiles = self.get_pattern_tiles(self.editing_pattern_id)
        base_px, base_py = 112, 80  # 画面中央に配置

        # 2x2パターン（16x16ドット）として正しくプレビュー描画
        for i, t in enumerate(tiles):
            tx, ty = i % 2, i // 2
            cx, cy = t % 16, int(t / 16)
            pyxel.blt(base_px + tx * 8, base_py + ty * 8, 1, cx * 8, cy * 8, 8, 8, 0)

        # 選択中のスロットを囲む枠線（8x8タイル単位）
        sel_tx, sel_ty = self.selected_slot % 2, self.selected_slot // 2
        pyxel.rectb(base_px + sel_tx * 8 - 1, base_py + sel_ty * 8 - 1, 10, 10, 8)
        
        pyxel.text(base_px - 24, base_py + 20, f"Current Tile ID: {tiles[self.selected_slot]}", 7)

    def draw_catalog_pattern_mode(self):
        for i in range(256):
            gx, gy = i % 16, i // 16
            px, py = gx * 16, gy * 16
            tiles = self.get_pattern_tiles(i)
            for j, t in enumerate(tiles):
                tx, ty = j % 2, j // 2
                cx, cy = t % 16, int(t / 16)
                pyxel.blt(px + tx * 8, py + ty * 8, 1, cx * 8, cy * 8, 8, 8, 0)
            pyxel.rectb(px, py, 16, 16, 5)
            if i == self.selected_pattern:
                pyxel.rectb(px, py, 16, 16, 8)

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if 0 <= mx < 256 and 0 <= my < 256:
            pyxel.rectb((mx // 16) * 16, (my // 16) * 16, 16, 16, 7)

    def draw_catalog_tile_mode(self):
        for i in range(256):
            gx, gy = i % 16, i // 16
            px, py = gx * 16, gy * 16
            cx, cy = i % 16, int(i / 16)
            pyxel.blt(px, py, 1, cx * 8, cy * 8, 8, 8, 0)
            pyxel.rectb(px, py, 16, 16, 5)

        mx, my = pyxel.mouse_x, pyxel.mouse_y
        if 0 <= mx < 256 and 0 <= my < 256:
            pyxel.rectb((mx // 16) * 16, (my // 16) * 16, 16, 16, 7)

CompleteMapEditor()