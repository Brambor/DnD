import os
import traceback
import sys

from datetime import datetime
from time import sleep

from modules.CustomCurses import CustomCurses
from modules.CustomInput import CustomInput
from modules.Game import Game
from modules.Parser import Parser
from modules.CustomPrint import CustomPrint

from library.Main import library

try:
	from settings import local_settings as settings
except ImportError:
	input("Did you forget to copy 'settings/local_settings_default.py' to a file named 'settings/local_settings.py'?")
	raise

"""
class Effect():
	def __init__(self):
		pass
"""

path_to_DnD = sys.path[0]

def wrapper(func, stdin=None, **kwargs):
	try:
		func(**kwargs)
	except EOFError:
		print("EOF happened")
		cPrint("ERROR EOF happened\n")
	except Exception as e:
		cPrint("ERROR Exception happened\n")
		cCurses.endCurses()
		print("\n\n")
		if stdin:
			sys.stdin = stdin
		traceback.print_exc(file=sys.stdout)
		input("CRASHED, PRESS ENTER")
		raise

def regular_wrap():
	while P.input_command():
		pass

def test_wrap(test, len_f_copy):
	cPrint("test name: %s\n" % test)
	sleep(1)
	while (cInput.i+1 < len_f_copy) and P.input_command():
		sleep(0.1)
	cPrint("\n\n\n\n")

do_tests = False
if settings.AUTO_INPUT:
	tests = [f[5:-4] for f in os.listdir("%s/tests" % path_to_DnD)]
	print("Avaiable tests: %s" % ", ".join(tests))

	while True:
		the_input = input("Press enter if you wish to proceed.\nWrite '[t]est' to run all tests. Write 'test_name*' to select which tests to run.\n'*' is a symbol\n>>> ")
		if the_input == "":
			break
		elif the_input in ("test", "t"):
			do_tests = True
			break
		else:
			do_tests = True
			tests_selected = the_input.split()
			good = True
			for t in tests_selected:
				if t not in tests:
					print("'%s' is not a valid test." % t)
					good = False
			if not good:
				continue
			tests = tests_selected
			break

if not do_tests:
	# REGULAR USE
	if settings.LOG:
		current_time = str(datetime.today()).split(".")[0]
	else:
		current_time = None

	cCurses = CustomCurses(settings.COLOR_PALETTE, settings.COLOR_USAGE)
	windows = cCurses.windows
	curses = cCurses.curses

	cPrint = CustomPrint(path_to_DnD, windows, cCurses, log_file=current_time)
	cInput = CustomInput(cPrint, cCurses, input_stream=False)

	G = Game(library, cPrint, cCurses)
	P = Parser(G, cInput, cPrint, settings.DEBUG)
	
	wrapper(regular_wrap)

	cCurses.endCurses()
	input("You are exiting")
else:
	# TESTING
	f1 = sys.stdin

	cCurses = CustomCurses(settings.COLOR_PALETTE, settings.COLOR_USAGE)
	windows = cCurses.windows
	curses = cCurses.curses

	cPrint = CustomPrint(path_to_DnD, windows, cCurses)
	cInput = CustomInput(cPrint, cCurses, input_stream=True, test_environment=True)  # input_stream latter changed 

	for test in tests:
		cInput.i = 0
		path = '%s/tests/test_%s.txt' % (path_to_DnD, test)
		f = open(path,'r')
		f_copy = open(path,'r').read().split("\n")
		cInput.input_stream = f_copy

		G = Game(library, cPrint, cCurses)
		P = Parser(G, cInput, cPrint, settings.DEBUG)
		sys.stdin = f

		wrapper(test_wrap, stdin=f1, test=test, len_f_copy=len(f_copy))

		f.close()
	f.close()

	cPrint("TESTS ARE DONE\n")
	sys.stdin = f1

	cInput.test_environment = False
	cInput.input_stream = False

	wrapper(regular_wrap)

	cCurses.endCurses()
	input("You are exiting")
