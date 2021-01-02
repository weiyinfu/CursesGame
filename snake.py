import curses
import random
import time

logfile = open("haha.log", 'w')
"""
控制台版贪吃蛇
"""


def log(*args, **kwargs):
    logfile.write(str((args, kwargs)))
    logfile.write('\n')


scr = curses.initscr()
curses.noecho()
curses.curs_set(0)
curses.cbreak()
scr.keypad(True)

refresh_second = 0.15  # 多长时间移动一次，单位为秒
rows, cols = scr.getmaxyx()
snake = [(rows // 2, cols // 2)]
food = (0, 0)


def generate_food():
    global food
    while 1:
        food = (random.randint(1, rows - 2), random.randint(1, cols - 2))
        if food not in snake:
            return food


def get_empty():
    return [[' ' for _ in range(cols)] for __ in range(rows)]


class Char:
    wall = '❀'
    snake = '█'
    food = 'F'
    snake_head = 'H'


def tos():
    # 画墙
    a = get_empty()
    for i in range(rows):
        a[i][0] = a[i][-1] = Char.wall
    for i in range(cols):
        a[0][i] = a[-1][i] = Char.wall
    for ind, (x, y) in enumerate(snake):
        a[x][y] = Char.snake_head if ind == 0 else Char.snake
    x, y = food
    a[x][y] = Char.food
    return a


def dif(old, now):
    assert len(old) == len(now) and len(now[0]) == len(old[0])
    op = []
    for i in range(len(old)):
        for j in range(len(old[0])):
            if old[i][j] != now[i][j]:
                op.append((i, j, now[i][j]))
    return op


last_s = None


def draw():
    global last_s
    now = tos()
    if last_s is None:
        last_s = get_empty()
    ops = dif(last_s, now)
    last_s = now
    for x, y, ch in ops:
        try:
            scr.move(x, y)
            scr.addstr(ch)
        except Exception as ex:
            # 根据官方文档：尝试在窗口、子窗口或面板的右下角写入将在字符被打印之后导致异常被引发。
            log(x, y, ch, rows, cols, str(ex))


def legal(x, y):
    # 需要排除墙
    return 1 <= x <= rows - 2 and 1 <= y <= cols - 2


def center_write(x, y, s):
    scr.move(x, y - len(s) // 2)
    scr.addstr(s)


def game_over():
    curses.beep()
    curses.flash()
    center_write(rows // 2, cols // 2, f"GameOver:{len(snake)}")


def move(dx, dy) -> bool:
    # 让蛇移动
    x, y = snake[0]
    x += dx
    y += dy
    if not legal(x, y):
        return False
    if (x, y) in snake:
        # 撞上了自己
        return False
    snake.insert(0, (x, y))
    if (x, y) == food:
        # 吃了一粒食物，直接长身体
        generate_food()
        return True
    snake.pop()
    return True


def play_game():
    global snake, last_s
    last_s = None
    generate_food()
    snake = [(rows // 2, cols // 2)]
    last_move_time = 0
    directions = ((-1, 0), (0, 1), (1, 0), (0, -1))
    direction = 0
    ks = [curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]
    while 1:
        cmd = scr.getch()
        if cmd != -1:
            if cmd in ks:
                direction = ks.index(cmd)
        now = time.time()
        if now - last_move_time > refresh_second:
            last_move_time = now
            dx, dy = directions[direction]
            if not move(dx, dy):
                game_over()
                break
            draw()


def main():
    while 1:
        scr.erase()
        scr.timeout(50)
        play_game()
        scr.timeout(-1)
        scr.getch()


if __name__ == '__main__':
    main()
