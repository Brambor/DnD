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

	cCurses = CustomCurses()
	windows = cCurses.windows


	cPrint = CustomPrint(windows, log_file=current_time)
	cInput = CustomInput(cPrint, cCurses, log_file=current_time, input_stream=False)

	G = Game(library, cPrint)
	P = Parser(G, cInput, cPrint, settings.DEBUG)
	try:
		while True:
			command = cInput(">>>")
			if command == "&" and settings.DEBUG:
				crash  # force crash
			if command == "exit":
				break  # force crash

			print ("in cycle: %s" % command)
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
	f1 = sys.stdin

	for test in ("basics cast dead_splash dmg effect_stats fight freeze freeze_fire freeze_hard help").split():
		path = 'tests/test_%s.txt' % test
		f = open(path,'r')
		f_copy = open(path,'r').read().split("\n")

		cPrint = CustomPrint(log_file=None)
		cInput = CustomInput(cPrint, log_file=None, input_stream=f_copy)

		G = Game(library, cPrint)
		P = Parser(G, cInput, cPrint, settings.DEBUG)

		sys.stdin = f
		print("test name: %s" % test)
		while cInput.i+1 < len(f_copy):
			P.input("%d>>>" % (cInput.i+1))
		print("\n\n\n\n")

	f.close()

	sys.stdin = f1
	input("DONE (settings.AUTO_INPUT was set to True)")
