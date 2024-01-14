import pyxel as px
import json

MIN_LENGTH = 2
MAX_LENGTH = 16
FIRST_HEIGHT = 160
SPEED = 2
DIFFICULTY = 0.05
TOTAL_LENGTH = int(FIRST_HEIGHT / DIFFICULTY + 160)


def calculate_vertical_coordinates():
    binary_array = [0]
    vertical_coordinates = [0]
    velocity = 0

    while len(binary_array) < TOTAL_LENGTH:
        next_element = 0 if binary_array[-1] == 1 else 1
        length = px.rndi(MIN_LENGTH, MAX_LENGTH)
        length = min(length, TOTAL_LENGTH - len(binary_array))
        binary_array.extend([next_element] * length)
        for _ in range(length):
            velocity = (
                min(velocity + 1, 16) if next_element == 1 else max(velocity - 1, -16)
            )
            vertical_coordinates.append(vertical_coordinates[-1] + velocity)
    return vertical_coordinates[:-1]


def text(x, y, s, c):
    for i in range(4):
        (dx, dy) = [(0, -1), (1, 0), (0, 1), (-1, 0)][i]
        px.text(x + dx, y + dy, s, 0)
    px.text(x, y, s, c)


class App:
    def __init__(self):
        px.init(160, 256, title="Pyxel Caver")
        px.load("platformer.pyxres")
        with open(f"./music.json", "rt") as fin:
            self.music = json.loads(fin.read())
        px.sounds[4].set("a3a2c2c2", "n", "7742", "s", 10)
        self.is_first = True
        self.start()
        px.run(self.update, self.draw)

    def start(self):
        self.x = 0
        self.y = 0
        self.g = 0
        self.walls = calculate_vertical_coordinates()
        self.h = 160.0
        self.start_timer = 0
        self.end_timer = 0

    def update(self):
        pressed = px.btn(px.KEY_SPACE) or px.btn(px.MOUSE_BUTTON_LEFT)
        if self.is_first:
            if not pressed:
                return
            self.is_first = False
            for ch, sound in enumerate(self.music):
                px.sounds[ch].set(*sound)
                px.play(ch, ch, loop=True)
        if self.end_timer:
            if self.end_timer >= 20 and pressed:
                self.start()
            else:
                self.end_timer = min(self.end_timer + 1, 20)
            return
        self.start_timer = min(self.start_timer + 1, 60)
        if self.start_timer < 30:
            return
        self.x += SPEED
        self.h -= DIFFICULTY * SPEED
        self.g += (-1 if pressed else 1) * SPEED
        self.y += self.g
        dist = abs(self.walls[self.x + 12] - self.y) // 8
        if dist >= self.h // 2:
            px.play(3, 4)
            self.end_timer = 1

    def draw(self):
        bc = 4 if self.end_timer % 2 else 0
        sx = self.x % 8
        sy = (self.y // 8) % 8
        for x in range(21):
            for y in range(32):
                px.blt(x * 8 - sx, y * 8 - sy, 0, 0, 40, 8, 8)
        px.rect(0, 248, 256, 8, 0)
        for x in range(160):
            wall_center = (self.walls[self.x + x] - self.y) // 8 + 124
            wall_ceil = min(wall_center - self.h // 2, 247)
            wall_floor = max(wall_center + self.h // 2, 0)
            px.line(x, wall_ceil + 1, x, wall_floor - 1, bc)
        if not self.end_timer:
            u = (px.frame_count // 3) % 3
            px.blt(8, 120, 0, u * 8, 16, 8, 8, 2)
        text(120, 250, f"SCORE:{self.x}", 7)
        if self.is_first:
            text(58, 108, "Pyxel Caver", 7)
            text(30, 124, "Press Space or tap screen", 13)
            text(40, 132, "[ON] up / [OFF] down", 13)
        elif self.end_timer:
            text(54, 116, "- GAME OVER -", 8)
            if self.end_timer >= 20:
                text(48, 124, "Press to restart", 7)
        elif self.start_timer < 30:
            text(62, 120, "- READY -", 7)
        elif self.start_timer < 60:
            text(74, 120, "GO!", 7)


App()
