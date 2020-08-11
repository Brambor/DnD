import re


if __name__ != "__main__":
	from library.Main import library
	from modules.SettingsLoader import settings
else:
	print("[fake settings]")
	class A():
		def __init__(self):
			self.SEPARATORS = ["|", ";", "&"]
	settings = A()
	library = {
		"damage_types",
		"effects",
		"entities",
		"items",
		"spells",
		"skills",
	}

def separate(splitted_parts):
	">>> separate('hello there | my args & how are ya 7?'.split())"
	"['hello there', 'my args', 'how are ya 7?']"
	return [part.strip() for part in re.split("|".join("\\%s" % s for s in settings.SEPARATORS), " ".join(splitted_parts))]

cmd = (
	("#", "//"),
	("attack", "a"),
	("help", "h"),
	("create", "c"),
	("compare", "cmp"),
	("damage", "dmg", "d"),
	("effect", "e"),
	("erase",),
	("eval",),
	("exit",),
	("file",),
	("heal",),
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
	"?": "Symbol '?' means optional zero or one.\n",
	"|": "Symbol '|' is a separator."
		f" Separators are {', '.join(repr(s) for s in settings.SEPARATORS)} set in 'settings.SEPARATORS'.\n",
}

math_expression = (
	"\texpression can contain multiplication, rational numbers, die in form dX where X is number of sides\n"
	"\tab is not multiplication, a*b is\n"
	"\t0.5 5 1/3 are all acceptable, '0,5' is not\n"
	"\tfor each dX one dice is thrown, 3*dX is result of throwing a dice multiplied by 3\n"
)

strs = {
#	"cmd": cmd,
	"help": {
		"commands": (
			"Write command without any more arguments for further help,\n"
			"or 'help command/cmd command' which works for commands without arguments too.\n"
			"\tsecond 'command' is one of commands, such as 'turn', 'move'...\n"
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
		"Use ctrl+z and ctrl+y to move backwards and forwards in history.\n"
		"Use command 'exit' or press 'alt + f4' to exit.\n"
	),
	"commands": {
		"#": (
			"# or // command_body\n"
			"\tcommand_body will be printed. This command does nothing else.\n"
		),
		"attack": (
			"[a]ttack entity\n"
			"\tshow attacks list(with details) of entity\n"
			"[a]ttack entity attack_how target+\n"
			"\tcalculate 'attack_how', apply dmg to 'target+'\n"
			f'\t{symbol["+"]}'
		),
		"create": (
			"[c]reate entity_library nickname*\n"
			"\t'entity_library' can be listed via command 'library entities' 'l en' for short.\n"
			"\tif 'nickname' is '_', automatic nickname is used\n"
			"\tc pes <==> c pes _\n"
			"\trunning 'c pes' twice <==> c pes _ _\n"
			f'\t{symbol["*"]}'
		),
		"compare": (
			"compare/cmp entity1 skill1 val1 entity2 skill2 val2\n"
			"\tprobably throws a die to see who won\n"
			"\tskill determines which skill is entity using\n"
			"\tval is integer, 'a' or 'auto' for auto based on skill\n"
			"compare/cmp val1 val2\n"
			"\tprobably throws a die to see what is more\n"
			"\tval is either integer or dice in format 'dx' where x is integer\n"
		),
		"dmg": (
			"[d]amage/dmg (damage_types* {expression})+ | target+\n"
			"\tdamages target+ by calculated ammount with respective damage_types\n"
			"\texample:\n"
			"\tdamage physical blunt {45+12+4-2+d8} fire elemental {(d4+10)*0.5} ... | entity_1 entity_2 ...\n"
			"\n"
			"\tdamage_type are listed in 'library damage_types'\n"
			"\n"
			f'{math_expression}'
			"\n"
			f'\t{symbol["*"]}'
			f'\t{symbol["+"]}'
			f'\t{symbol["|"]}'
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
		"exit": "Exits the program.\n",
		"file": (
			"WARNING(!): Warnings not yet implemented!\n"
			"file list\n"
			"\tlists currently saved files\n"
			"file save\n"
			"\tsaves game to a file associated with this game\n"
			"\tsave becomes associated file, when it is loaded or saved\n"
			"file save file_name\n"
			"\tsaves game to 'saves/file_name'\n"
			"\tto prevent human mistake, it is prefered to use 'file save' to save to associated file\n"
			"file load file_name\n"
			"\twarns(!), then deletes game and loads 'saves/file_name'\n"
			"file delete file_name\n"
			"\twarns(!), then deletes 'saves/file_name'\n"
		),
		"heal": (
			"heal expression+ | target+\n"
			"\theals target+ by calculated ammount\n"
			"\texample:\n"
			"\theal 45+12+4-2+d8 + (d4+10)*0.5 ... | entity_1 entity_2 ...\n"
			"\n"
			f"{math_expression}"
			"\n"
			f'\t{symbol["+"]}'
			f'\t{symbol["|"]}'
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
			"\tWHAT can be [en]tities, [ef]fects, [[s]p]ells, [i]tems, "
			f'{", ".join( set(library) - {"entities", "effects", "spells", "items"})}\n'
			"\tduplicates (a1, a2, a3 are the same, different from b1) are printed in 'a1/a2/a3, b1, c1/c2' form\n"
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
			f'{symbol["+"]}'
		),
		"set": (
			"set entity\n"
			"\tprints all stats of entity\n"
			"set entity stat\n"
			"\tprints 'stat' of entity\n"
			"set entity stat to_expression\n"
			"\tchanges entity's 'stat' to value calculated from 'to_expression'\n"
			"set entity stat expression stat_type\n"
			"\tmakes new 'stat' for 'entity' with value calculated from 'expression' of type 'stat_type'\n"
			"\t'stat_type' can be one of 'int', 'float', 'str', or 'bool'\n"
		),
		"spell": (
			"[s]pell/cast caster_entity spell manual_dice? | target_entity+\n"
			"\tspell must be from library.spells\n"
			f'\t{symbol["?"]}'
			f'\t{symbol["+"]}'
			f'\t{symbol["|"]}'
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
			"\tprints (width, height) of window\n"
			"w get_top_left/gtl what_window\n"
			"\tprints (y, x) of top left corner\n\n"

			"w set_size/ss what_window width height\n"
			"\tset window size to (width, height)\n"
			"w set_top_left/stl what_window y x\n"
			"\tset window top left corner to (y, x)\n"
		),
	},
}

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
