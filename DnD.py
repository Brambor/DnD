from modules.CustomCurses import CustomCurses
from modules.CustomInput import CustomInput
from modules.Game import Game
from modules.Parser import Parser
from modules.CustomPrint import CustomPrint

from library.Main import library

try:
	from settings import local_settings as settings
except ImportError:
	print("Did you forget to copy 'settings/local_settings_default.py' to a file named 'settings/local_settings.py'?")
	input()
	raise

"""
class Effect():
	def __init__(self):
		pass
"""

while settings.AUTO_INPUT:
	the_input = input("Press enter if you wish to proceed.\nWrite 'test' if you wish to make tests.")
	if the_input == "":
		do_tests = False
		break
	elif the_input.lower() == "test":
		do_tests = True
		break
	else:
		print("What was '%s'?" % the_input)


if not do_tests:
	# REGULAR USE

	if settings.LOG:
		import datetime
		current_time = str(datetime.datetime.today()).split(".")[0]
	else:
		current_time = None

	cCurses = CustomCurses(settings.COLOR_PALETTE, settings.COLOR_USAGE)
	windows = cCurses.windows
	curses = cCurses.curses

	cPrint = CustomPrint(windows, cCurses, log_file=current_time)
	cInput = CustomInput(cPrint, cCurses, log_file=current_time, input_stream=False)

	G = Game(library, cPrint, cCurses)
	P = Parser(G, cInput, cPrint, settings.DEBUG)
	try:
		while P.input_command():
			pass
	except Exception as e:
		cCurses.endCurses()
		print("\n\n")
		print(e)
		input("CRASHED, PRESS ENTER")
		raise
	cCurses.endCurses()
	input("You are exiting")

else:
	# TESTING
	import sys
	from time import sleep
	f1 = sys.stdin

	cCurses = CustomCurses(settings.COLOR_PALETTE, settings.COLOR_USAGE)
	windows = cCurses.windows
	curses = cCurses.curses

	cPrint = CustomPrint(windows, cCurses)
	cInput = CustomInput(cPrint, cCurses, input_stream=True, test_environment=True)  # input_stream latter changed 

	for test in ("basics cast dead_splash dmg effect_stats erase fight freeze freeze_fire freeze_hard groups help inventory move").split():
		cInput.i = 0
		path = 'tests/test_%s.txt' % test
		f = open(path,'r')
		f_copy = open(path,'r').read().split("\n")
		cInput.input_stream = f_copy

		G = Game(library, cPrint, cCurses)
		P = Parser(G, cInput, cPrint, settings.DEBUG)
		sys.stdin = f

		try:
			cPrint("test name: %s\n" % test)
			sleep(1)
			while (cInput.i+1 < len(f_copy)) and P.input_command():
				sleep(0.1)
			cPrint("\n\n\n\n")
		except EOFError:
			print("EOF happened")
			cPrint("ERROR EOF happened\n")
		except Exception as e:
			cPrint("ERROR Exception happened\n")
			cCurses.endCurses()
			print("\n\n")
			print(e)
			sys.stdin = f1
			input("CRASHED, PRESS ENTER")
			raise

	f.close()
	cPrint("TESTS ARE DONE\n")
	sys.stdin = f1

	cInput.test_environment = False
	cInput.input_stream = False

	try:
		while P.input_command():
			pass
	except Exception as e:
		cCurses.endCurses()
		print("\n\n")
		print(e)
		input("CRASHED, PRESS ENTER")
		raise

	cCurses.endCurses()
	input("DONE (settings.AUTO_INPUT was set to True)")
