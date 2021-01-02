from curses import wrapper
import curses

"""
使用wrapper
"""
def main(stdscr):
    # Clear screen
    stdscr.erase()
    stdscr.clear()

    stdscr.addstr(20, 20, "Current mode: Typing mode",
                  curses.A_REVERSE)
    stdscr.refresh()
    stdscr.getkey()


wrapper(main)
