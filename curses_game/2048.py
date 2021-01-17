"""
基于curses的2048小游戏
"""
import curses
from typing import List

import numpy as np

from curses_game.framework import Game, CursesGame


def down(a: np.ndarray):
    for y in range(4):
        ans = []
        merged = False
        for x in range(3, -1, -1):
            if a[x][y]:
                if ans and ans[-1] == a[x][y] and not merged:
                    merged = True
                    ans[-1] *= 2
                else:
                    ans.append(a[x][y])
        while len(ans) < 4:
            ans.append(0)
        a[:, y] = ans[::-1]


def rotate(a: np.ndarray):
    b = np.empty_like(a)
    for i in range(4):
        for j in range(4):
            b[i][j] = a[j][3 - i]
    return b


def generate(a: np.ndarray):
    # 随机产生一个元素
    b = a.reshape(-1)
    ind = np.argwhere(b == 0).reshape(-1)
    b[ind[np.random.randint(0, len(ind))]] = 2


def rotate_many(a: np.ndarray, times: int):
    for i in range(times):
        a = rotate(a)
    return a


def no_same(a):
    for i in range(4):
        for j in range(4):
            if i + 1 < 4 and a[i][j] == a[i + 1][j]:
                return False
            if j + 1 < 4 and a[i][j] == a[i][j + 1]:
                return False
    return True


class Game2048(Game):
    def is_over(self) -> bool:
        return np.count_nonzero(self.a == 0) == 0 and no_same(self.a)

    def update(self):
        pass

    def on_cmd(self, cmd: int):
        ops = [curses.KEY_UP, curses.KEY_RIGHT, curses.KEY_DOWN, curses.KEY_LEFT]
        if cmd not in ops:
            return
        ind = ops.index(cmd)
        times = (2 - ind + 4) % 4
        b = rotate_many(self.a, (4 - times) % 4)
        down(b)
        self.a = rotate_many(b, times)
        if np.count_nonzero(self.a == 0):
            generate(self.a)

    def tos(self) -> List[List[str]]:
        b = self.a.reshape(-1)
        sz = max(len(str(i)) for i in b)
        sz += 1
        assert self.cols > sz * 4
        ans = [[' ' for y in range(self.cols)] for x in range(self.rows)]

        def write(x, y, s):
            for i in range(len(s)):
                ans[x][y + i] = s[i]

        for i in range(len(self.a)):
            for j in range(len(self.a[i])):
                write(i, j * sz, str(self.a[i][j]))
        return ans

    def init(self, rows: int, cols: int):
        self.a = np.zeros((4, 4), dtype=np.int32)
        self.rows = rows
        self.cols = cols
        generate(self.a)


CursesGame(Game2048()).main()
