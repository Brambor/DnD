import os

class CustomInput():
	"log_file is path to file where the output is saved\
	input_stream bool(input_stream) == True: given message is printed ('print', not 'CustomPrint') - for purposes of tests\
	input_handlerer is a object accepting message via send and returning resulting command"
	def __init__(self, cPrint, input_handlerer, input_stream=False, test_environment=False):
		self.path_to_DnD = cPrint.path_to_DnD
		self.input_stream = input_stream
		self.input_handlerer = input_handlerer
		self.i = 0
		self.log_file = cPrint.log_file
		self.cPrint = cPrint
		self.test_environment = test_environment

	def __call__(self, message):
		if self.test_environment:
			res = self.input_handlerer.send_test(message)
		else:
			res = self.input_handlerer.send(message)

		if self.log_file:
			self.write_to_log(message, res)

		if self.input_stream:
			self.i += 1
		return res

	"""
	HISTORY
	def print_history(self):
		for h in self.input_handlerer.history:
			self.cPrint("%s\n" % h)
		self.cPrint("history_pointer/len(history)=%d/%d\n" % (self.input_handlerer.history_pointer, len(self.input_handlerer.history)))
	"""

	def write_to_log(self, message, res):
		logs_path = "%s/logs" % self.path_to_DnD
		if not os.path.exists(logs_path):
			os.mkdir(logs_path)
		with open(("%s/%s.txt" % (logs_path, self.log_file)), "a") as log_file:
			log_file.write("%s%s\n" % (message, res) )
		with open(("%s/%s only input.txt" % (logs_path, self.log_file)), "a") as log_file:
			log_file.write("%s\n" % res)
