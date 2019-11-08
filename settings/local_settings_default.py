# This file is a template designed to be copied and pasted.
# Copy this file, name the copy 'local_settings.py'.
# The copied file contains personal settings that you can customize.


DEBUG = False  # True: When something goes wrong, the program prints error, waits for input, then crashes; False: it prints "fcked up" and carries on.
AUTO_INPUT = True  # True: when DnD is run, DnD asks which tests to run, if any
LOG = True  # False: Nothing; True: As the program runs, it logs all input and outputs into two files (one for inputs only, the other for everything, inputs are not numbered, unlike with tests)

SEPARATORS = ["|", ";", "&"]

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
