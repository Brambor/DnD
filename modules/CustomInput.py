import os

class CustomInput():
	"log_file is path to file where the output is saved\
	input_stream True: given message is printed ('print', not 'CustomPrint')"
	def __init__(self, log_file="", input_stream=False):
		self.input_stream = input_stream
		self.i = 0
		self.log_file = log_file

	def __call__(self, message):
		res = input(message)
		if self.log_file:
			self.write_to_log(message, res)

		if self.input_stream:
			print(self.input_stream[self.i])
			self.i += 1
		return res

	def write_to_log(self, message, res):
		if not os.path.exists("logs"):
			os.mkdir("logs")
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "a") as log_file:
			log_file.write("%s%s\n" % (message, res) )
		with open(("logs/%s only input.txt" % self.log_file).replace(":", "_"), "a") as log_file:
			log_file.write("%s\n" % res)
