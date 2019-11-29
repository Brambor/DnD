import re


if __name__ == "__main__":
	print("[fake settings]")
	class A():
		def __init__(self):
			self.SEPARATORS = ["|", ";", "&"]
	settings = A()
else:
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
	("#", "//"),
	("help", "h"),
	("create", "c"),
	("compare", "cmp"),
	("damage", "dmg", "d", "attack", "a"),
	("effect", "e"),
	("erase",),
	("eval",),
	("exit",),
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


symbol = {
	"+": "Symbol '+' means at least one, as many as you want.\n",
	"*": "Symbol '*' means optional (at least zero), as many as you want.\n",
	"|": "Symbol '|' is separator, required when there are more arguments with '+' or '*'."
		" Separators are %s set in 'settings.SEPARATORS'.\n" % ", ".join("'%s'" % s for s in settings.SEPARATORS),
}

strs = {
#	"cmd": cmd,
	"help": {
		"commands": (
			"Write command without any more arguments for further help,\n"
			"or 'help command/cmd command' which works for commands without arguments too.\n"
			"\tsecond 'command' is one of commands, such as 'turn', 'move', 'fight'...\n"
			"\texample: 'help cmd turn'\n"
			"See example usage in directory 'tests'.\n"
			"COMMANDS:\n"
			"\t%s\n" % "\n\t".join(", ".join(c) for c in cmd)
		),
		"entity_reference": (
			"'entity' can be referenced via entity nickname or entity id.\n"
			"e.g. for entity 'a_0' either 'a' (entity nickname) or '0' (entity id) works.\n"
			"Then commands 'move a' & 'move 0' are equivalent.\n"
		),
		"symbol": symbol,
	},
	"help_general": (
		"General help: use 'help WHAT' for more detailed help.\n"
		"\tWHAT can be: %s\n"
		"If something doesn't work or you don't understand something TELL ME, please!\n"
		"\tIt means that something is wrongly implemented or documented!\n"
		"Use command 'exit' or press 'alt + f4' to exit.\n"
	),
	"commands": {
		"#": (
			"# or // command_body\n"
			"\tcommand_body will be printed. This command does nothing else."
		),
		"create": (
			"[c]reate entity_library nickname_to_be_set\n"
			"\t'entity_library' can be listed via command 'library entities' 'l en' for short.\n"
		),
		"compare": (
			"compare/cmp entity1 skill1 val1 entity2 skill2 val2\n"
			"\tprobably throws a die to see who won\n"
			"\tskill determines which skill is entity using\n"
			"\tval is integer, 'a' for auto based on skill\n"
			"compare/cmp val1 val2\n"
			"\tprobably throws a die to see what is more\n"
			"\tval is either integer or dice in format 'dx' where x is integer\n"
		),
		"dmg": (
			"[d]amage/dmg/[a]ttack source_text | type_of_dmg base_dmg dice(die)* | target(s)+\n"
			"\tsource_text is string latter used in log message (it is NOT optional, thought it is vaguely saved)\n"
			"\tdamage_type ([p]hysical/[m]agic/[t]rue)\n"
			"\tdie are row integers representing used dice(die)\n"
			"\ttarget_entity_1 target_entity_2 ...\n"
			"\t%s" % symbol["*"]
			+"\t%s" % symbol["+"]
			+"\t%s" % symbol["|"]
		),
		"effect": (
			"[e]ffect entity effect dice\n"
			"\tadds 'effect' with dice 'dice' to 'entity'\n"
		),
		"erase": (
			"erase entity\n"
			"\tnot to be confused with 'remove'\n"
			"\terases entity\n"
		),
		"eval": (
			"eval command\n"
			"\tbetter not use that!\n"
		),
		"exit": "Exits the program.",
		"fight": (
			"[f]ight entity1 entity2 val1 val2 manual_dice\n"
			"\tval is integer, 'a' for auto\n"
			"%s"
			"\tboj entity1 entity2 <==> boj entity1 entity2 a a <!=!=!> boj entity1 entity2 a a anything\n"
		),
		"inventory": (
			"[i]nventory entity\n"
			"\tchoose entity's inventory to be listed in inventory window; lists items in inventory\n"
			"[i]nventory entity add/del item\n"
			"\titem is from item_library\n"
			"[i]nventory entity mod item key value\n"
			"\titem is from entity's inventory\n"
			"\tkey & value are it's key & value respectively\n"
			"\tvalue is transformed into int if possible\n"
		),
		"library": (
			"[[l]ib]rary/list WHAT\n"
			"\tWHAT can be [en]tities, [ef]fects, [[s]p]ells, [i]tems\n"
		),
		"move": (
			"[m]ove target_entity_1 target_entity_2 ...\n"
			"\ttoggles all selected entities played_this_turn\n"
		),
		"remove_effect": (
			"remove_effect entity\n"
			"\tnot to be confused with 'erase'\n"
			"\tprints all effects of entity in numbered order\n"
			"ef+\n"
			"\tef are numbers of effects to remove\n"
			+symbol["+"]
		),
		"set": (
			"set entity\n"
			"\tprints all stats of entity\n"
			"set entity stat to_value\n"
			"\tchanges entity's 'stat' to 'to_value'\n"
			"set entity stat value stat_type\n"
			"\tmakes new 'stat' for 'entity' with 'value' of type 'stat_type'\n"
			"\t'stat_type' can be one of 'int', 'str', or 'bool'\n"
		),
		"spell": (
			"1) [s]pell/cast caster_entity spell manual_dice\n"
			"\tspell must be from library.spells\n"
			"%s"
			"2) target_entity_1 target_entity_2 ...\n"
		),
		"turn": (
			"For each entity applies all its effects.\n"
			"If all entities played this turn (command 'move'),\n"
			"unmove all entities and make new round.\n"
			"Rounds are not counted, turns are.\n"
		),
		"window": (
			"w <==> window; ([w]indow)\n"
			"w show sleep_for\n"
			"\tdisplays windows (what + size) for sleep_for secs\n\n"  # TODO until enter is pressed
			
			"w get_size/gs what_window\n"
			"\tprints (height, width) of window\n"
			"w get_top_left/gtl what_window\n"
			"\tprints (y, x) of top left corner\n\n"

			"w set_size/ss what_window ncols nlines\n"
			"\tset window size to (ncols, nlines)\n"
			"w set_top_left/stl what_window y x\n"
			"\tset window top left corner to (y, x)\n"
		),
	},
}

# adding missing strings
manual_dice = (
	"\tif manual_dice, dice are not thrown automatically\n"
	"\tmanual_dice must be one word\n"
)
for command in ("fight", "spell"):
	strs["commands"][command] %= manual_dice

# BEGIN copying
# copying in help
strs["help"]["cmd"] = strs["help"]["commands"]

# copying in general
# TODO: do this as a function / alternative dict lookup?, rather than adding it
for desired_cmd in tuple(strs["commands"]):
	for cmds in cmd:
		if desired_cmd in cmds:
			for c in cmds:
				strs["commands"][c] = strs["commands"][desired_cmd]
			break
# adding missing string 2
strs["help_general"] %= ", ".join(strs["help"])
# copying for help
strs["commands"]["help"] = strs["help_general"]
# END copying

if __name__ == "__main__":
	def pretty(d, indent=0):
		for key, value in d.items():
			print('\t' * indent + str(key))
			if isinstance(value, dict):
				pretty(value, indent+1)
			else:
				for line in value.split("\n"):
					print('\t' * (indent+1) + line)
	pretty(strs)
