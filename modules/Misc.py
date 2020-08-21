import re

from datetime import datetime

from library.Main import library

from modules.DnDException import DnDException


def calculate(string):
	string = string.replace("%", "/100")
	unallowed = set(string) - set("0123456789-+*/.() ><=!")
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

def get_library(which_library, thing):
	"getting things from self.library"
	if which_library not in library:
		raise DnDException("Unknown library '%s'." % which_library)
	else:
		ret = library[which_library].get(thing, None)
		if ret:
			return ret
		raise DnDException("'%s' is not in '%s' library." % (thing, which_library))

def get_now_str():
	return str(datetime.now())[:-7].replace(" ", "--").replace(":", "-")

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

def pretty_print_filename(filename_date):
	("'my_save--2020-08-16--10-15-08' -> 'my_save\t| 2020-08-16 10:15:08'"
	"but only if appendix looks like valid datetime, otherwise '{filename_date}\t| ?'")
	filename = remove_date_from_filename(filename_date)
	if filename == filename_date:
		return f'{filename_date}\t| unknown file save time'
	date = filename_date[-20:]
	return f'{filename}\t| {date[:10]} {date[12:14]}:{date[15:17]}:{date[18:20]}'

def remove_date_from_filename(filename_date):
	("'my_save--2020-08-16--10-15-08' -> 'my_save'"
	"but only if date looks like valid datetime, otherwise return input")
	if len(filename_date) < 23:
		return filename_date  # "ERR short filename"
	date = filename_date[-22:]
	dashes = {0, 1, 6, 9, 12, 13, 16, 19}
	for i in dashes:
		if date[i] != "-":
			return filename_date  # "ERR invalid datetime (not a dash)"
	for i in range(22):
		if i not in dashes and not date[i].isdigit():
			return filename_date  # "ERR invalid datetime (not a digit)"
	return filename_date[:-22]
