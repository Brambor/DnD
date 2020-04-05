# If you want to change something:
# Copy this file, name the copy 'settings_local.py'.
# The copied file contains personal settings that you should customize.

DEBUG = False  # True: When something goes wrong, the program prints error, waits for input, then crashes; False: it prints "fcked up" and carries on.
AUTO_INPUT = False  # True: when DnD is run, DnD asks which tests to run, if any
LOG = True  # Log while not testing. As the program runs, it logs all input and outputs into two files (one for inputs only, the other for everything, inputs are not numbered, unlike with tests)
LOG_TEST = False  # Log while testing.

EXIT_MESSAGE = True # True: on exit prevent closing terminal right away with exit message requiring enter press

SEPARATORS = ["|", ";", "&"]

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
	"entity_played_this_turn": ("white", "grey300"),  # used for when entity played this turn already
	"HP": ("green", "black"),  # used for hp/hp_max
	"mana": ("cyan", "black"),  # used for mana/mana_max ; group names
}

WINDOWS = {
	"fight": {
		"left_top": ("0", "0"),
		"width_height": ("(2*x+1)//3", "y-3"),
	},
	"entities": {
		"left_top": ("(2*x+1)//3", "0"),
		"width_height": ("(x+1)//3", "(y-1)//3"),
		"scrollok": False,
	},
	"inventory": {
		"left_top": ("(2*x+1)//3", "(y-1)//3"),
		"width_height": ("(x+1)//3", "(y-2)//3"),
		"scrollok": False,
	},
	"history": {
		"left_top": ("(2*x+1)//3", "(y-1)//3 + (y-2)//3"),
		"width_height": ("(x+1)//3", "(y-3)//3"),
	},
	"console_input": {
		"left_top": ("0", "y-3"),
		"width_height": ("x", "3"),
	},
}

