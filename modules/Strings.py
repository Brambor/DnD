import re

try:
	from settings import local_settings as settings
except ImportError:
	print("Did you forget to copy 'settings/local_settings_default.py' to a file named 'settings/local_settings.py'?")
	input()
	raise


def separate(splitted_parts):
	splitted_parts = [part.strip() for part in re.split("|".join("\\%s" % s for s in settings.SEPARATORS), " ".join(splitted_parts))]
	return splitted_parts

cmd = (
	# command ("#", "//"),
	("help", "h"),
	("create", "c"),
	("compare", "cmp"),
	("dmg", "d", "attack", "a"),
	("effect", "e"),
	("erase",),
	("eval",),
	("fight", "f"),
	#HISTORY	("history",),
	("inventory", "i"),
	("library", "lib", "list", "l"),
	("move", "m"),
	("remove_effect", "remove", "r"),
	("set",),
	("spell", "s", "cast"),
	("turn", "t"),
	("window", "w"),
)

strs = {
#	"cmd": cmd,
	"placeholder_input_sequence": "placeholder_input_sequence activates inputing sequence latter down the chain; for now any value just means True",
	"help": {
		"commands": (
			"Write command without any more arguments for further help,\n"
			"(except for turn)\n"
			"See example usage in directory 'tests'\n"
			"COMMANDS:\n"
		),
		"symbol": {
			"+": "Symbol '+' means at least one, as many as you want.\n",
			"*": "Symbol '*' means optional (at least zero), as many as you want.\n",
			"|": "Symbol '|' is separator, required when there are more arguments with '+' or '*'."
				" Separators are %s set in 'settings.SEPARATORS'.\n" % ", ".join("'%s'" % s for s in settings.SEPARATORS),
		},
	},
	"help_general": (
		"General help: use 'help WHAT' for more detailed help.\n"
		"\tWHAT can be: %s\n"
		"If something doesn't work or you don't understand somethin TELL ME IMIDIATELY please!\n"
		"It means that something is wrongly implemented or documented!\n"
		"Use 'exit' pseudo command or press 'alt + f4' to exit.\n"
	),
}

for c in (", ".join(c) for c in cmd):
	strs["help"]["commands"] += "\t%s\n" % c
#print("\n\t".join(", ".join(c) for c in cmd))
strs["help"]["entity_reference"] = ("'entity' can be referenced via entity nickname or entity id.\n"
					"e.g. for entity 'a_0' either 'a' (entity nickname) or '0' (entity id) works.\n"
					"Then commands 'move a' & 'move 0' are equivalent.\n"
)

strs["help_general"] %= ", ".join(strs["help"])
