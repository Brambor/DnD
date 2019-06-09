# Copy this file, make one named 'local_settings.py'
# in that file is your personal settings


DEBUG = True  # True: The program crashes when something goes wrong; False: it prints "fcked up" and carries on
AUTO_INPUT = True  # False: regular use; True: One of the tests (or all of them, this is based on setup/code) are run
LOG = False  # AUTO_INPUT must be False for this to work. False: Nothing; True: As the program runs, it logs all input and outputs into two files (one for inputs only, the other for everything, inputs are not numbered, unlike with tests)

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
}
