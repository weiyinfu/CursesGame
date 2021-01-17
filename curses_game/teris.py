"""
俄罗斯方块
"""
import curses
from typing import List, Tuple

from curses_game.framework import CursesGame, Game, log
import numpy as np

"""
俄罗斯方块一共有七种小块
I、J、L、O、S、T、Z
"""
blocks = """
* 
*
*
*

*
***

  *
***

**
**

 **
**

 *
***

**
 **
""".splitlines()
directions = ((0, 1), (0, -1), (-1, 0), (1, 0))


def legal(x, y, map):
    return len(map) > x >= 0 and len(map[x]) > y >= 0


def get_object(x, y, map):
    # 在一个二维结构中找到一个块
    q = [(x, y)]
    ch = map[x][y]
    vis = set()
    vis.add((x, y))
    while q:
        x, y = q.pop()
        for dx, dy in directions:
            xx, yy = x + dx, y + dy
            if not legal(xx, yy, map) or (xx, yy) in vis:
                continue
            if map[xx][yy] != ch:
                continue
            vis.add((xx, yy))
            q.append((xx, yy))
    return list(vis)


def regularize(obj: List[Tuple[int, int]]):
    x, y = min(obj)
    return [(i - x, j - y) for i, j in obj]


def parse_blocks():
    ans = []
    vis = set()
    for i in range(len(blocks)):
        for j in range(len(blocks[i])):
            if blocks[i][j] == '*' and (i, j) not in vis:
                obj = list(get_object(i, j, blocks))
                for pos in obj:
                    vis.add(pos)
                ans.append(regularize(obj))
    return ans


block_list = parse_blocks()


def find_object(map: np.ndarray):
    # 在map中寻找物体
    return list(np.argwhere(map == 2))


def rotate(obj, map):
    # 首先计算出obj的中心，这个函数是一个尽力而为服务，返回是否旋转成功
    a = np.array(obj)
    x, y = np.mean(a, axis=0)
    x, y = int(x), int(y)
    b = []
    for i, j in obj:
        ii, jj = i - x, j - y
        xx, yy = x + jj, y - ii
        b.append((xx, yy))
    v = map[obj[0][0]][obj[0][1]]

    def roback():
        for x, y in obj:
            map[x][y] = v

    for i, j in obj:
        map[i][j] = 0
    for i, j in b:
        if not legal(i, j, map) or map[i][j]:
            roback()
            return False
    for i, j in b:
        map[i][j] = v
    return True


def generate(map):
    # 在map中生成一个物体，如果生成成功，则
    ind = np.random.randint(0, len(block_list))
    obj = block_list[ind]
    cx = 0
    cy = len(map[0]) // 2
    for x, y in obj:
        if map[x + cx][y + cy]:
            return False
    for x, y in obj:
        map[x + cx][y + cy] = 2  # 2表示当前的活跃object
    return True


def move(obj, dx, dy, map: np.ndarray):
    v = map[obj[0][0]][obj[0][1]]
    for x, y in obj:
        map[x][y] = 0

    def roback():
        for x, y in obj:
            map[x][y] = v

    for x, y in obj:
        xx, yy = x + dx, y + dy
        if not legal(xx, yy, map) or map[xx][yy]:
            roback()
            return False
    for x, y in obj:
        xx, yy = x + dx, y + dy
        map[xx][yy] = v
    return True


def disappear(a: np.ndarray):
    # 把一整行消除掉
    line = []
    for i in range(len(a)):
        if not np.all(a[i] == 1) and np.any(a[i] == 1):
            line.append(i)
    b = np.zeros_like(a)
    for ind, i in enumerate(line):
        j = len(line) - ind
        b[-j] = a[i]
    return b


class Teris(Game):
    def is_over(self) -> bool:
        return self.over

    def update(self):
        obj = find_object(self.map)  # list[pos]
        if not obj:  # 产生一个新的物体
            res = generate(self.map)
            if not res:
                self.over = True
        else:
            self.tick += 1
            if self.tick % 4 != 0:
                return
            if not move(obj, 1, 0, self.map):
                # 如果没能移动成功，小块由活跃转向不活跃
                self.after_down()

    def after_down(self):
        obj = find_object(self.map)
        for x, y in obj:
            self.map[x][y] = 1
        self.map = disappear(self.map)

    def on_cmd(self, cmd: int):
        if cmd == -1:
            return
        obj = find_object(self.map)
        log.info(f"got command {cmd}")
        if not obj:
            log.info(f" no object can be found")
            return
        if cmd == curses.KEY_RIGHT:
            if not move(obj, 0, 1, self.map):
                curses.beep()
        elif cmd == curses.KEY_LEFT:
            if not move(obj, 0, -1, self.map):
                curses.beep()
        elif cmd == curses.KEY_UP:
            if not rotate(obj, self.map):
                curses.beep()
        elif cmd == curses.KEY_DOWN:
            while move(obj, 1, 0, self.map):
                obj = find_object(self.map)
            self.after_down()

    def tos(self) -> List[List[str]]:
        a = [['' for x in range(self.cols)] for y in range(self.rows)]
        for i in range(self.rows):
            a[i][0] = a[i][-1] = '@'
        for i in range(self.rows):
            for j in range(len(self.map[i])):
                a[i][j + 1] = 'H' if self.map[i][j] else '.'
        return a

    def init(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.over = False
        self.tick = 1  # 始终tick，每隔多少个时钟走一格
        self.map = np.zeros((self.rows, self.cols - 2), dtype=np.int)


def test_disappear():
    a = np.random.randint(0, 2, (7, 4))
    a[-1] = 1
    a[-3] = 1
    print(a)
    print('===')
    print(disappear(a))


CursesGame(Teris(), refresh_second=0.05, rows_cols=(20, 13)).main()
