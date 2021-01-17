"""
基于curses的游戏框架
"""
import curses
import logging
import signal
import time
from abc import ABCMeta, abstractmethod
from typing import List

good_format = logging.Formatter(
    '%(asctime)s pid=%(process)d %(filename)s:%(lineno)s %(funcName)s [%(name)s]-%(levelname)s: %(message)s')

log = logging.getLogger("framework")
log.setLevel(logging.INFO)
filehandler = logging.FileHandler("frame.log", mode='w')
filehandler.setFormatter(good_format)
log.addHandler(filehandler)


def dif(old, now):
    assert len(old) == len(now) and len(now[0]) == len(old[0])
    op = []
    for i in range(len(old)):
        for j in range(len(old[0])):
            if old[i][j] != now[i][j]:
                op.append((i, j, now[i][j]))
    return op


class Game(metaclass=ABCMeta):
    @abstractmethod
    def is_over(self) -> bool:
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def on_cmd(self, cmd: int):
        pass

    @abstractmethod
    def tos(self) -> List[List[str]]:
        pass

    @abstractmethod
    def init(self, rows: int, cols: int):
        pass


class CursesGame:
    def __init__(self, game: Game, refresh_second: float = 0.15, rows_cols=None):
        """
        :param game:
        :param refresh_second:
        如果指明
        """
        scr = curses.initscr()
        curses.noecho()
        curses.curs_set(0)
        if rows_cols is not None:
            rows, cols = rows_cols
            self.scr = curses.newwin(rows, cols)
        else:
            self.scr = scr
        self.scr.keypad(True)
        self.refresh_second = refresh_second  # 多长时间移动一次，单位为秒
        self.rows, self.cols = self.scr.getmaxyx()
        self.last_s = None
        self.game = game

    def get_empty(self):
        return [[' ' for _ in range(self.cols)] for __ in range(self.rows)]

    def draw(self, now):
        if self.last_s is None:
            self.last_s = self.get_empty()
        ops = dif(self.last_s, now)
        self.last_s = now
        for x, y, ch in ops:
            try:
                self.scr.move(x, y)
                self.scr.addstr(ch)
            except Exception as ex:
                # 根据官方文档：尝试在窗口、子窗口或面板的右下角写入将在字符被打印之后导致异常被引发。
                log.info(f"x={x}, y={y}, ch={ch}, rows={self.rows}, cols={self.cols}, {str(ex)}")

    def main(self):
        curses.noecho()
        curses.curs_set(0)

        def rollback():
            curses.curs_set(2)
            curses.endwin()
            curses.beep()

        def on_interupted(signumber, frame):
            rollback()
            exit(0)

        signal.signal(signal.SIGINT, on_interupted)
        try:
            while 1:
                self.scr.erase()
                self.scr.timeout(50)
                self.play_game()
                self.scr.timeout(-1)
                self.scr.getch()
        except Exception as ex:
            log.exception(ex)
            rollback()

    def center_write(self, x, y, s):
        self.scr.move(x, y - len(s) // 2)
        self.scr.addstr(s)

    def game_over(self):
        curses.beep()
        curses.flash()
        self.center_write(self.rows // 2, self.cols // 2, f"GameOver")

    def play_game(self):
        self.last_s = None
        self.game.init(self.rows, self.cols)
        last_move_time = 0
        while 1:
            cmd = self.scr.getch()
            if cmd != -1:
                self.game.on_cmd(cmd)
            now = time.time()
            if now - last_move_time > self.refresh_second:
                last_move_time = now
                self.game.update()
                self.draw(self.game.tos())
                if self.game.is_over():
                    self.game_over()
                    break
