import curses
from curses import textpad

class CustomCurses():
	def __init__(self):
		input("Make this window however big and press ENTER.")
		stdscr = curses.initscr()
		curses.start_color()

		curses.noecho()  # doesn't print pressed keys
		#curses.echo()
		#curses.cbreak()  # doesn't wait for Enter to be pressed
		
		#unnecesary since it is handled around every input
		curses.curs_set(2)  # cursor is: [0/False] doesn't show blinking cursor; [1] underslash; [2] block
		stdscr.keypad(True)  # getting special keys such as curses.KEY_LEFT
		#stdscr.nodelay(1)  # get_wch doesn't wait for char, returns -1 instead

		width = curses.COLS - 1
		height = curses.LINES - 1

		#win = curses.newwin(height, width//3, begin_y, begin_x)
		windows = []
		self.windows = windows

		#left
		windows.append(curses.newwin(height-3, width//3, 0, 0))
		#middle
		windows.append(curses.newwin(height-3, width//3, 0, width//3))
		#right
		windows.append(curses.newwin(height-3, width//3, 0, 2*(width//3)))
		#input
		windows.append(curses.newwin(3, width, height-2, 0))
		self.command_textbox = textpad.Textbox(windows[3])

		for w, t in zip(windows, ("<<left>>\n", "<<middle>>\n", "<<right>>\n")):
			w.scrollok(True)
			for i in range(height):
				w.addstr("\n")
			w.addstr(t)
			w.refresh()

	def send(self, message):
		input_command = ""
		windows = self.windows

		print("message yielded (send) %s" % message)
		windows[3].addstr(0, 0, message)
		message_s = message.split()
		windows[3].move(len(message_s)-1, len(message_s[-1])+1)
#		windows[3].leaveok(False)

		# INPUT
		curses.curs_set(2)
		input_command = self.command_textbox.edit(enter_is_terminate)
		curses.curs_set(False)  # so that it doesn't blink in top left corner. >>> ocasionally blinks thought...

		# removing >>>
		input_command = input_command[len(message)+1 + message.count("\n"):]

		windows[3].clear()

		windows[0].addstr(input_command)  # fight, but s

		print("in generator: %s" % input_command)
		#  yield input_command[:-2]  # removing ending \n
		print("after yield")

		for w in windows:
			w.refresh()
		return input_command[:-2]  # removing ending \n

	def endCurses(self):
		curses.nocbreak()
		# stdscr.keypad(False)
		curses.echo()

		curses.endwin()


def enter_is_terminate(x):
	if x in (10, 459):  # regular enter, enter on notepad
		x = 7
	return x

#curses.wrapper(input_curses)

#input()