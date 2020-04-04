import importlib

from modules.DnDException import DnDException
from modules.Dice import D


def convert_string_to_bool(string):
	if string == "True":
		return True
	elif string == "False":
		return False
	else:
		raise DnDException("Unacceptable value '%s' accepting only 'True' and 'False'." % string)

def get_int_from_dice(n_str):
	if n_str.replace("-", "", 1).isdigit():
		return int(n_str)
	elif n_str.startswith("d") and n_str[1:].isdigit():
		return D(int(n_str[1:]))
	raise DnDException("'%s' is not an integer nor in format 'dx'." % n_str)

def local_loader(global_dict, lib, dicts_name):
	try:
		output = []
		loc_dict = getattr(importlib.import_module(lib), dicts_name)
		output.append("'%s' loaded" % dicts_name)
		for e in loc_dict:
			if e in global_dict:
				output.append("\t'%s' overrode" % e)
		global_dict.update(loc_dict)
		return output
	except ImportError:
		return []

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

def yield_valid(threw_sequence):
	threw = next(threw_sequence)
	if type(threw) != int:
		raise DnDException("Sequence was too short!")
	return threw
