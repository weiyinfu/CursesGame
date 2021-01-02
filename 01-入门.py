import curses

stdscr = curses.initscr()
stdscr.addstr(1, 1, '天下大势为我所控')
stdscr.border('L', 'R', 'T', 'B', 'A', 'B', 'C', 'D')
stdscr.addstr(10, 10, "Good")
stdscr.getch()