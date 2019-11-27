import importlib

from modules.DnDException import DnDException


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

def local_loader(global_dict, lib, dicts_name):
	try:
		loc_dict = getattr(importlib.import_module(lib), dicts_name)
		print("'%s' loaded" % dicts_name)
		for e in loc_dict:
			if e in global_dict:
				print("\t'%s' overrode" % e)
		global_dict.update(loc_dict)
	except ImportError:
		pass
