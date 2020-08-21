class Connector():
	def __init__(self, path_to_DnD, log_file, test_environment):
		"log_file is path to file where the output is saved"
		self.path_to_DnD = path_to_DnD
		self.log_file = log_file.replace(":", "_") if log_file else ""
		self.test_environment = test_environment

	def populate(self, cCurses, cInput, cPrint, Game):
		self.Curses = cCurses
		self.Input = cInput
		self.Print = cPrint
		self.Game = Game

	def start_logging(self, log_file):
		self.log_file = log_file.replace(":", "_") if log_file else ""
