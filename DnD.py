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
if not settings.AUTO_INPUT:
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
		while True:
			command = cInput(">>>")
			if command == "&" and settings.DEBUG:
				crash  # force crash
			if command == "exit":
				break  # force crash

			P.process(command)
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

	for test in ("basics cast dead_splash dmg effect_stats fight freeze freeze_fire freeze_hard groups help move").split():
		cInput.i = 0
		path = 'tests/test_%s.txt' % test
		f = open(path,'r')
		f_copy = open(path,'r').read().split("\n")
		cInput.input_stream = f_copy

		G = Game(library, cPrint, cCurses)
		P = Parser(G, cInput, cPrint, settings.DEBUG)
		sys.stdin = f

		try:
			windows["fight"].addstr("test name: %s" % test)
			windows["fight"].refresh()
			sleep(1)
			while cInput.i+1 < len(f_copy):
				command = cInput(">>>")
				P.process(command)
				sleep(0.1)
			windows["fight"].addstr("\n\n\n\n")
			windows["fight"].refresh()
		except EOFError:
			print("EOF happened")
			windows["fight"].addstr("ERROR EOF happened")
			windows["fight"].refresh()
		except Exception as e:
			windows["fight"].addstr("ERROR Exception happened")
			windows["fight"].refresh()
			cCurses.endCurses()
			print("\n\n")
			print(e)
			sys.stdin = f1
			input("CRASHED, PRESS ENTER")
			raise

	f.close()
	windows["fight"].addstr("TESTS ARE DONE")
	windows["fight"].refresh()
	sys.stdin = f1

	cInput.test_environment = False
	cInput.input_stream = False

	try:
		while True:
			command = cInput(">>>")
			if command == "&" and settings.DEBUG:
				crash  # force crash
			if command == "exit":
				break  # force crash

			P.process(command)
	except Exception as e:
		cCurses.endCurses()
		print("\n\n")
		print(e)
		input("CRASHED, PRESS ENTER")
		raise


	cCurses.endCurses()
	input("DONE (settings.AUTO_INPUT was set to True)")
