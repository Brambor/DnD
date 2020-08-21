# If you want to change something:
# Copy this file, name the copy 'settings_local.py'.
# The copied file contains personal settings that you should customize.

DEBUG = False  # True: When something goes wrong, the program prints error, waits for input, then crashes; False: it prints "fcked up" and carries on.

TAB_WIDTH = 3  # How many spaces is one tab.
OVERFLOW_INDICATOR = "\\O"  # This text will be print in COLOR_USAGE["error"] color if window overflows. It can be multiple characters, the first character should always display, the rest are not guaranteed.

AUTOSAVE_SLOT_COUNT = 5  # Determines number of autosave slots, it cycles through them (autosave_0 .. autosave_{n-1}). Any natural number, n <= 0 results in no autosaving.

LOG = True  # Log while not testing. As the program runs, it logs all input and outputs into two files (one for inputs only, the other for everything)
LOG_TEST = False  # Log while testing. (separate file from LOG, if LOG, then last test is in the LOG file).

EXIT_MESSAGE = True # True: on exit prevent closing terminal right away with exit message requiring enter press

SEPARATORS = ["|", ";", "&"]

AUTO_INPUT = False  # True: when DnD is run, DnD asks which tests to run, if any
TEST_WAIT_BETWEEN_COMMANDS = 0.1
TEST_WAIT_BETWEEN_TESTS = 1
TEST_CRASH_ON_UNKNOWN_COMMAND = True

# COLORS
"""
predefined:
"black"
"blue"
"green"
"cyan"
"red"
"magenta"
"yellow"
"white"
"""

# "color_name": (R, G, B)
# where each color component is between 0 and 1000
COLOR_PALETTE = {
	"grey300": (300, 300, 300),
}

# "name": foreground, background
# name must be defined in code, fore/back are colors, either baisic or user defined in COLOR_PALETTE
COLOR_USAGE = {
	"basic": ("white", "black"),
	"error": ("red", "white"),
	"entity_played_this_turn": ("white", "grey300"),  # used for when entity played this turn already
	"HP": ("green", "black"),  # used for hp/hp_max
	"mana": ("cyan", "black"),  # used for mana/mana_max ; group names
	"derived_from": ("yellow", "black"),  # used in "entities window" for derived from (such as "pes" in "pes a_0 100/1...")
}

# used when Curses cannot change colors; all pairs in COLOR_USAGE that use COLOR_PALETTE should be replaced
# otherwise it will crash when Curses cannot change colors
COLOR_USAGE_BASIC = {
	"entity_played_this_turn": ("white", "blue"),  # used for when entity played this turn already
}

WINDOWS = {
	"fight": {
		"left_top": ("0", "0"),
		"width_height": ("(2*x+1)//3", "y-3"),
	},
	"entities": {
		"left_top": ("(2*x+1)//3", "0"),
		"width_height": ("(x+1)//3", "(y+2)//3 + y//3"),
		"scrollok": False,
	},
	"history": {
		"left_top": ("(2*x+1)//3", "(y+2)//3 + y//3"),
		"width_height": ("(x+1)//3", "(y+1)//3"),
	},
	"console_input": {
		"left_top": ("0", "y-3"),
		"width_height": ("(2*x+1)//3", "3"),
	},
}
