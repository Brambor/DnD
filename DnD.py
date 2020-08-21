import os
import sys

from datetime import datetime
from time import sleep, time

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

if do_tests and settings.LOG_TEST:
	current_time = str(datetime.today()).split(".")[0]
else:
	current_time = None

C = Connector(path_to_DnD, log_file=current_time, test_environment=do_tests)
cCurses = CustomCurses(C)
cInput = CustomInput(C)
cPrint = CustomPrint(C)

if not do_tests:
	# REGULAR USE
	G = Game(C)
	P = Parser(C)
	C.populate(cCurses, cInput, cPrint, G)
else:
	# TESTING
	f1 = sys.stdin
	start = time()
	for test in tests:
		cInput.i = 0
		path = '%s/tests/test_%s.txt' % (path_to_DnD, test)
		f = open(path, 'r')
		f_lines = open(path, 'r').read().split("\n")

		G = Game(C)
		P = Parser(C)
		C.populate(cCurses, cInput, cPrint, G)

		sys.stdin = f

		if test == tests[-1] and settings.LOG:
			C.start_logging(str(datetime.today()).split(".")[0])
		cPrint(f"test name: {test}\n")
		sleep(settings.TEST_WAIT_BETWEEN_TESTS)
		try:
			while (cInput.i+1 < len(f_lines)) and P.input_command():
				sleep(settings.TEST_WAIT_BETWEEN_COMMANDS)
		except ValueError as e:
			raise Exception(f"test failed: {test}") from e
		cPrint("\n\n\n\n")

		f.close()
	total = time() - start

	wait = 0
	count_cmds = 0
	for test in tests:
		path = f'{path_to_DnD}/tests/test_{test}.txt'
		file_lines = open(path, 'r').read().split("\n")
		wait += (len(file_lines) - 1) * settings.TEST_WAIT_BETWEEN_COMMANDS
		count_cmds += (len(file_lines) - 1)
	wait += len(tests) * settings.TEST_WAIT_BETWEEN_TESTS
	count_tests = len(tests)

	cPrint("TESTS ARE DONE\n"
		f"Tests took {round(total, 3)} seconds.\n"
		f"\tExpected computing {round(total-wait, 2)}s, exp. waiting {round(wait, 2)}s (set in settings).\n"
		f"\tRan {count_tests} tests with total of {count_cmds} lines.\n")
	sys.stdin = f1

	C.test_environment = False

for line in (*output_settings, *output_library):
	cPrint(f"{line}\n")
while P.input_command():
	pass

cCurses.endCurses()
if settings.EXIT_MESSAGE:
	input("You are exiting")
