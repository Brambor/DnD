import re

from library.Main import library

from modules.DnDException import DnDException
from modules.Dice import D, dice_eval, dice_parser


def calculate(string):
	string = string.replace("%", "/100")
	unallowed = set(string) - set("0123456789-+*/.() ")
	if unallowed:
		raise DnDException(f"These character(s) '{''.join(unallowed)}' are not allowed in calculation.\n'{string}'")
	try:
		return eval(string)
	except SyntaxError:
		raise DnDException(f"'{string}' is not a valid mathematical expression.")

def convert_string_to_bool(string):
	if string == "True":
		return True
	elif string == "False":
		return False
	else:
		raise DnDException(f"Unacceptable value '{string}' accepting only 'True' and 'False'.")

def get_int_from_dice(n_str):
	if n_str.replace("-", "", 1).isdigit():
		return int(n_str)
	elif n_str.startswith("d") and n_str[1:].isdigit():
		return D(int(n_str[1:]))
	raise DnDException("'%s' is not an integer nor in format 'dx'." % n_str)

def get_library(which_library, thing):
	"getting things from self.library"
	if which_library not in library:
		raise DnDException("Unknown library '%s'." % which_library)
	else:
		ret = library[which_library].get(thing, None)
		if ret:
			return ret
		raise DnDException("'%s' is not in '%s' library." % (thing, which_library))

def get_valid_filename(s):
	"""
	from https://github.com/django/django/blob/master/django/utils/text.py
	Return the given string converted to a string that can be used for a clean
	filename. Remove leading and trailing spaces; convert other spaces to
	underscores; and remove anything that is not an alphanumeric, dash,
	underscore, or dot.
	>>> get_valid_filename("john's portrait in 2004.jpg")
	'johns_portrait_in_2004.jpg'
	"""
	s = str(s).strip().replace(' ', '_')
	return re.sub(r'(?u)[^-\w.]', '', s)

def normal_round(f):
	return int(f) + ( f - int(f) >= 0.5 )

def parse_damage(string, game):
	"string = 'physical acid {7*d20} acid {7 + d4} acid { d12}'"
	"returns [{'physical', 'acid'}: 14, {'acid'}: 8, {'acid'}: 5]"
	damage_list = []
	crits = set()
	for whole in (type_damage.split("{") for type_damage in string.split("}") if type_damage != ""):
		if len(whole) != 2:
			raise DnDException("%s is %d long, 2 expected.\nMaybe you forgot '{' ?" % (whole, len(whole)))

		types = set()
		for damage_type in whole[0].strip().split():
			if damage_type not in library["damage_types"]:
				raise DnDException("Invalid damage_type '%s'." % damage_type)
			types.add(library["damage_types"][damage_type])  # a -> acid; acid -> acid	

		whole[1], c = dice_eval(whole[1], game)
		crits.update(c)

		# calculate
		damage_list.append((types, calculate(whole[1])))
	return damage_list, crits

def parse_sequence(sequence, carry_when_crit=False):
	"does not process negative integers as integers"
	sequence = sequence.split()
	if len(sequence) == 0:  # or 'not sequence'
		raise DnDException("The sequence contains nothing! WtF?")
	if (len(sequence) > 1) and (carry_when_crit == False):
		raise DnDException("Lenght of sequence > 1, when asked only for one number.")
	for i, word in enumerate(sequence):
		if not word.isdigit():
			raise DnDException("Sequence contains non-digit character '%s'." % word)
		yield int(word)
	# raise: sequence longer than needed to be
	yield "Perfectly right lenght."
