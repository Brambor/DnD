from modules.CustomCurses import CustomCurses
from modules.CustomInput import CustomInput
from modules.CustomPrint import CustomPrint
from modules.Dice import Dice


class Connector():
	def __init__(self, path_to_DnD, log_file, test_environment):
		"log_file is path to file where the output is saved"
		self.path_to_DnD = path_to_DnD
		self.log_file = log_file.replace(":", "_") if log_file else ""
		self.test_environment = test_environment

		self.Curses = CustomCurses(self)
		self.Dice = Dice(self)
		self.Input = CustomInput(self)
		self.Print = CustomPrint(self)

	def populate(self, Game):
		self.Game = Game

	def start_logging(self, log_file):
		self.log_file = log_file.replace(":", "_") if log_file else ""
