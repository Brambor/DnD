import os

class CustomPrint():
	"log_file is path to the file where the output is saved\
	windows are the four window object used for communication (courses.window)"
	def __init__(self, windows, log_file=""):
		self.log_file = log_file
		self.windows = windows

	def __call__(self, message="", info_type="fight"):
		if info_type == "fight":
			self.windows[0].addstr("\n" + message)  # fight window
			self.windows[0].refresh()
		print(message)
		if self.log_file:
			self.write_to_log(message)

	def write_to_log(self, message):
		if not os.path.exists("logs"):
			os.mkdir("logs")
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "ab") as log_file:
			log_file.write(("%s\n" % message).encode("utf8"))
