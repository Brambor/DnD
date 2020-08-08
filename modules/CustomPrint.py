import os

class CustomPrint():
	def __init__(self, Connector):
		self.C = Connector
		self.inventory_entity = None  # which entity is selected for inventory display

	def __call__(self, message="", info_type="fight"):
		if info_type == "fight":
			self.C.Curses.windows["fight"].addstr(message)  # fight window
			self.C.Curses.fight_history.append(message)
			self.C.Curses.windows["fight"].refresh()

		if self.C.log_file:
			self.write_to_log(message)

	def spaces_to_center(self, window_name, word):
		# TODO: use str.center
		return " "*(max(0, self.C.Curses.windows[window_name].getmaxyx()[1] - len(word))//2)

	def refresh_entity_window(self):
		if "entities" not in self.C.Curses.windows:
			return
		self.C.Curses.windows["entities"].clear()
		if not self.C.Game.entities:
			self.C.Curses.windows["entities"].addstr("no entities")
			self.C.Curses.windows["entities"].refresh()
			return

		# get groups
		groups = {"DEAD": {}}
		for e in self.C.Game.entities:
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

		get_color = self.C.Curses.get_color_pair
		try:
			for group in groups:
				group_count = f'{group} (%d)' % sum(len(groups[group][derived_from]) for derived_from in groups[group])
				spaces = self.spaces_to_center("entities", group_count)
				self.C.Curses.windows["entities"].addstr(f"{spaces}{group_count}\n", get_color("mana"))
				for derived_from in groups[group]:
					self.C.Curses.windows["entities"].addstr(f"{derived_from} ", get_color("derived_from"))
					first = True
					for e in groups[group][derived_from]:
						if not first:
							self.C.Curses.windows["entities"].addstr(" " * (len(derived_from) + 1))
						first = False
						for item in e.get_stats_reduced():
							self.C.Curses.windows["entities"].addstr(item[0], get_color(item[1]))
		except self.C.Curses.curses.error as e:
			self("ERR: Window entities overflowed.\n")

		self.C.Curses.windows["entities"].refresh()

	def select_entity_inventory(self, entity):
		self.inventory_entity = entity

	def deselect_entity_inventory(self, entity):
		# if given entity's inventory is selected, deselect it
		# otherwise do nothing
		if self.inventory_entity == entity:
			self.inventory_entity = None

	def refresh_inventory_window(self):
		if "inventory" not in self.C.Curses.windows:
			return
		entity = self.inventory_entity
		self.C.Curses.windows["inventory"].clear()
		try:
			if entity == None:
				header = "%sinventory\n" % self.spaces_to_center("inventory", "inventory")
				self.C.Curses.windows["inventory"].addstr(header)
				self.C.Curses.windows["inventory"].addstr(
					"None entity selected! Note: select with command 'inventory entity'.\n")
			else:
				header = "%s's inventory" % entity.nickname
				header = "%s%s\n" % (self.spaces_to_center("inventory", header), header)
				self.C.Curses.windows["inventory"].addstr(header)
				if not entity.body["inventory"]:
					self.C.Curses.windows["inventory"].addstr("empty inventory!")
				for item in entity.body["inventory"]:
					self.C.Curses.windows["inventory"].addstr(f'{item["derived_from"]}: %s\n' %
						{key:item[key] for key in item if key != "derived_from"},  # remove derived_from
					)
		except self.C.Curses.curses.error as e:
			self("ERR: Window inventory overflowed.\n")
		self.C.Curses.windows["inventory"].refresh()

	def refresh_history_window(self):
		if "history" not in self.C.Curses.windows:
			return

		history_w = self.C.Curses.windows["history"]
		# current command in the middle of window
		height, width = history_w.getmaxyx()
		height -= 1
		if len(self.C.Curses.cmd_history) <= height:
			slice_start = 0
			slice_end = len(self.C.Curses.cmd_history)
		else:
			slice_start = max(0, self.C.Curses.cmd_history_pointer - height//2)
			slice_start = min(slice_start, len(self.C.Curses.cmd_history)-height)
			slice_end = slice_start + height

		history_w.clear()
		for i, line in enumerate(self.C.Curses.cmd_history[slice_start:slice_end]):
			i += slice_start
			mark = "*" if i==self.C.Curses.cmd_history_pointer and not self.C.Curses.cmd_history_pointer_at_end else " "
			history_w.addnstr(f'{i}.{mark}{line}', width)
		self.C.Curses.windows["history"].refresh()

	def write_to_log(self, message):
		logs_path = "%s/logs" % self.C.path_to_DnD
		if not os.path.exists(logs_path):
			os.mkdir(logs_path)
		with open(("%s/%s.txt" % (logs_path, self.C.log_file)), "ab") as log_file:
			log_file.write(("%s" % message).encode("utf8"))
