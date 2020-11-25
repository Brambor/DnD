from library.Main import library

from modules.DnDException import DnDException, DnDExit
from modules.Misc import calculate, get_library
from modules.Attack import Attack
from modules.SettingsLoader import settings
from modules.Strings import strs, separate


class Parser():
	def __init__(self, Connector):
		self.C = Connector

	def argument_wrong_ammount(self, cmd, takes, count, separators=False, last_at_least=False):
		count -= 1
		if separators:
			takes = list(t-1 for t in takes)
		else:
			takes = list(t-1 for t in ((1,) + takes))

		if last_at_least:
			takes[-1] = f"at least {takes[-1]}"
		if len(takes) == 1:
			takes_str = str(takes[0])
		else:
			takes_str = f'{", ".join((str(t) for t in takes[:-1]))} or {takes[-1]}'

		if separators:
			raise DnDException((
				f"Command '{cmd}' (with arguments!) takes {takes_str} "
				f"separator{'' if takes[-1] == 1 else 's'}, {count} given."))
		else:
			raise DnDException((
				f"Command '{cmd}' takes {takes_str} "
				f"argument{'' if takes[-1] == 1 else 's'}, {count} given."))

	def check(self, values, types):
		for v, t in zip(values.split(), types.split()):
			if t == "entity_library":
				if not (v in library["entities"]):
					raise DnDException(f"Entity '{v}' not found in library.")
			if t == "dice":
				if not v.isdigit():
					raise DnDException(f"'{v}' is not a valid integer.")

	def input_command(self):
		"Handles one line of input. Returns True if game while loop should continue. False otherwise."
		try:
			command = self.C.Input()
			self.process(command)
		except DnDExit as exception:
			print(f"Exiting due to {exception}\n")
			self.C.DatabaseManager.stopserver(silent=True)
			return False
		return True

	def print_unrecognized_command(self, parts):
		if any(separator in parts[0] for separator in settings.SEPARATORS):
			note = " Maybe you forgot a space between command and first separator?"
		else:
			note = ""
		self.C.Print(f"?!: Unrecognized command '{parts[0]}'.{note}\n")
		if settings.TEST_CRASH_ON_UNKNOWN_COMMAND and self.C.test_environment:
			raise ValueError(f"Unknown command '{parts[0]}'.")

	def process(self, cmd):
		"processes one command"
		#input
		parts = cmd.split()
		try:
			if len(parts) == 0:
				pass

			elif (len(parts) == 1) and (parts[0] not in ("#", "//", "exit", "turn", "t")):
				if parts[0] in strs["commands"]:
					self.C.Print(strs["commands"][parts[0]])
				else:
					self.print_unrecognized_command(parts)

			elif parts[0] in ("#", "//"):
				self.C.Print(f'\r# {" ".join(parts[1:])}\n')

			elif parts[0] in ("help", "h"):
				if len(parts) == 2:
					if parts[1] in strs["help"]:
						d = strs["help"][parts[1]]
						text = ""
						if type(d) == dict:
							for key in d:
								text += d[key]
						elif type(d) == str:
							text = d
						else:
							raise
						self.C.Print(text)
					else:
						raise DnDException(f"'{parts[1]}' is not helped with. These are: {', '.join(strs['help'])}.")
				elif len(parts) == 3:
					if parts[1] not in ("commands", "cmd"):
						raise DnDException("Command 'help' with 3 arguments accepts only 'commands'/'cmd' as second argument.")
					if parts[2] in strs["commands"]:
						self.C.Print(strs["commands"][parts[2]])
					else:
						raise DnDException(f"Help for command '{parts[2]}' not found. See 'help commands' for avaiable commands.")
				else:
					self.argument_wrong_ammount("help", (2, 3), len(parts))

			elif parts[0] in ("attack", "a"):
				if len(parts) == 3:
					self.argument_wrong_ammount("attack", (2, 4), len(parts), last_at_least=True)

				attacker = self.C.Game.get_entity(parts[1])[1]
				if len(parts) == 2:
					attacker.attack_list_print()
				else:
					targets = [self.C.Game.get_entity(p)[1] for p in parts[3:]]
					Attack(self.C, attacker, parts[2], targets)
					self.C.Game.history_add()

			elif parts[0] in ("create", "c"):
				self.check(parts[1], "entity_library")

				if len(parts) == 2:
					parts.append("_")

				created = False
				for nickname in parts[2:]:
					try:
						if nickname == "_":
							self.C.Game.create(parts[1])
						else:
							self.C.Game.create(parts[1], nickname)
						created = True
					except DnDException as e:
						self.C.Print(f"?!: {e}\n")
				if created:
					self.C.Game.history_add()

			elif parts[0] in ("compare", "cmp"):
				if len(parts) == 3:
					val1 = self.C.Dice.get_int_from_dice(parts[1])
					val2 = self.C.Dice.get_int_from_dice(parts[2])
					self.C.Print(f'{val1} {"<" if val1 < val2 else ">" if val1 > val2 else "="} {val2}\n')
				elif len(parts) == 7:
					e1 = self.C.Game.get_entity(parts[1])[1]
					e2 = self.C.Game.get_entity(parts[4])[1]
					if parts[3] in ("auto", "a"):
						val1 = self.C.Dice.dice_stat(e1.get_stat(parts[2], return_as_integer=True))
					else:
						val1 = self.C.Dice.get_int_from_dice(parts[3])
					if parts[6] in ("auto", "a"):
						val2 = self.C.Dice.dice_stat(e2.get_stat(parts[5], return_as_integer=True))
					else:
						val2 = self.C.Dice.get_int_from_dice(parts[6])

					self.C.Print((
						f"{e1}'s {parts[2]}: {val1} "
						f'{"<" if val1 < val2 else ">" if val1 > val2 else "="} '
						f"{e2}'s {parts[5]}: {val2}\n"
					))
				else:
					self.argument_wrong_ammount("compare", (3, 7), len(parts))

			elif parts[0] == "ctrl":
				if len(parts) != 2:
					self.argument_wrong_ammount("ctrl", (2,), len(parts))
				if parts[1] in {"s", "t", "y", "z"}:
					self.C.Curses.press_ctrl(parts[1])
				else:
					raise DnDException(f"'ctrl+{parts[1]}' is not defined.")

			elif parts[0] in ("damage", "dmg", "d"):
				parts = separate(parts[1:])

				if len(parts) != 2:
					self.argument_wrong_ammount("damage", (2,), len(parts), separators=True)

				damage_list = self.C.Dice.parse_damage(parts[0])[0]

				targets = parts[1].split()
				if len(targets) == 0:
					raise DnDException(
						f"Command 'dmg' after separator (target+) takes at least 1 argument, {len(targets)} given.")

				for target in [self.C.Game.get_entity(target)[1] for target in targets]:
					target.damaged(damage_list)
				self.C.Game.history_add()

			elif parts[0] == "django":
				if len(parts) not in (2, 3):
					self.argument_wrong_ammount("django", (2, 3), len(parts))

				if parts[1] == "start":
					self.C.DatabaseManager.runserver(len(parts) == 2)
				elif parts[1] == "download":
					if len(parts) != 2:
						raise DnDException(f"Command 'django' with 'download' takes 2 arguments, {len(parts)-1} given.")
					self.C.DatabaseManager.download()
				elif parts[1] == "stop":
					if len(parts) != 2:
						raise DnDException(f"Command 'django' with 'stop' takes 2 arguments, {len(parts)-1} given.")
					self.C.DatabaseManager.stopserver()
				else:
					raise DnDException("Second argument of command 'django' must be one of 'start', 'download', or 'stop'.")

			elif parts[0] in ("effect", "e"):
				if len(parts) < 3:
					self.argument_wrong_ammount("effect", (3,), len(parts), last_at_least=True)

				if parts[1] == "add":
					if len(parts) < 5:
						raise DnDException(
							f"Command 'effect' with 'add' takes at least 4 arguments, {len(parts)-1} given.")
					effect = get_library("effects", parts[2])
					self.check(parts[3], "dice")
					dice = int(parts[3])
					for entity in [self.C.Game.get_entity(e)[1] for e in parts[4:]]:
						entity.add_effect(effect, dice)
				elif parts[1] in ("execute", "exe"):
					for entity in [self.C.Game.get_entity(e)[1] for e in parts[2:]]:
						entity.apply_effects()
				else:
					raise DnDException(f"Command window first argument '{parts[1]}' is invalid.")
				self.C.Game.history_add()

			elif parts[0] == "erase":
				self.C.Game.erase(parts[1:])
				self.C.Game.history_add()

			elif parts[0] == "eval":
				parts = " ".join(parts[1:])
				try:
					self.C.Print("eval:\n")
					eval(parts)
				except:
					self.C.Print("eval done wrong\n")
				self.C.Game.history_add()  # sure, why not?

			elif parts[0] == "exit":
				if len(parts) != 1:
					self.argument_wrong_ammount("exit", tuple(), len(parts))
				raise DnDExit("command exit")

			elif parts[0] == "file":
				if len(parts) not in (2, 3):
					self.argument_wrong_ammount("file", (2, 3), len(parts))

				if len(parts) == 2:
					if parts[1] == "save":
						self.C.Game.save()
					elif parts[1] == "list":
						self.C.Game.list_saves()
					else:
						raise DnDException("Second argument of command 'file' with 2 arguments must be one of 'save' or 'list'.")
				else:
					if parts[1] == "save":
						self.C.Game.save(filename=parts[2])
					elif parts[1] == "load":
						self.C.Game.load(filename=parts[2])
					elif parts[1] == "delete":
						self.C.Game.delete(filename=parts[2])
					else:
						raise DnDException("Second argument of command 'file' with 3 arguments must be one of 'save', 'load' or 'delete'.")

			elif parts[0] == "heal":
				parts = separate(parts[1:])

				if len(parts) != 2:
					self.argument_wrong_ammount("heal", (2,), len(parts), separators=True)

				expression = self.C.Dice.dice_eval(parts[0])[0]
				# calculate
				healed_for = calculate(expression)

				targets = parts[1].split()
				if len(targets) == 0:
					raise DnDException(
						f"Command 'heal' after separator (target+) takes at least 1 argument, {len(targets)} given.")

				for target in [self.C.Game.get_entity(target)[1] for target in targets]:
					target.healed(healed_for)
				self.C.Game.history_add()

			elif parts[0] in ("inventory", "i"):
				separated = separate(parts)
				if len(separated) == 1:
					if len(parts) not in (2, 4, 6):
						self.argument_wrong_ammount("inventory", (2, 4, 6), len(parts))

					entity = self.C.Game.get_entity(parts[1])[1]
					self.C.Print.select_entity_inventory(entity)
					if len(parts) == 2:
						if entity.body["inventory"]:
							self.C.Print(
								"\n".join(f"{i}: {item}" for i, item in enumerate(entity.body["inventory"])) + "\n")
						else:
							self.C.Print(f"{entity}'s inventory is empty.\n")
					elif len(parts) == 4:
						if parts[2] == "add":
							entity.put_item_into_inventory(parts[3])
						elif parts[2] == "del":
							entity.remove_item_from_inventory(parts[3])
						else:
							raise DnDException((
								"On 3 arguments, command's 'inventory' second argument "
								f"should be add/del, {parts[2]} given."))
						self.C.Game.history_add()
					elif len(parts) == 6:
						item, key, value = parts[3], parts[4], parts[5]
						if value.replace("-", "", 1).isdigit():
							value = int(value)
						entity.set_inventory_item(item, key, value)
						self.C.Game.history_add()
				elif len(separated) == 2:
					parts = separated[0].split()
					if len(parts) != 3:
						raise DnDException((
							"With 1 separator, command 'inventory' "
							f"before the separator takes 2 arguments, {len(parts)-1} given."))
					if not separated[1]:
						raise DnDException((
							"With 1 separator, command 'inventory' "
							f"after separator (item+) takes at least 1 argument, {len(separated[1].split())} given."))

					entity = self.C.Game.get_entity(parts[1])[1]
					self.C.Print.select_entity_inventory(entity)
					if parts[2] == "add":
						entity.put_items_into_inventory(separated[1].split())
					elif parts[2] == "del":
						entity.remove_items_from_inventory(separated[1].split())
					else:
						raise DnDException((
							"With 1 separator and 2 arguments before the separator, "
							f"command's 'inventory' second argument should be add/del, {parts[2]} given."))
					self.C.Game.history_add()
				else:
					self.argument_wrong_ammount("inventory", (1, 2), len(separated), separators=True)

			elif parts[0] in ("library", "lib", "list", "l"):
				if len(parts) != 2:
					self.argument_wrong_ammount("library", (2,), len(parts))

				lib = {
					"ef": "effects",
					"en": "entities",
					"i": "items",
				}.get(parts[1], parts[1])
				if lib in library:
					lib = library[lib]
				else:
					raise DnDException(f"No library '{lib}'.")

				# print duplicates in 'a1/a2/a3, b1, c1/c2' form
				if type(lib) in (set, tuple):
					lib = dict(zip(sorted(lib), lib))
				unique = {}
				for orig in lib:
					is_unique = True
					for u in unique:
						if lib[orig] == lib[u]:
							unique[u].append(orig)
							is_unique = False
					if is_unique:
						unique[orig] = []

				complete_string = ""
				comma = ""
				for u in unique:
					complete_string += comma
					comma = ", "
					complete_string += u
					if unique[u]:
						complete_string += f'/{"/".join(unique[u])}'

				self.C.Print(complete_string + "\n")

			elif parts[0] in ("move", "m"):
				changes = ""
				errors = ""
				for p in parts[1:]:
					try:
						entity = self.C.Game.get_entity(p)[1]
					except DnDException as e:
						errors += str(e) + "\n"
						continue
					entity.played_this_turn = not entity.played_this_turn
					changes += f"\n\t{entity}->{'played' if entity.played_this_turn else '''didn't play'''}"

				if changes:
					self.C.Print(f"Toggled:{changes}\n{errors}")
					self.C.Game.history_add()
				elif errors:
					self.C.Print(errors)

			elif parts[0] in ("remove_effect", "remove", "r"):
				if len(parts) != 2:
					self.argument_wrong_ammount("remove_effect", (2,), len(parts))

				entity = self.C.Game.get_entity(parts[1])[1]
				if not entity.body["effects"]:
					self.C.Print(f"Entity '{entity}' has no effects.\n")
					return

				self.C.Print(
						"%s\n" % "\n".join(
							f"{i}. {entity.get_effect_string(e)}" for i, e in enumerate(entity.body["effects"])))
				effects_to_remove = self.C.Input("effects to remove").split()

				#MUHAHAHAHA
				indexes = [int(i) if i.isdigit() else DnDException(f"'{i}' is not a non-negative integer.") for i in effects_to_remove]

				if entity.remove_effects_by_index(indexes):
					self.C.Game.history_add()

			elif parts[0] == "set":
				separated = separate(parts)
				if len(separated) == 1:
					if len(parts) not in (2, 3, 4, 5):
						self.argument_wrong_ammount("set", (2, 3, 4, 5), len(parts))

					entity = self.C.Game.get_entity(parts[1])[1]
					if len(parts) == 2:
						entity.printStats()
						return

					stat = parts[2]
					if len(parts) == 3:
						entity.printStat(stat)
						return

					if len(parts) == 4:
						entity.setStat(stat, parts[3])
					elif len(parts) == 5:
						entity.setStat(stat, parts[3], parts[4])
					self.C.Game.history_add()

				elif len(separated) == 2:
					parts, stats = (s.split() for s in separated)
					if len(parts) != 2:
						raise DnDException(
							f"With 1 separator, command 'set' before separator takes 1 argument, {len(parts)-1} given.")
					if not stats:
						raise DnDException((
							"With 1 separator, command 'set' "
							f"after separator (stat+) takes at least 1 argument, {len(stats)} given."))

					entity = self.C.Game.get_entity(parts[1])[1]
					for stat in stats:
						entity.printStat(stat)
				else:
					self.argument_wrong_ammount("set", (1, 2), len(separated), separators=True)

			elif parts[0] in ("turn", "t"):
				if len(parts) != 1:
					self.argument_wrong_ammount("turn", tuple(), len(parts))
				self.C.Game.turn()
				self.C.Game.history_add()

			elif parts[0] in ("window", "w"):
				if parts[1] in ("resize", "r"):
					if len(parts) != 2:
						self.argument_wrong_ammount("window resize", (2,), len(parts))
					self.C.Curses.resized_terminal()
				elif parts[1] in ("show", "s"):
					if len(parts) != 3:
						self.argument_wrong_ammount("window show", (3,), len(parts))
					if not parts[2].isdigit():
						raise DnDException(f"Argument 'sleep_for' of command 'window show' must be integer, '{parts[2]}' given.")
					self.C.Curses.window_show(int(parts[2]))
				elif parts[1] in ("get_size", "gs"):
					if len(parts) != 3:
						self.argument_wrong_ammount("window get_size", (3,), len(parts))
					self.C.Curses.window_get_size(parts[2])
				elif parts[1] in ("get_top_left", "gtl"):
					if len(parts) != 3:
						self.argument_wrong_ammount("window get_top_left", (3,), len(parts))
					self.C.Curses.window_get_top_left(parts[2])
				elif parts[1] in ("set_size", "ss"):
					if len(parts) != 5:
						self.argument_wrong_ammount("window set_size", (5,), len(parts))
					if not (parts[3].isdigit() and parts[4].isdigit() and int(parts[3]) > 0 and int(parts[4]) > 0):
						raise DnDException(f"height & width must be positive ints, {parts[3]}, {parts[4]} given.")
					self.C.Curses.window_set_size(parts[2], int(parts[3]), int(parts[4]))
				elif parts[1] in ("set_top_left", "stl"):
					if len(parts) != 5:
						self.argument_wrong_ammount("window set_top_left", (5,), len(parts))
					if not (parts[3].isdigit() and parts[4].isdigit()):
						raise DnDException(f"y & x must be ints, {parts[3]}, {parts[4]} given.")
					self.C.Curses.window_set_top_left(parts[2], int(parts[3]), int(parts[4]))
				else:
					raise DnDException(f"Command window first argument '{parts[1]}' is invalid.")

			else:
				self.print_unrecognized_command(parts)

		except DnDException as exception:
			self.C.Print(f"?!: {exception}\n")
		except DnDExit:
			raise
		except Exception as exc:
			if settings.DEBUG:
				raise
			self.C.Print(f"EXCEPTION: {exc}\n")
			self.C.Print("fcked up\n")

		# entities window refresh
		try:
			self.C.Print.refresh_windows()
		except DnDException as exception:
			self.C.Print(f"?!: {exception}\n")
		except DnDExit:
			raise
		except Exception as exc:
			if settings.DEBUG:
				raise
			self.C.Print(f"EXCEPTION: {exc}\n")
			self.C.Print("fcked up\n")
