import curses
from curses import textpad

from time import sleep

from modules.DnDException import DnDException, DnDExit


class CustomCurses():
	def __init__(self, settings):
		"Needs self.cPrint from outside. Both way dependency."
		# got self.cPrint = cPrint from outside
		self.curses = curses
		self.COLOR_USAGE = settings.COLOR_USAGE
		self.WINDOWS = settings.WINDOWS
		self.history = []

		self.width = 0
		stdscr = curses.initscr()
		curses.start_color()
		self.stdscr = stdscr

		curses.noecho()  # doesn't print pressed keys
		#curses.echo()
		curses.cbreak()  # doesn't wait for Enter to be pressed
		
		#unnecesary since it is handled around every input
		curses.curs_set(2)  # cursor is: [0/False] doesn't show blinking cursor; [1] underslash; [2] block
		stdscr.keypad(True)  # getting special keys such as curses.KEY_LEFT
		#stdscr.nodelay(1)  # get_wch doesn't wait for char, returns -1 instead

		starty, startx = stdscr.getmaxyx()
		self.width = startx - 1
		self.height = starty - 1
		self.windows = {}

		self.init_windows()

		# Colors
		self.color_palette = {
			"black": 0,
			"blue": 1,
			"green": 2,
			"cyan": 3,
			"red": 4,
			"magenta": 5,
			"yellow": 6,
			"white": 7,
		}
		for i, key in enumerate(settings.COLOR_PALETTE):
			curses.init_color(i+8, *settings.COLOR_PALETTE[key])
			self.color_palette[key] = i+8

		self.init_colors()

		"""
		leaving it there just in case something breaks 
		except Exception as e:
			curses.nocbreak()
			curses.echo()
			curses.endwin()
			print("\n\n")
			traceback.print_exc(file=sys.stdout)
			input("CRASHED, PRESS ENTER")
			raise
		"""

	def init_windows(self):
		stdscr = self.stdscr

		"""
		HISTORY
		# this means that history is session specific
		# last thing in self.history is current command that hasn't been run yet
		self.history = [""]
		self.history_pointer = 0
		self.move_history = 0
		"""
		
		if self.windows == {}:
			add_history = False
		else:
			add_history = True

			curses.resize_term(0, 0)
			stdscr.clear()
			stdscr.refresh()
			starty, startx = stdscr.getmaxyx()
			self.width = startx - 1
			self.height = starty - 1
			self.windows.clear()
		
		#win = curses.newwin(height, width//3, begin_y, begin_x)

		for w in self.WINDOWS:
			wi = self.calculate(self.WINDOWS[w]["width_height"][0])
			he = self.calculate(self.WINDOWS[w]["width_height"][1])
			left_top_wi = self.calculate(self.WINDOWS[w]["left_top"][0])
			left_top_he = self.calculate(self.WINDOWS[w]["left_top"][1])
			self.windows[w] = curses.newwin(he, wi, left_top_he, left_top_wi)

			if self.WINDOWS[w].get("scrollok", True):
				self.windows[w].scrollok( True )  # on False it crashes
				for i in range(self.height):
					self.windows[w].addstr("\n")
			if w != "console_input":
				self.windows[w].addstr("<<%s>>\n" % w)
			self.windows[w].refresh()  # shouldn't this refresh it after resize?

		if add_history:
			for msg in self.history[-self.windows["fight"].getmaxyx()[0]:]:
				self.windows["fight"].addstr(msg)

			for w in self.windows:
				self.windows[w].refresh()
			self.cPrint.refresh_entity_window()
			self.cPrint.refresh_inventory_window()

		self.command_textbox = textpad.Textbox(self.windows["console_input"], insert_mode=True)

		# TODO: check if we have "console_input" window and "fight" window

	def init_colors(self):
		# Color pairs
		self.color_usage = {}
		for i, key in enumerate(self.COLOR_USAGE):
			foreground, background = self.COLOR_USAGE[key]
			foreground, background = self.color_palette[foreground], self.color_palette[background]
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
		if x == curses.KEY_RESIZE:
			self.init_windows()
			self.init_colors()
			self.msg_interrupted = True
			return 7
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
		self.msg_interrupted = False
		while True:
			if self.msg_interrupted:
				input_command = input_command.strip()
				if input_command.endswith(">>>"):
					input_command += " "
				self.windows["console_input"].addstr(0, 0, input_command)
				input_command_s = input_command.split("\n")
				self.windows["console_input"].move(len(input_command_s)-1, len(input_command_s[-1]))
			else:
				self.windows["console_input"].addstr(0, 0, message)

				message_s = message.split("\n")

				self.windows["console_input"].move(len(message_s)-1, len(message_s[-1])+1)  # TODO: crashes when len(message_s) > 3 or 4
	#		windows["console_input"].leaveok(False)

			# INPUT
			curses.curs_set(2)
			self.msg_interrupted = False
			input_command = self.command_textbox.edit(self.enter_is_terminate)
			if self.msg_interrupted:
				continue
			break

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
		"""
		HISTORY
		if self.history_pointer == len(self.history) - 1:
			self.history_pointer += 1
		self.history.append(input_command_stripped)
		"""

		self.windows["fight"].addstr(input_command)  # fight, but s
		self.history.append(input_command)

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


#curses.wrapper(input_curses)

#input()