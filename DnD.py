import os
import sys

from datetime import datetime
from time import sleep

from library.Main import output_library

from modules.Connector import Connector
from modules.CustomCurses import CustomCurses
from modules.CustomInput import CustomInput
from modules.CustomPrint import CustomPrint
from modules.Game import Game
from modules.Parser import Parser
from modules.SettingsLoader import settings, output_settings


path_to_DnD = sys.path[0]

do_tests = False
if settings.AUTO_INPUT:
	tests = [f[5:-4] for f in os.listdir(f"{path_to_DnD}/tests")]
	print(f'Avaiable tests: {" ".join(tests)}')

	while True:
		the_input = input("Press enter if you wish to proceed.\n"
			"Write '[t]est' to run all tests.\n"
			"Write 'test_name*' to select which tests to run.\n"
			"'*' is a symbol\n"
			">>> "
		)
		if the_input in ("test", "t"):
			do_tests = True
		elif the_input:
			do_tests = True
			tests_selected = the_input.split()
			for t in tests_selected:
				if t not in tests:
					print(f"'{t}' is not a valid test.")
					do_tests = False
			if not do_tests:
				continue
			tests = tests_selected
		break

if (not do_tests and settings.LOG) or (do_tests and settings.LOG_TEST):
	current_time = str(datetime.today()).split(".")[0]
else:
	current_time = None

C = Connector(path_to_DnD, log_file=current_time)
cCurses = CustomCurses(C)
cInput = CustomInput(C,
	input_stream=do_tests,  # in TESTING input_stream changed
	test_environment=do_tests)
cPrint = CustomPrint(C)

if not do_tests:
	# REGULAR USE
	G = Game(C)
	P = Parser(C)
	C.populate(cCurses, cInput, cPrint, G)
else:
	# TESTING
	f1 = sys.stdin
	for test in tests:
		cInput.i = 0
		path = '%s/tests/test_%s.txt' % (path_to_DnD, test)
		f = open(path,'r')
		f_copy = open(path,'r').read().split("\n")
		cInput.input_stream = f_copy

		G = Game(C)
		P = Parser(C)
		C.populate(cCurses, cInput, cPrint, G)

		sys.stdin = f

		cPrint(f"test name: {test}\n")
		sleep(settings.TEST_WAIT_BETWEEN_TESTS)
		try:
			while (cInput.i+1 < len(f_copy)) and P.input_command():
				sleep(settings.TEST_WAIT_BETWEEN_COMMANDS)
		except ValueError as e:
			raise Exception(f"test failed: {test}") from e
		cPrint("\n\n\n\n")

		f.close()

	cPrint("TESTS ARE DONE\n")
	sys.stdin = f1

	cInput.test_environment = False
	cInput.input_stream = False

for line in (*output_settings, *output_library):
	cPrint(f"{line}\n")
while P.input_command():
	pass

cCurses.endCurses()
if settings.EXIT_MESSAGE:
	input("You are exiting")
