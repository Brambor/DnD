import os


class CustomInput():
	def __init__(self, Connector):
		self.C = Connector
		self.i = 0  # used in DnD.py/test_wrap

	def __call__(self, message=""):
		if message:
			message += " >>>"
		else:
			message = ">>>"
		if self.C.test_environment:
			res = self.C.Curses.send_test(message)
			self.i += 1
		else:
			res = self.C.Curses.send(message)

		self.write_to_log(message, res)
		return res

	def write_to_log(self, message, res):
		if not self.C.log_file:
			return
		logs_path = f"{self.C.path_to_DnD}/logs"
		if not os.path.exists(logs_path):
			os.mkdir(logs_path)
		with open(f"{logs_path}/{self.C.log_file}.txt", "a") as log_file:
			log_file.write(f"{message}{res}\n")
		with open(f"{logs_path}/{self.C.log_file} only input.txt", "a") as log_file:
			log_file.write(f"{res}\n")
