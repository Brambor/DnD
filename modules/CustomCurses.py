import curses
from curses import textpad

from time import sleep

from modules.DnDException import DnDException, DnDExit
from modules.Misc import calculate
from modules.SettingsLoader import settings


class CustomCurses():
	def __init__(self, Connector):
		self.C = Connector
		self.resize_error_triggered = False
		self.curses = curses
		self.fight_history = []
		self.cmd_history = []
		self.cmd_history_pointer = 0
		self.cmd_history_pointer_at_end = True
		self.keys = {
			10: 7,  # regular enter -> enter
			459: 7,  # enter on notepad -> enter
			127: 8,  # backspace on android & wireless keyboard -> backspace
			#NumePad / * - +
			458: "/",
			463: "*",
			464: "-",
			465: "+",
		}

		self.width = 0
		stdscr = curses.initscr()  # Crashes when console's height = 1 :(
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
		self.window_newline_buffer = {}

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
			settings.COLOR_USAGE.update(settings.COLOR_USAGE_BASIC)
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

	def init_windows(self, do_not_resize=False):
		stdscr = self.stdscr

		if self.windows == {}:
			add_history = False
			do_not_resize = False
		else:
			add_history = True
			# check whether we have to resize in spite of do_not_resize
			if do_not_resize:
				stdscr.timeout(0)
				stack = []
				# for some reason chars are only read
				# up to & including KEY_RESIZE
				# => getch stops after KEY_RESIZE
				while ((ch := stdscr.getch()) != -1 ):
					if ch == curses.KEY_RESIZE:
						do_not_resize = False
						break
					stack.append(ch)
				for ch in stack[::-1]:
					curses.ungetch(ch)
				stdscr.timeout(-1)

			self.clear_terminal()
			stdscr.clear()
			stdscr.refresh()
			starty, startx = stdscr.getmaxyx()
			self.width = startx - 1
			self.height = starty - 1
			old_window_dimensions = {w:(*self.windows[w].getmaxyx(), *self.windows[w].getbegyx()) for w in self.windows}
			self.windows.clear()

		for w in settings.WINDOWS:
			if do_not_resize:
				self.windows[w] = curses.newwin(*old_window_dimensions[w])
			else:
				self.windows[w] = curses.newwin(*self.calculate_window_size(w))

			if settings.WINDOWS[w].get("scrollok", True):
				self.windows[w].scrollok( True )  # on False it crashes
				self.windows[w].addstr("\n"*self.height)
			if w != "console_input":
				self.addstr(w, f"<<{w}>>\n")
			self.windows[w].refresh()  # shouldn't this refresh it after resize?

		if add_history:
			self.windows["fight"].addstr("".join(
				self.fight_history[-self.windows["fight"].getmaxyx()[0]:]
			))

			for w in self.windows:
				self.windows[w].refresh()

		self.init_command_textbox()

		# TODO: check if we have "console_input" window and "fight" window

	def init_colors(self):
		# Color pairs
		self.color_usage = {}
		for i, key in enumerate(settings.COLOR_USAGE):
			foreground, background = settings.COLOR_USAGE[key]
			foreground, background = self.color_palette[foreground], self.color_palette[background]
			curses.init_pair(i+1, foreground, background)
			self.color_usage[key] = i+1

	def init_command_textbox(self):
		self.command_textbox = textpad.Textbox(self.windows["console_input"], insert_mode=True)

	def addstr(self, window_str, string, *args, restart=False, only_print_if_possible=False, **kwargs):
		try:
			if restart or (window_str not in self.window_newline_buffer):
				self.window_newline_buffer[window_str] = (False, None, None)

			should_print, saved_args, saved_kwargs = self.window_newline_buffer[window_str]
			if should_print:
				self.windows[window_str].addstr("\n", *saved_args, **saved_kwargs)
				self.window_newline_buffer[window_str] = (False, None, None)

			if string.endswith("\n"):
				string = string[:-1]
				self.window_newline_buffer[window_str] = (True, args, kwargs)
			self.windows[window_str].addstr(string, *args, **kwargs)
		except curses.error:
			if not only_print_if_possible:
				self.indicate_overflow(window_str)

	def calculate_window_size(self, w):
		"expresion is a string that can contain 'x' or 'y' and other mathematical symbols."
		max_y, max_x = self.stdscr.getmaxyx()
		ncols, nlines, begin_x, begin_y = (calculate(
			settings.WINDOWS[w][s][i].replace("x", str(self.width+1)).replace("y", str(self.height+1))
		) for s in ("width_height", "left_top") for i in (0, 1))
		return (max(1, min(nlines, max_y)), max(1, min(ncols, max_x)), max(0, begin_y), max(0, begin_x))

	def clear_terminal(self):
		i = 0
		while True:
			try:
				curses.resize_term(0, 0)
				return
			except:
				if not self.resize_error_triggered:
					print("RESIZE ERROR n.0", end="")
				print(f" {i}", end="")
				self.resize_error_triggered = True
				sleep(0.01)
				i += 1
				if i == 100:
					return

	def get_color_pair(self, pair_human):
		return curses.color_pair(self.color_usage[pair_human])

	def get_window(self, window_name):
		if window_name in self.windows:
			return self.windows[window_name]
		else:
			raise DnDException(f"Window '{window_name}' doesn't exist. These do: {', '.join(self.windows)}.")

	def enter_is_terminate(self, message_len):
		def terminate(x):
			if x == curses.KEY_RESIZE:
				self.resized_terminal()
				self.msg_interrupted = True
				return 7
			if x in self.keys:
				x = self.keys[x]
			if x == 8:  # backspace
				w = self.windows['console_input']
				_, max_x = w.getmaxyx()
				c_y, c_x = w.getyx()
				if (c_y * max_x + c_x <= message_len + 1):  # backspace at begining
					return None
			#up right down left: 259 261 258 260
			if x in {260, 261}:
				w = self.windows['console_input']
				max_y, max_x = w.getmaxyx()
				c_y, c_x = w.getyx()
				if (x == 260 and c_y * max_x + c_x <= message_len + 1  # press left at begining
					or x == 261 and c_y == max_y-1 and c_x == max_x-1  # press right at end
				):
					return None
				c_x += (1 if x == 261 else -1)
				c_y = max(0, min(max_y-1, c_y + c_x // max_x))
				c_x = c_x % max_x
				w.move(c_y, c_x)
				return None
			if x == 259:
				self.move_in_history = -1
				return 7
			if x == 258:
				self.move_in_history = +1
				return 7
			if x == 304:  # alt + f4
				raise DnDExit("alt + f4")
			if x == 7:
				self.cmd_history_pointer = len(self.cmd_history) - 1
				self.cmd_history_pointer_at_end = True
			if x == 26:  # ctrl+z -> move back in history
				self.press_ctrl("z", add_to_log=True)
			if x == 25:  # ctrl+y
				self.press_ctrl("y", add_to_log=True)
			if x == 20:  # ctrl+t
				self.press_ctrl("t", add_to_log=True)
			return x
		return terminate

	def press_ctrl(self, X, add_to_log=False):
		if X == "z":
			self.C.Game.history_move(-1)
		elif X == "y":
			self.C.Game.history_move(+1)
		elif X == "t":
			self.C.Game.toggle_manual_dice()
		else:
			raise NameError(f"'ctrl+{X}' is not defined.")
		if add_to_log:
			self.C.Input.write_to_log(">>>", f"ctrl {X}")			

	def indicate_overflow(self, window):
		self.addstr(window, settings.OVERFLOW_INDICATOR, self.get_color_pair("error"), restart=True, only_print_if_possible=True)

	def send(self, message):
		self.msg_interrupted = False
		self.move_in_history = 0
		while True:
			if self.msg_interrupted:
				input_command = input_command.strip()
			else:
				input_command = message

			if input_command.endswith(">>>"):
				input_command += " "

			self.windows["console_input"].addstr(0, 0, input_command)
			input_command_s = input_command.split("\n")
	#		windows["console_input"].leaveok(False)

			# INPUT
			curses.curs_set(2)
			self.msg_interrupted = False
			input_command = self.command_textbox.edit(self.enter_is_terminate(len(message)))
			if self.msg_interrupted:
				continue
			if self.move_in_history:
				if self.cmd_history:
					self.cmd_history_pointer_at_end, self.cmd_history_pointer = (
						self.cmd_history_pointer + self.move_in_history == len(self.cmd_history),
						min(
							max(0, self.cmd_history_pointer + self.move_in_history + self.cmd_history_pointer_at_end),
							len(self.cmd_history) - 1
						)
					)
					if self.cmd_history_pointer_at_end:
						input_command = f"{message} "
					else:
						input_command = f"{message} {self.cmd_history[self.cmd_history_pointer]}"
				self.windows["console_input"].clear()
				self.C.Print.refresh_history_window()
				self.move_in_history = 0
				self.msg_interrupted = True
				continue
			break

		curses.curs_set(False)  # so that it doesn't blink in top left corner. >>> ocasionally blinks thought...
		return self.serialization(input_command, message)

	def send_test(self, message):
		return self.serialization(f"{message} {input()}\n", message)

	def serialization(self, input_command, message):
		"common parts of self.send and self.send_test"
		# fixing multiline inputs
		input_command = input_command.replace("\n", "") + "\n"
		# removing >>>
		input_command_stripped = input_command[len(message):].strip()
		# if only >>>, then print only \n
		if input_command.strip() == ">>>":
			input_command = "\n"

		self.windows["console_input"].clear()
		self.addstr("fight", input_command)
		self.fight_history.append(input_command)
		self.add_to_history_commands(input_command_stripped)

		self.C.Print.refresh_history_window()
		for w in self.windows:
			self.windows[w].refresh()
		return input_command_stripped

	def add_to_history_commands(self, command):
		if not command:
			return
		if self.cmd_history and command == self.cmd_history[-1]:
			return
		if settings.HISTORY_IGNORE_NUMBERS and command.isdigit():
			return

		self.cmd_history_pointer += (self.cmd_history_pointer == len(self.cmd_history) - 1)
		self.cmd_history.append(command)

	def endCurses(self):
		curses.nocbreak()
		curses.echo()
		curses.endwin()

	def resized_terminal(self, do_not_resize=False):
		self.init_windows(do_not_resize)
		self.C.Print.refresh_windows()

	def window_get_size(self, window_name):
		h, w = self.get_window(window_name).getmaxyx()
		self.C.Print(f"{window_name} is (height, width): {h}, {w}\n")

	def window_get_top_left(self, window_name):
		y, x = self.get_window(window_name).getbegyx()
		self.C.Print(f"{window_name} is at (y, x): {y}, {x}\n")

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
		for i, w in enumerate(self.windows):
			window = self.windows[w]

			# fill windows up, destroying their content
			CP = curses.color_pair(i+1)  # +1 to skip "basic" colour
			window.bkgdset(str(i), CP)
			window.clear()
			he, wi = window.getmaxyx()
			self.addstr(w, f"<<{w}>>", CP, restart=True)
			window.refresh()
		sleep(sleep_for)

		self.resized_terminal(do_not_resize=True)  # make new windows
