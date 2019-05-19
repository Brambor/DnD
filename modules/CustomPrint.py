import os

class CustomPrint():
	"log_file is path to the file where the output is saved"
	def __init__(self, log_file=""):
		self.log_file = log_file

	def __call__(self, message=""):
		print(message)
		if self.log_file:
			self.write_to_log(message)

	def write_to_log(self, message):
		if not os.path.exists("logs"):
			os.mkdir("logs")
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "ab") as log_file:
			log_file.write(("%s\n" % message).encode("utf8"))
