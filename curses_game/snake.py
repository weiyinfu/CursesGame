import random

from curses_game.framework import Game, CursesGame, log
import curses


class Char:
    wall = '❀'
    snake = '#'  # '█'■
    food = 'F'
    snake_head = 'H'


ks = [curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]
directions = ((-1, 0), (0, 1), (1, 0), (0, -1))


class Snake(Game):
    def is_over(self):
        return self.over

    def update(self):
        # 让蛇移动
        x, y = self.snake[0]
        dx, dy = directions[self.direction]
        x += dx
        y += dy
        if not self.legal(x, y):
            self.over = True
            return
        if (x, y) in self.snake:
            # 撞上了自己
            self.over = True
            return
        self.snake.insert(0, (x, y))
        if (x, y) == self.food:
            # 吃了一粒食物，直接长身体
            self.generate_food()
            return
        self.snake.pop()

    def on_cmd(self, cmd: int):
        if cmd == -1:
            return
        if cmd in ks:
            log.info(f"got command {cmd}")
            self.direction = ks.index(cmd)

    def tos(self):
        # 画墙
        a = self.get_empty()
        for i in range(self.rows):
            a[i][0] = a[i][-1] = Char.wall
        for i in range(self.cols):
            a[0][i] = a[-1][i] = Char.wall
        for ind, (x, y) in enumerate(self.snake):
            a[x][y] = Char.snake_head if ind == 0 else Char.snake
        x, y = self.food
        a[x][y] = Char.food
        return a

    def init(self, rows, cols):
        self.snake = [(rows // 2, cols // 2)]
        self.rows = rows
        self.cols = cols
        self.generate_food()
        self.direction = 0
        self.over = False

    def generate_food(self):
        while 1:
            food = (random.randint(1, self.rows - 2), random.randint(1, self.cols - 2))
            if food not in self.snake:
                self.food = food
                return

    def legal(self, x, y):
        # 需要排除墙
        return 1 <= x <= self.rows - 2 and 1 <= y <= self.cols - 2

    def get_empty(self):
        return [[' ' for i in range(self.cols)] for j in range(self.rows)]

    def __init__(self):
        self.snake = [(0, 0)]
        self.rows = 0
        self.cols = 0
        self.food = (0, 0)
        self.direction = 0
        self.over = False


CursesGame(Snake()).main()
