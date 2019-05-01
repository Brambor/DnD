from copy import copy

from modules.CustomInput import CustomInput
from modules.Game import Game
from modules.Parser import Parser
from modules.CustomPrint import CustomPrint

from library.Main import library

DEBUG = True  # True: The program crashes when something goes wrong; False: it prints "fcked up" and carries on
AUTO_INPUT = False  # False: regular use; True: One of the tests (or all of them, this is based on setup/code) are run
LOG = False  # AUTO_INPUT must be False for this to work. False: Nothing; True: As the program runs, it logs all input and outputs into two files (one for inputs only, the other for everything, inputs are not numbered, unlike with tests)

"""
class Effect():
	def __init__(self):
		pass
"""
if not AUTO_INPUT:
	# REGULAR USE

	if LOG:
		import datetime
		current_time = str(datetime.datetime.today()).split(".")[0]
	else:
		current_time = None

	cInput = CustomInput(log_file=current_time, input_stream=False)
	cPrint = CustomPrint(log_file=current_time)

	G = Game(library, cPrint)
	P = Parser(G, cInput, cPrint, DEBUG)

	"""
	e = G.create("pes", "a")
	e = G.create("pes", "b")
	e = G.create("Thorbald", "t")

	print([str(e) for e in G.entities])
	"""
	while True:
		P.input(">>>")
else:
	# TESTING
	import sys
	f1 = sys.stdin

	for test in ("basics cast fight freeze freeze_fire freeze_hard help").split():
		path = 'tests/test_%s.txt' % test
		f = open(path,'r')
		f_copy = open(path,'r').read().split("\n")

		cInput = CustomInput(log_file=None, input_stream=f_copy)
		cPrint = CustomPrint(log_file=None)

		G = Game(library, cPrint)
		P = Parser(G, cInput, cPrint, DEBUG)

		sys.stdin = f
		print("test name: %s" % test)
		while cInput.i+1 < len(f_copy):
			P.input("%d>>>" % (cInput.i+1))
		print("\n\n\n\n")

	f.close()

	sys.stdin = f1
	input("DONE (AUTO_INPUT was set to True)")
