import pyxel
import random

WIDTH = 256
HEIGHT = 160
SCROLL_SPEED = 1.8

class App:
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, title="Complex Cave Flyer", fps=60)
        self.debug = False
        self.reset()
        pyxel.run(self.update, self.draw)
    
    def reset(self):
        self.px = 50
        self.py = HEIGHT // 2
        self.score = 0
        self.game_over = False
        self.speed = SCROLL_SPEED
        self.gap_center = HEIGHT // 2
        self.gap_size = 115
        
        self.top_points = []
        self.bottom_points = []
        self.generate_initial_terrain()
    
    def generate_initial_terrain(self):
        self.top_points.clear()
        self.bottom_points.clear()
        x = 0
        for i in range(35):
            top = self.gap_center - self.gap_size // 2
            bottom = self.gap_center + self.gap_size // 2
            self.top_points.append([x, max(10, top)])
            self.bottom_points.append([x, min(HEIGHT-10, bottom)])
            x += 17
    
    def update_terrain(self):
        for p in self.top_points: p[0] -= self.speed
        for p in self.bottom_points: p[0] -= self.speed
        
        if self.top_points[0][0] < -40:
            self.top_points.pop(0)
            self.bottom_points.pop(0)
        
        if self.top_points[-1][0] < WIDTH + 40:
            difficulty = self.score // 45   # 上昇ペースを少し緩やかに
            
            # 最小幅を広めに調整（ここがメイン修正）
            self.gap_size = max(68, 122 - difficulty * 2.8)
            
            # 隙間中心の動き（予測しにくく）
            self.gap_center += random.randint(-24, 24)
            self.gap_center = max(HEIGHT//2 - 38, min(HEIGHT//2 + 38, self.gap_center))
            
            new_top = self.gap_center - self.gap_size // 2
            new_bottom = self.gap_center + self.gap_size // 2
            
            self.top_points.append([self.top_points[-1][0] + 17, max(10, int(new_top))])
            self.bottom_points.append([self.bottom_points[-1][0] + 17, min(HEIGHT-10, int(new_bottom))])
    
    def update(self):
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset()
            return
        
        speed = 2.8
        if pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W):   self.py -= speed
        if pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S): self.py += speed
        if pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A): self.px -= speed * 0.9
        if pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D): self.px += speed * 1.1
        
        self.px = max(15, min(WIDTH - 28, self.px))
        self.py = max(12, min(HEIGHT - 15, self.py))
        
        self.score += 1
        if self.score % 65 == 0 and self.speed < 3.7:
            self.speed += 0.05
        
        self.update_terrain()
        self.check_collision()
    
    def get_terrain_height(self, points, x):
        for i in range(len(points)-1):
            x1, y1 = points[i]
            x2, y2 = points[i+1]
            if x1 <= x <= x2:
                t = (x - x1) / (x2 - x1)
                return y1 + (y2 - y1) * t
        return points[-1][1]
    
    def check_collision(self):
        hit_left   = self.px + 3
        hit_right  = self.px + 11
        hit_top    = self.py + 2
        hit_bottom = self.py + 7
        
        top_y = max(
            self.get_terrain_height(self.top_points, hit_left),
            self.get_terrain_height(self.top_points, hit_right)
        )
        bottom_y = min(
            self.get_terrain_height(self.bottom_points, hit_left),
            self.get_terrain_height(self.bottom_points, hit_right)
        )
        
        if hit_top < top_y + 3 or hit_bottom > bottom_y - 3:
            self.game_over = True
    
    def draw(self):
        pyxel.cls(0)
        
        for i in range(len(self.top_points)-1):
            x1, t1 = self.top_points[i]
            x2, t2 = self.top_points[i+1]
            b1 = self.bottom_points[i][1]
            b2 = self.bottom_points[i+1][1]
            
            pyxel.rect(x1, 0, x2 - x1 + 2, max(t1, t2) + 2, 1)
            pyxel.rect(x1, min(b1, b2) - 2, x2 - x1 + 2, HEIGHT + 2, 1)
        
        pyxel.tri(self.px+14, self.py+4, self.px, self.py, self.px, self.py+8, 8)
        pyxel.rect(self.px+3, self.py+2, 10, 5, 7)
        pyxel.rect(self.px+10, self.py+3, 4, 3, 10)
        
        pyxel.text(6, 6, f"SCORE {self.score//8:05d}", 7)
        pyxel.text(6, 16, f"SPEED {self.speed:.1f}", 13)
        
        if self.game_over:
            pyxel.text(WIDTH//2-38, HEIGHT//2-10, "GAME OVER", 8)
            pyxel.text(WIDTH//2-48, HEIGHT//2+10, "PRESS R TO RESTART", 7)

App()