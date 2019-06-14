import os

class CustomPrint():
	"log_file is path to the file where the output is saved\
	windows are the four window object used for communication (courses.window)"
	def __init__(self, windows, cCurses, log_file=""):
		self.log_file = log_file
		self.windows = windows
		self.cCurses = cCurses

	def __call__(self, message="", info_type="fight"):
		if info_type == "fight":
			self.windows["fight"].addstr(message)  # fight window
			self.windows["fight"].refresh()

		if self.log_file:
			self.write_to_log(message)

	def refresh_entities(self, entities):
		self.windows["entities"].clear()
		if not entities:
			self.windows["entities"].addstr("no entities")
			self.windows["entities"].refresh()
			return

		# get groups
		groups = {}
		for e in entities:
			if e.body["group"] not in groups:
				groups[e.body["group"]] = []
			groups[e.body["group"]].append(e)

		CU = self.cCurses.color_usage
		for group in groups:
			spaces = " "*((self.windows["entities"].getmaxyx()[0] - len(group))//2)
			self.windows["entities"].addstr(spaces + group + "\n", self.cCurses.curses.color_pair(CU["mana"]))
			# TODO CRASH WHEN TO MANY LINES IN TOTAL
			for e in groups[group]:
				generator = e.get_stats_reduced()
				for item in generator:
					self.windows["entities"].addstr(item[0], self.cCurses.curses.color_pair(item[1]))

		self.windows["entities"].refresh()

	def write_to_log(self, message):
		if not os.path.exists("logs"):
			os.mkdir("logs")
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "ab") as log_file:
			log_file.write(("%s" % message).encode("utf8"))
