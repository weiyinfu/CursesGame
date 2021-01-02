import curses

x = curses.initscr()
rows, cols = x.getmaxyx()
x.addstr('❀' * (cols // 2))
x.move(1, 0)
x.addstr('●' * (cols // 2))
x.move(2, 0)
x.addstr('█' * (cols // 2))
x.getch()
