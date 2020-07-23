import os

class CustomPrint():
	"log_file is path to the file where the output is saved\
	windows are the four window object used for communication (courses.window)"
	def __init__(self, path_to_DnD, windows, cCurses, log_file=""):
		self.path_to_DnD = path_to_DnD
		self.log_file = log_file.replace(":", "_") if log_file else ""
		self.windows = windows
		self.cCurses = cCurses
		#self.game from outside
		self.inventory_entity = None  # which entity is selected for inventory display

	def __call__(self, message="", info_type="fight"):
		if info_type == "fight":
			self.windows["fight"].addstr(message)  # fight window
			self.cCurses.history.append(message)
			self.windows["fight"].refresh()

		if self.log_file:
			self.write_to_log(message)

	def spaces_to_center(self, window_name, word):
		# TODO: use str.center
		return " "*(max(0, self.windows[window_name].getmaxyx()[1] - len(word))//2)

	def refresh_entity_window(self):
		if "entities" not in self.windows:
			return
		self.windows["entities"].clear()
		if not self.game.entities:
			self.windows["entities"].addstr("no entities")
			self.windows["entities"].refresh()
			return

		# get groups
		groups = {"DEAD": {}}
		for e in self.game.entities:
			if not e.body["alive"]:
				if e.body["derived_from"] not in groups["DEAD"]:
					groups["DEAD"][e.body["derived_from"]] = []
				groups["DEAD"][e.body["derived_from"]].append(e)
				continue
			if e.body["group"] not in groups:
				groups[e.body["group"]] = {}
			if e.body["derived_from"] not in groups[e.body["group"]]:
				groups[e.body["group"]][e.body["derived_from"]] = []
			groups[e.body["group"]][e.body["derived_from"]].append(e)
		if not groups["DEAD"]:
			del groups["DEAD"]

		get_color = self.cCurses.get_color_pair
		try:
			for group in groups:
				spaces = self.spaces_to_center("entities", group)
				self.windows["entities"].addstr(f"{spaces}{group}\n", get_color("mana"))
				for derived_from in groups[group]:
					self.windows["entities"].addstr(f"{derived_from} ", get_color("derived_from"))
					first = True
					for e in groups[group][derived_from]:
						if not first:
							self.windows["entities"].addstr(" " * (len(derived_from) + 1))
						first = False
						for item in e.get_stats_reduced():
							self.windows["entities"].addstr(item[0], get_color(item[1]))
		except self.cCurses.curses.error as e:
			self.windows["fight"].addstr("ERR: Window entities overflowed.")

		self.windows["entities"].refresh()
	def select_entity_inventory(self, entity):
		self.inventory_entity = entity

	def refresh_inventory_window(self):
		if "inventory" not in self.windows:
			return
		entity = self.inventory_entity
		self.windows["inventory"].clear()
		try:
			if entity == None:
				header = "%sinventory\n" % self.spaces_to_center("inventory", "inventory")
				self.windows["inventory"].addstr(header)
				self.windows["inventory"].addstr("None entity selected! Note: select with command 'inventory entity'.\n")
			else:
				header = "%s's inventory" % entity.nickname
				header = "%s%s\n" % (self.spaces_to_center("inventory", header), header)
				self.windows["inventory"].addstr(header)
				if not entity.body["inventory"]:
					self.windows["inventory"].addstr("empty inventory!")
				for item in entity.body["inventory"]:
					self.windows["inventory"].addstr(f'{item["derived_from"]}: %s\n' %
						{key:item[key] for key in item if key != "derived_from"},  # remove derived_from
					)
		except self.cCurses.curses.error as e:
			self.windows["fight"].addstr("ERR: Window inventory overflowed.")
		self.windows["inventory"].refresh()

	def refresh_history_window(self):
		if "history" not in self.windows:
			return

		history_w = self.windows["history"]
		# current command in the middle of window
		height, width = history_w.getmaxyx()
		height -= 1
		if len(self.cCurses.history_commands) <= height:
			slice_start = 0
			slice_end = len(self.cCurses.history_commands)
		else:
			slice_start = max(0, self.cCurses.history_pointer - height//2)
			slice_start = min(slice_start, len(self.cCurses.history_commands)-height)
			slice_end = slice_start + height

		history_w.clear()
		for i, line in enumerate(self.cCurses.history_commands[slice_start:slice_end]):
			i += slice_start
			history_w.addnstr("%d.%s%s" % (i, [" ", "*"][i==self.cCurses.history_pointer], line), width)
#		self.windows["history"].addstr("[%d:%d] / %d" % (slice_start, slice_end, len(self.cCurses.history_commands)))
		self.windows["history"].refresh()

	def write_to_log(self, message):
		logs_path = "%s/logs" % self.path_to_DnD
		if not os.path.exists(logs_path):
			os.mkdir(logs_path)
		with open(("%s/%s.txt" % (logs_path, self.log_file)), "ab") as log_file:
			log_file.write(("%s" % message).encode("utf8"))
