import curses
from curses import textpad

from time import sleep
from tempfile import TemporaryFile

from modules.DnDException import DnDException, DnDExit


class CustomCurses():
	def __init__(self, settings):
		"Needs self.cPrint from outside. Both way dependency."
		# got self.cPrint = cPrint from outside
		self.curses = curses
		self.COLOR_USAGE = settings.COLOR_USAGE
		self.WINDOWS = settings.WINDOWS
		self.history = []
		self.history_commands = []
		self.history_pointer = 0
		self.history_pointer_at_end = True
		self.keys = {
			10: 7,  # regular enter -> enter
			459: 7,  # enter on notepad -> enter
			127: 263,  # backspace on android & wireless keyboard -> backspace
			#NumePad / * - +
			458: "/",
			463: "*",
			464: "-",
			465: "+",
		}

		self.width = 0
		stdscr = curses.initscr()
		self.COLOR = curses.can_change_color()
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
		if self.COLOR:
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
			# TODO instead write WARNING when not self.COLOR
			for key in settings.COLOR_PALETTE:
				le = len(self.color_palette)
				curses.init_color(le, *settings.COLOR_PALETTE[key])
				self.color_palette[key] = le
		else:
			self.COLOR_USAGE.update(settings.COLOR_USAGE_BASIC)
			self.color_palette = {
				"black": 0,
				"blue": 4,
				"green": 2,
				"cyan": 6,
				"red": 1,
				"magenta": 5,
				"yellow": 3,
				"white": 7,
			}

		self.init_colors()

	def init_windows(self):
		stdscr = self.stdscr

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

		for w in self.WINDOWS:
			self.windows[w] = curses.newwin(
				self.calculate(self.WINDOWS[w]["width_height"][1]),
				self.calculate(self.WINDOWS[w]["width_height"][0]),
				self.calculate(self.WINDOWS[w]["left_top"][1]),
				self.calculate(self.WINDOWS[w]["left_top"][0]),
			)

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
			self.cPrint.refresh_history_window()

		self.init_command_textbox()

		# TODO: check if we have "console_input" window and "fight" window

	def init_colors(self):
		# Color pairs
		self.color_usage = {}
		for i, key in enumerate(self.COLOR_USAGE):
			foreground, background = self.COLOR_USAGE[key]
			foreground, background = self.color_palette[foreground], self.color_palette[background]
			curses.init_pair(i+1, foreground, background)
			self.color_usage[key] = i+1

	def init_command_textbox(self):
		self.command_textbox = textpad.Textbox(self.windows["console_input"], insert_mode=True)

	def calculate(self, expresion):
		"expresion is a string that can contain 'x' or 'y' and other mathematical "
		return eval( expresion.replace("x", str(self.width+1)).replace("y", str(self.height+1)) )

	def get_color_pair(self, pair_human):
		return curses.color_pair(self.color_usage[pair_human])

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
		if x in self.keys:
			x = self.keys[x]
		#up right down left: 259 261 258 260
		if x == 259:
			self.move_in_history = -1
			return 7
		if x == 258:
			self.move_in_history = +1
			return 7
		if x == 304:  # alt + f4
			raise DnDExit("alt + f4")
		if x == 7:
			self.history_pointer = len(self.history_commands) - 1
			self.history_pointer_at_end = True
		return x

	def send(self, message):
		self.msg_interrupted = False
		self.move_in_history = 0
		while True:
			if self.msg_interrupted:
				input_command = input_command.strip()
				if input_command.endswith(">>>"):
					input_command += " "
				offset = 0
			else:
				input_command = message
				offset = 1

			self.windows["console_input"].addstr(0, 0, input_command)
			input_command_s = input_command.split("\n")
			self.windows["console_input"].move(len(input_command_s)-1, len(input_command_s[-1])+offset)  # TODO: crashes when len(message_s) > 3 or 4
	#		windows["console_input"].leaveok(False)

			# INPUT
			curses.curs_set(2)
			self.msg_interrupted = False
			input_command = self.command_textbox.edit(self.enter_is_terminate)
			if self.msg_interrupted:
				continue
			if self.move_in_history:
				if self.history_commands:
					self.history_pointer_at_end, self.history_pointer = (
						self.history_pointer + self.move_in_history == len(self.history_commands),
						min(
							max(0, self.history_pointer + self.move_in_history + self.history_pointer_at_end),
							len(self.history_commands) - 1
						)
					)
					if self.history_pointer_at_end:
						input_command = f"{message} "
					else:
						input_command = f"{message} {self.history_commands[self.history_pointer]}"
				self.windows["console_input"].clear()
				self.cPrint.refresh_history_window()
				self.move_in_history = 0
				self.msg_interrupted = True
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
		self.windows["fight"].addstr(input_command)  # fight, but s
		self.history.append(input_command)
		self.add_to_history_commands(input_command_stripped)

		self.cPrint.refresh_history_window()
		for w in self.windows:
			self.windows[w].refresh()
		return input_command_stripped[:-1]  # removing ending \n

	def add_to_history_commands(self, command):
		if command in ("",):
			return
		if self.history_commands and command == self.history_commands[-1]:
			return

		if self.history_pointer == len(self.history_commands) - 1:
			self.history_pointer += 1
		self.history_commands.append(command)

	def endCurses(self):
		curses.nocbreak()
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
		tmpfiles = []
		for i, w in enumerate(self.windows):
			# save windows
			window = self.windows[w]
			tmpfile = TemporaryFile()
			window.putwin(tmpfile)
			tmpfiles.append(tmpfile)

			# fill windows up, destroying their content
			CP = curses.color_pair(i+1)  # +1 to skip "basic" colour
			window.bkgdset(str(i), CP)
			window.clear()
			window.addstr(f"<<{w}>>", CP)
			window.refresh()
		sleep(sleep_for)

		for w, tmpfile in zip(self.windows, tmpfiles):
			# restore windows
			tmpfile.seek(0)
			self.windows[w] = curses.getwin(tmpfile)
			self.windows[w].refresh()
		self.init_command_textbox()
