import curses

x = curses.initscr()
curses.noecho()
while 1:
    b = x.getch()
    x.addstr(str(b))
    x.addstr(str(type(b)))
    x.addstr("haha")