class CustomInput():
	"""auto == True: print what has been inputed"""
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
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "a") as log_file:
			log_file.write("%s%s\n" % (message, res) )
		with open(("logs/%s only input.txt" % self.log_file).replace(":", "_"), "a") as log_file:
			log_file.write("%s\n" % res)
