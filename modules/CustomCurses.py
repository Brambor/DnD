import curses
from curses import textpad

from time import sleep

from modules.DnDException import DnDException, DnDExit


class CustomCurses():
	def __init__(self, COLOR_PALETTE, COLOR_USAGE):
		input("Make this window however big and press ENTER.")
		stdscr = curses.initscr()
		curses.start_color()
		self.curses = curses

		curses.noecho()  # doesn't print pressed keys
		#curses.echo()
		#curses.cbreak()  # doesn't wait for Enter to be pressed
		
		#unnecesary since it is handled around every input
		curses.curs_set(2)  # cursor is: [0/False] doesn't show blinking cursor; [1] underslash; [2] block
		stdscr.keypad(True)  # getting special keys such as curses.KEY_LEFT
		#stdscr.nodelay(1)  # get_wch doesn't wait for char, returns -1 instead

		self.width = curses.COLS - 1
		self.height = curses.LINES - 1

		#win = curses.newwin(height, width//3, begin_y, begin_x)
		self.windows = {}

		for w in WINDOWS:
			wi = self.calculate(WINDOWS[w]["width_height"][0])
			he = self.calculate(WINDOWS[w]["width_height"][1])
			left_top_wi = self.calculate(WINDOWS[w]["left_top"][0])
			left_top_he = self.calculate(WINDOWS[w]["left_top"][1])
			self.windows[w] = curses.newwin(he, wi, left_top_he, left_top_wi)

			if WINDOWS[w].get("scrollok", True):
				self.windows[w].scrollok( True )  # on False it crashes
				for i in range(self.height):
					self.windows[w].addstr("\n")
			if w != "console_input":
				self.windows[w].addstr("<<%s>>\n" % w)
			self.windows[w].refresh()

		self.command_textbox = textpad.Textbox(self.windows["console_input"])

		# TODO: check if we have "console_input" window and "fight" window

		# Colors
		color_palette = {
			"black": 0,
			"blue": 1,
			"green": 2,
			"cyan": 3,
			"red": 4,
			"magenta": 5,
			"yellow": 6,
			"white": 7,
		}
		for i, key in enumerate(COLOR_PALETTE):
			curses.init_color(i+8, *COLOR_PALETTE[key])
			color_palette[key] = i+8

		# Color pairs
		self.color_usage = {}
		for i, key in enumerate(COLOR_USAGE):
			foreground, background = COLOR_USAGE[key]
			foreground, background = color_palette[foreground], color_palette[background]
			curses.init_pair(i+1, foreground, background)
			self.color_usage[key] = i+1

	def calculate(self, expresion):
		"expresion is a string that can contain 'x' or 'y' and other mathematical "
		return eval( expresion.replace("x", str(self.width)).replace("y", str(self.height)) )

	def get_window(self, window_name):
		if window_name in self.windows:
			return self.windows[window_name]
		else:
			raise DnDException("Window '%s' doesn't exist. These do: %s." % (window_name, ", ".join(key for key in self.windows)))

	def enter_is_terminate(self, x):
		#up right down left: 259 261 258 260
		if x in (10, 459):  # regular enter, enter on notepad
			return 7  # enter
		"""
		HISTORY
		if x == 259:
			self.move_history = -1
			return 7
		if x == 258:
			self.move_history = +1
			return 7
		"""
		if x == 304:  # alt + f4
			raise DnDExit("alt + f4")
		return x

	def send(self, message):
		self.windows["console_input"].addstr(0, 0, message)

		message_s = message.split("\n")

		self.windows["console_input"].move(len(message_s)-1, len(message_s[-1])+1)  # TODO: crashes when len(message_s) > 3 or 4
#		windows["console_input"].leaveok(False)

		# INPUT
		curses.curs_set(2)
		input_command = self.command_textbox.edit(self.enter_is_terminate)
		# each line in regular input is " \n" instead of "\n" (for some reason)
		input_command = input_command.replace(" \n", "\n")
		curses.curs_set(False)  # so that it doesn't blink in top left corner. >>> ocasionally blinks thought...
		return self.serialization(input_command, message)

	def send_test(self, message):
		input_command = "%s %s\n" % (message, input())
		input_command = input_command.replace(" \n", "\n")  # for the one special case when input_command == ">>> \n"
		return self.serialization(input_command, message)

	def serialization(self, input_command, message):
		"common parts of self.send and self.send_test"
		# removing >>>
		input_command_stripped = input_command[len(message)+1:]
		# if only >>>, then print only \n
		if input_command == ">>>\n":
			input_command = "\n"

		self.windows["console_input"].clear()

		self.windows["fight"].addstr(input_command)  # fight, but s

		for w in self.windows:
			self.windows[w].refresh()
		return input_command_stripped[:-1]  # removing ending \n

	def endCurses(self):
		curses.nocbreak()
		# stdscr.keypad(False)
		curses.echo()

		curses.endwin()

	def window_get_size(self, window_name):
		window = self.get_window(window_name)
		ret_str = "%s is (height, width): %d, %d\n" % (window_name, *window.getmaxyx())
		self.windows["fight"].addstr(ret_str)
		self.windows["fight"].refresh()

	def window_get_top_left(self, window_name):
		window = self.get_window(window_name)
		ret_str = "%s is at (y, x): %d, %d\n" % (window_name, *window.getbegyx())
		self.windows["fight"].addstr(ret_str)
		self.windows["fight"].refresh()

	def window_set_size(self, window, ncols, nlines):
		"set window size to (ncols, nlines)"
		window = self.get_window(window)

		bgchar = window.getbkgd()
		window.bkgdset(" ")
		window.clear()
		window.refresh()

		window.bkgdset(bgchar)
		window.resize(ncols, nlines)
		window.refresh()

	def window_set_top_left(self, window, y, x):
		"set window top left corner to (y, x)"
		window = self.get_window(window)

		bgchar = window.getbkgd()
		window.bkgdset(" ")
		window.clear()
		window.refresh()

		window.bkgdset(bgchar)
		window.mvwin(y, x)
		window.refresh()

	def window_show(self, sleep_for):
		"displays where are the windows, which are which and their size"
		"TODO clears window. that should not happen"
		for i, w in enumerate(self.windows):
			window = self.windows[w]
			bgchar = window.getbkgd()
			window.bkgdset(str(i))
			window.clear()
			window.addstr("<<%s>>" % w)
			window.refresh()
			window.bkgdset(bgchar)
			window.refresh()
		sleep(sleep_for)
		for w in self.windows:
			self.windows[w].clear()
			self.windows[w].refresh()

WINDOWS = {
	"fight": {
		"left_top": ("0", "0"),
		"width_height": ("2*x//3", "y-2"),
	},
	"entities": {
		"left_top": ("2*x//3", "0"),
		"width_height": ("x//3", "y//2"),
		"scrollok": False,
	},
	"inventory": {
		"left_top": ("2*x//3", "y//2"),
		"width_height": ("x//3", "y//2-1"),
		"scrollok": False,
	},
	"console_input": {
		"left_top": ("0", "y-2"),
		"width_height": ("x", "3"),
	},
}

"""
WINDOWS = { # fight, help, effect ; console_input
	"fight": {
		"left_top": ("0", "0"),
		"width_height": ("x//3", "y-3"),
	},
	"help": {
		"left_top": ("x//3", "0"),
		"width_height": ("x//3", "y-3"),
	},
	"effect": {
		"left_top": ("2*x//3", "0"),
		"width_height": ("x//3", "y-3"),
	},
	"console_input": {
		"left_top": ("0", "y-2"),
		"width_height": ("x", "3"),
	},
}
"""

#curses.wrapper(input_curses)

#input()