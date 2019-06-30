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

	def spaces_to_center(self, window_name, word):
		return " "*(max(0, self.windows[window_name].getmaxyx()[1] - len(word))//2)

	def refresh_entities(self, entities):
		self.windows["entities"].clear()
		if not entities:
			self.windows["entities"].addstr("no entities")
			self.windows["entities"].refresh()
			return

		# get groups
		groups = {"DEAD": []}
		for e in entities:
			if not e.body["alive"]:
				groups["DEAD"].append(e)
				continue
			if e.body["group"] not in groups:
				groups[e.body["group"]] = []
			groups[e.body["group"]].append(e)
		if groups["DEAD"] == []:
			del groups["DEAD"]

		CU = self.cCurses.color_usage
		for group in groups:
			spaces = self.spaces_to_center("entities", group)
			self.windows["entities"].addstr(spaces + group + "\n", self.cCurses.curses.color_pair(CU["mana"]))
			# TODO CRASH WHEN TO MANY LINES IN TOTAL
			for e in groups[group]:
				generator = e.get_stats_reduced()
				for item in generator:
					self.windows["entities"].addstr(item[0], self.cCurses.curses.color_pair(item[1]))

		self.windows["entities"].refresh()

	def refresh_inventory(self, entity):
		self.windows["inventory"].clear()
		if entity == None:
			header = "%sinventory\n" % self.spaces_to_center("inventory", "inventory")
			self.windows["inventory"].addstr(header)
			self.windows["inventory"].addstr("None entity selected! Note: select with command 'inventory entity'.\n")
		else:
			header = "%s's inventory" % entity.nickname
			header = "%s%s\n" % (self.spaces_to_center("inventory", header), header)
			self.windows["inventory"].addstr(header)
			if entity.body["inventory"]:
				for item in entity.body["inventory"]:
					self.windows["inventory"].addstr("%s: %s\n" % (
						item["derived_from"],
						{key:item[key] for key in item if key != "derived_from"},  # remove derived_from
					))
			else:
				self.windows["inventory"].addstr("empty inventory!")
		self.windows["inventory"].refresh()

	def write_to_log(self, message):
		if not os.path.exists("logs"):
			os.mkdir("logs")
		with open(("logs/%s.txt" % self.log_file).replace(":", "_"), "ab") as log_file:
			log_file.write(("%s" % message).encode("utf8"))
