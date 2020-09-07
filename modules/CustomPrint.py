import os

from modules.SettingsLoader import settings


class CustomPrint():
	def __init__(self, Connector):
		self.C = Connector
		self.inventory_entity_id = -1  # which entity is selected for inventory display

	def __call__(self, message="", info_type="fight"):
		message = message.expandtabs(settings.TAB_WIDTH)
		if info_type == "fight":
			self.C.Curses.addstr("fight", message)  # fight window
			self.C.Curses.fight_history.append(message)
			self.C.Curses.windows["fight"].refresh()

		self.write_to_log(message)

	def spaces_to_center(self, window_name, word):
		# TODO: use str.center
		return " "*(max(0, self.C.Curses.windows[window_name].getmaxyx()[1] - len(word))//2)

	def refresh_windows(self):
		self.refresh_entity_window()
		self.refresh_history_window()

	def refresh_entity_window(self):
		if "entities" not in self.C.Curses.windows:
			return
		self.C.Curses.windows["entities"].clear()
		get_color = self.C.Curses.get_color_pair
		self.C.Curses.addstr("entities",
			f'History {self.C.Game.entities_history_pointer}/{len(self.C.Game.entities_history)-1} Dice ',
			restart=True)

		state, color = (
			"M", get_color("indicator_running")) if self.C.Game.manual_dice else ("A", get_color("indicator_stopped"))
		self.C.Curses.addstr("entities", state, color)

		self.C.Curses.addstr("entities", f' Django ')
		state, color = (
			"running", get_color("indicator_running")
			) if self.C.DatabaseManager.server_is_running else ("stopped", get_color("indicator_stopped"))
		self.C.Curses.addstr("entities", f"{state}\n", color)

		if not self.C.Game.entities:
			self.C.Curses.addstr("entities", "no entities")
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

		entity = self.C.Game.get_entity_by_id(self.inventory_entity_id)
		# entities list
		for group in groups:
			group_count = f'{group} ({sum(len(groups[group][derived_from]) for derived_from in groups[group])})'
			spaces = self.spaces_to_center("entities", group_count)
			self.C.Curses.addstr("entities", f"{spaces}{group_count}\n", get_color("mana"))
			for derived_from in groups[group]:
				self.C.Curses.addstr("entities", f"{derived_from} ", get_color("derived_from"))
				first = True
				for e in groups[group][derived_from]:
					if not first:
						self.C.Curses.addstr("entities", " " * (len(derived_from) + 1))
					first = False
					for item in e.get_stats_reduced():
						self.C.Curses.addstr("entities", item[0], get_color(item[1]))
		# inventory
		if entity == None:
			header = f'{self.spaces_to_center("entities", "inventory")}inventory\n'
			self.C.Curses.addstr("entities", header)
			text = f"Entity with id={self.inventory_entity_id} doesn't exist." if self.inventory_entity_id != -1 else "None entity selected!"
			self.C.Curses.addstr("entities", 
				f"{text} Note: select with command 'inventory entity'.\n")
		else:
			header = f"{entity.nickname}'s inventory"
			header = f'{self.spaces_to_center("entities", header)}{header}\n'
			self.C.Curses.addstr("entities", header)
			if not entity.body["inventory"]:
				self.C.Curses.addstr("entities", "empty inventory!")
			for item in entity.body["inventory"]:
				self.C.Curses.addstr("entities", 
					f'{item["derived_from"]}: { {key:item[key] for key in item if key != "derived_from"}}\n')

		self.C.Curses.windows["entities"].refresh()

	def select_entity_inventory(self, entity):
		self.inventory_entity_id = entity.id

	def deselect_entity_inventory(self, entity):
		# if given entity's inventory is selected, deselect it
		# otherwise do nothing
		if self.inventory_entity_id == entity.id:
			self.inventory_entity_id = -1

	def refresh_history_window(self):
		if "history" not in self.C.Curses.windows:
			return

		history_w = self.C.Curses.windows["history"]
		# current command in the middle of window
		height, width = history_w.getmaxyx()
		if len(self.C.Curses.cmd_history) <= height:
			slice_start = 0
			slice_end = len(self.C.Curses.cmd_history)
		else:
			slice_start = max(0, self.C.Curses.cmd_history_pointer - height//2)
			slice_start = min(slice_start, len(self.C.Curses.cmd_history)-height)
			slice_end = slice_start + height

		history_w.clear()
		for i, line in enumerate(self.C.Curses.cmd_history[slice_start:slice_end]):
			history_w.move(i, 0)
			i += slice_start
			mark = "*" if i==self.C.Curses.cmd_history_pointer and not self.C.Curses.cmd_history_pointer_at_end else " "
			history_w.insstr(f'{i}.{mark}{line}\n')
		self.C.Curses.windows["history"].refresh()

	def write_to_log(self, message):
		if not self.C.log_file:
			return
		logs_path = f"{self.C.path_to_DnD}/logs"
		if not os.path.exists(logs_path):
			os.mkdir(logs_path)
		with open(f"{logs_path}/{self.C.log_file}.txt", "ab") as log_file:
			log_file.write(message.encode("utf8"))
