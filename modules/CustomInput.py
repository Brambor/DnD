import os

class CustomInput():
	"(file)input_stream (if input_stream): given message is printed ('print', not 'CustomPrint') - for purposes of tests"
	def __init__(self, Connector, input_stream=False, test_environment=False):
		self.C = Connector
		self.input_stream = input_stream
		self.i = 0  # used in DnD.py/test_wrap
		self.test_environment = test_environment

	def __call__(self, message):
		if self.test_environment:
			res = self.C.Curses.send_test(message)
		else:
			res = self.C.Curses.send(message)

		if self.C.log_file:
			self.write_to_log(message, res)

		self.i += bool(self.input_stream)
		return res

	def write_to_log(self, message, res):
		logs_path = "%s/logs" % self.C.path_to_DnD
		if not os.path.exists(logs_path):
			os.mkdir(logs_path)
		with open(("%s/%s.txt" % (logs_path, self.C.log_file)), "a") as log_file:
			log_file.write("%s%s\n" % (message, res) )
		with open(("%s/%s only input.txt" % (logs_path, self.C.log_file)), "a") as log_file:
			log_file.write("%s\n" % res)
