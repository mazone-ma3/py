import pyxel
import random

class Othello:
    def __init__(self):
        pyxel.init(160, 160, title="Othello")
        pyxel.mouse(True)
        self.board = [[0 for _ in range(8)] for _ in range(8)]
        self.board[3][3] = self.board[4][4] = 2  # White
        self.board[3][4] = self.board[4][3] = 1  # Black
        self.current_player = 1  # Black (Player) starts
        self.game_over = False
        self.pass_count = 0
        self.computer_player = 2  # Computer plays as White
        pyxel.run(self.update, self.draw)

    def is_valid_move(self, x, y, player):
        if self.board[x][y] != 0:
            return False
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        opponent = 3 - player
        flips = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            temp_flips = []
            while 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == opponent:
                temp_flips.append((nx, ny))
                nx += dx
                ny += dy
                if 0 <= nx < 8 and 0 <= ny < 8 and self.board[nx][ny] == player:
                    flips.extend(temp_flips)
                    break
        return flips

    def get_valid_moves(self, player):
        valid_moves = []
        for x in range(8):
            for y in range(8):
                if self.is_valid_move(x, y, player):
                    valid_moves.append((x, y))
        return valid_moves

    def has_valid_moves(self, player):
        return len(self.get_valid_moves(player)) > 0

    def count_discs(self):
        black = sum(row.count(1) for row in self.board)
        white = sum(row.count(2) for row in self.board)
        return black, white

    def computer_move(self):
        valid_moves = self.get_valid_moves(self.current_player)
        if valid_moves:
            x, y = random.choice(valid_moves)
            flips = self.is_valid_move(x, y, self.current_player)
            self.board[x][y] = self.current_player
            for fx, fy in flips:
                self.board[fx][fy] = self.current_player
            self.current_player = 3 - self.current_player
            self.pass_count = 0

    def update(self):
        if self.game_over:
            return

        # Check for pass
        if not self.has_valid_moves(self.current_player):
            self.pass_count += 1
            self.current_player = 3 - self.current_player
            if self.pass_count >= 2:
                self.game_over = True
            return
        self.pass_count = 0

        # Player's turn (Black)
        if self.current_player == 1:
            if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
                mx, my = pyxel.mouse_x, pyxel.mouse_y
                x, y = my // 20, mx // 20
                if 0 <= x < 8 and 0 <= y < 8:
                    flips = self.is_valid_move(x, y, self.current_player)
                    if flips:
                        self.board[x][y] = self.current_player
                        for fx, fy in flips:
                            self.board[fx][fy] = self.current_player
                        self.current_player = 3 - self.current_player
        # Computer's turn (White)
        elif self.current_player == self.computer_player:
            self.computer_move()

    def draw(self):
        pyxel.cls(0)
        # Draw board
        for x in range(8):
            for y in range(8):
                pyxel.rect(y * 20, x * 20, 20, 20, 3)  # Green squares
                if self.board[x][y] == 1:
                    pyxel.circ(y * 20 + 10, x * 20 + 10, 8, 0)  # Black disc
                elif self.board[x][y] == 2:
                    pyxel.circ(y * 20 + 10, x * 20 + 10, 8, 7)  # White disc
        # Draw grid lines
        for i in range(9):
            pyxel.line(i * 20, 0, i * 20, 160, 0)
            pyxel.line(0, i * 20, 160, i * 20, 0)
        # Draw status
        black, white = self.count_discs()
        pyxel.text(10, 130, f"Black (Player): {black}  White (CPU): {white}", 7)
        player_str = "Player (Black)" if self.current_player == 1 else "CPU (White)"
        pyxel.text(10, 140, f"Turn: {player_str}", 7)
        if self.game_over:
            winner = "Player (Black)" if black > white else "CPU (White)" if white > black else "Draw"
            pyxel.text(10, 150, f"Game Over! Winner: {winner}", 8)

if __name__ == "__main__":
    Othello()
