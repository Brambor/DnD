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

		self.width = curses.COLS - 1
		self.height = curses.LINES - 1

		#win = curses.newwin(height, width//3, begin_y, begin_x)
		windows = {}
		self.windows = windows

		for w in WINDOWS:
			wi = self.calculate(WINDOWS[w]["width_height"][0])
			he = self.calculate(WINDOWS[w]["width_height"][1])
			left_top_wi = self.calculate(WINDOWS[w]["left_top"][0])
			left_top_he = self.calculate(WINDOWS[w]["left_top"][1])
			self.windows[w] = curses.newwin(he, wi, left_top_he, left_top_wi)

			self.windows[w].scrollok(True)
			for i in range(self.height):
				self.windows[w].addstr("\n")
			if w != "console_input":
				self.windows[w].addstr("<<%s>>\n" % w)
			self.windows[w].refresh()

		self.command_textbox = textpad.Textbox(windows["console_input"])

		# TODO: check if we have "console_input" window and "fight" window

	def calculate(self, expresion):
		"expresion is a string that can contain 'x' or 'y' and other mathematical "
		return eval( expresion.replace("x", str(self.width)).replace("y", str(self.height)) )


	def send(self, message):
		input_command = ""
		windows = self.windows

		print("message yielded (send) %s" % message)
		windows["console_input"].addstr(0, 0, message)

		message_s = message.split("\n")
		print("message_s:", message_s)
		print("will be moving to:", len(message_s)-1, len(message_s[-1])+1)

		windows["console_input"].move(len(message_s)-1, len(message_s[-1])+1)  # TODO: crashes when len(message_s) > 3 or 4
#		windows["console_input"].leaveok(False)

		# INPUT
		curses.curs_set(2)
		input_command = self.command_textbox.edit(enter_is_terminate)
		curses.curs_set(False)  # so that it doesn't blink in top left corner. >>> ocasionally blinks thought...

		# removing >>>
		input_command_stripped = input_command[len(message)+1 + message.count("\n"):]
		# if only >>>, then print only \n
		print("INPUT CMD: '%s'" % input_command)
		if input_command == ">>> \n":
			input_command = "\n"

		windows["console_input"].clear()

		windows["fight"].addstr(input_command)  # fight, but s

		print("in generator: %s" % input_command)
		#  yield input_command[:-2]  # removing ending \n
		print("after yield")

		for w in windows:
			windows[w].refresh()
		return input_command_stripped[:-2]  # removing ending \n

	def endCurses(self):
		curses.nocbreak()
		# stdscr.keypad(False)
		curses.echo()

		curses.endwin()


def enter_is_terminate(x):
	if x in (10, 459):  # regular enter, enter on notepad
		x = 7
	return x

WINDOWS = {
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

#curses.wrapper(input_curses)

#input()