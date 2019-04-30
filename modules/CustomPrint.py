class CustomPrint():
	"""auto is a bool deciding whether or not to print the input message
	if auto=True, then """
	def __init__(self, log_file=""):
		self.log_file = log_file

	def __call__(self, message=""):
		print(message)
		if self.log_file:
			self.write_to_log(message)

	def write_to_log(self, message):
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "a") as log_file:
			log_file.write("%s\n" % message)
