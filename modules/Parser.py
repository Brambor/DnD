from library.Main import library

from modules.DnDException import DnDException, DnDExit
from modules.Dice import D, dice_eval, dice_stat, dice_parser
from modules.Misc import calculate, get_int_from_dice, get_library, parse_damage  # imports its own Dice
from modules.SettingsLoader import settings
from modules.Strings import strs, separate

class Parser():
	def __init__(self, Connector):
		self.C = Connector

	def argument_wrong_ammount(self, cmd, takes, count, separators=False, last_at_least=False):
		count -= 1
		takes = list(t-1 for t in ((1,) + takes))
		if last_at_least:
			takes[-1] = f"at least {takes[-1]}"
		if len(takes) == 1:
			takes_str = str(takes[0])
		else:
			takes_str = "%s or %s" % (", ".join((str(t) for t in takes[:-1])), takes[-1])

		if separators:
			raise DnDException(
				"Command '%s' (with arguments!) takes %s separators, %d given." % (
					cmd, takes_str, count
				)
			)
		else:
			raise DnDException(
				"Command '%s' takes %s arguments, %d given." % (
					cmd, takes_str, count
				)
			)

	def check(self, values, types):
		for v, t in zip(values.split(), types.split()):
			if t == "entity_library":
				if not (v in library["entities"]):
					raise DnDException("Entity '%s' not found in library." % v)
			if t == "dice":
				if not v.isdigit():
					raise DnDException("'%s' is not a valid integer." % v)

	def input_command(self):
		"Handles one line of input. Returns True if game while loop should continue. False otherwise."
		try:
			command = self.C.Input(">>>")
			self.process(command)
		except DnDExit as exception:
			print("Exiting due to %s\n" % exception)  # for some reason this doesn't print
			return False
		return True

	def print_unrecognized_command(self, parts):
		self.C.Print("?: Unrecognized command '%s'.%s\n" % (
			parts[0],
			["", " Maybe you forgot a space between command and first separator?"][any(separator in parts[0] for separator in settings.SEPARATORS)],
		))
		if settings.TEST_CRASH_ON_UNKNOWN_COMMAND and self.C.Input.test_environment:
			raise ValueError("Unknown command '%s'." % parts[0])

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
				self.C.Print("\r# %s\n" % " ".join(parts[1:]))

			elif parts[0] in ("help", "h"):
				if len(parts) == 2:
					if parts[1] in strs["help"]:
						d = strs["help"][parts[1]]
						text = ""
						if type(d) == dict:
							for key in d:
								text += "%s" % (d[key])
						elif type(d) == str:
							text = d
						else:
							raise
						self.C.Print(text)
					else:
						raise DnDException("'%s' is not helped with. These are: %s." % (parts[1], ", ".join(strs["help"])))
				elif len(parts) == 3:
					if parts[1] not in ("commands", "cmd"):
						raise DnDException("Command 'help' with 3 arguments accepts only 'commands'/'cmd' as second argument.")
					if parts[2] in strs["commands"]:
						self.C.Print(strs["commands"][parts[2]])
					else:
						raise DnDException("Help for command '%s' not found. See 'help commands' for avaiable commands." % parts[2])
				else:
					self.argument_wrong_ammount("help", (2, 3), len(parts))

			elif parts[0] in ("attack", "a"):
				if len(parts) == 3:
					self.argument_wrong_ammount("attack", (2, 4), len(parts), last_at_least=True)

				attacker = self.C.Game.get_entity(parts[1])[1]
				if len(parts) == 2:
					attacker.attack_list_print()
				else:
					damage_list = attacker.attack(parts[2])

					for target in [self.C.Game.get_entity(p)[1] for p in parts[3:]]:
						target.damaged(damage_list)

			elif parts[0] in ("create", "c"):
				self.check(parts[1], "entity_library")

				if len(parts) == 2:
					parts.append("_")

				for nickname in parts[2:]:
					try:
						if nickname == "_":
							self.C.Game.create(parts[1])
						else:
							self.C.Game.create(parts[1], nickname)
					except DnDException as e:
						self.C.Print(f"?!: {e}\n")

			elif parts[0] in ("compare", "cmp"):
				if len(parts) == 3:
					val1 = get_int_from_dice(parts[1])
					val2 = get_int_from_dice(parts[2])
					self.C.Print(f'{val1} {"<" if val1 < val2 else ">" if val1 > val2 else "="} {val2}\n')
				elif len(parts) == 7:
					e1 = self.C.Game.get_entity(parts[1])[1]
					e2 = self.C.Game.get_entity(parts[4])[1]
					if parts[3] in ("auto", "a"):
						val1 = dice_stat(e1.get_stat(parts[2], return_as_integer=True))
					else:
						val1 = get_int_from_dice(parts[3])
					if parts[6] in ("auto", "a"):
						val2 = dice_stat(e2.get_stat(parts[5], return_as_integer=True))
					else:
						val2 = get_int_from_dice(parts[6])

					self.C.Print((
						f"{e1}'s {parts[2]}: {val1} "
						f'{"<" if val1 < val2 else ">" if val1 > val2 else "="} '
						f"{e2}'s {parts[5]}: {val2}\n"
					))
				else:
					self.argument_wrong_ammount("compare", (3, 7), len(parts))

			elif parts[0] in ("damage", "dmg", "d"):
				parts = separate(parts[1:])

				if len(parts) != 2:
					self.argument_wrong_ammount("damage", (2,), len(parts), separators=True)

				damage_list = parse_damage(parts[0], self.C.Game)[0]

				targets = parts[1].split()
				if len(targets) == 0:
					raise DnDException("Command 'dmg' after first separator (targets) takes at least 1 argument, %d given." % len(targets))

				for target in [self.C.Game.get_entity(target)[1] for target in targets]:
					target.damaged(damage_list)

			elif parts[0] in ("effect", "e"):
				if len(parts) != 4:
					self.argument_wrong_ammount("effect", (4,), len(parts))

				entity = self.C.Game.get_entity(parts[1])[1]
				effect = get_library("effects", parts[2])
				self.check(parts[3], "dice")
				dice = int(parts[3])
				entity.add_effect(effect, dice)

			elif parts[0] == "erase":
				if len(parts) == 2:
					self.C.Game.erase(parts[1])
				else:
					self.argument_wrong_ammount("erase", (2,), len(parts))

			elif parts[0] == "eval":
				parts = " ".join(parts[1:])
				try:
					self.C.Print("eval:\n")
					eval(parts)
				except:
					self.C.Print("eval done wrong\n")

			elif parts[0] == "exit":
				if len(parts) == 1:
					raise DnDExit("command exit")
				else:
					self.argument_wrong_ammount("exit", tuple(), len(parts))

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
						self.C.Game.save(file_name=parts[2])
					elif parts[1] == "load":
						self.C.Game.load(file_name=parts[2])
					elif parts[1] == "delete":
						self.C.Game.delete(file_name=parts[2])
					else:
						raise DnDException("Second argument of command 'file' with 3 arguments must be one of 'save', 'load' or 'delete'.")

			elif parts[0] == "heal":
				parts = separate(parts[1:])

				if len(parts) != 2:
					self.argument_wrong_ammount("heal", (2,), len(parts), separators=True)

				expression = dice_eval(parts[0], self.C.Game)[0]
				# calculate
				healed_for = calculate(expression)

				targets = parts[1].split()
				if len(targets) == 0:
					raise DnDException("Command 'heal' after first separator (targets) takes at least 1 argument, %d given." % len(targets))

				for target in [self.C.Game.get_entity(target)[1] for target in targets]:
					target.healed(healed_for)

			elif parts[0] in ("inventory", "i"):
				if len(parts) not in (2, 4, 6):
					self.argument_wrong_ammount("inventory", (2, 4, 6), len(parts))

				entity = self.C.Game.get_entity(parts[1])[1]
				self.C.Print.select_entity_inventory(entity)
				if len(parts) == 2:
					if entity.body["inventory"]:
						self.C.Print("\n".join(f"{i}: {item}" for i, item in enumerate(entity.body["inventory"])) + "\n")
					else:
						self.C.Print(f"{entity}'s inventory is empty.\n")
				elif len(parts) == 4:
					if parts[2] == "add":
						entity.put_item_into_inventory(get_library("items", parts[3]))
					elif parts[2] == "del":
						entity.remove_item_from_inventory(parts[3])
					else:
						raise DnDException(f"On 4 arguments, command's 'inventory' third argument should be add/del, {parts[2]} given.")
				elif len(parts) == 6:
					item, key, value = parts[3], parts[4], parts[5]
					if value.replace("-", "", 1).isdigit():
						value = int(value)
					entity.set_inventory_item(item, key, value)

			elif parts[0] in ("library", "lib", "list", "l"):
				if len(parts) != 2:
					self.argument_wrong_ammount("library", (2,), len(parts))

				lib = {
					"ef": "effects",
					"en": "entities",
					"i": "items",
					"s": "spells",
					"sp": "spells",
				}.get(parts[1], parts[1])
				if lib in library:
					lib = library[lib]
				else:
					raise DnDException("No library '%s'." % lib)

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
						complete_string += "/%s" % "/".join(unique[u])

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
				elif errors:
					self.C.Print(errors)

			elif parts[0] in ("remove_effect", "remove", "r"):
				if len(parts) != 2:
					self.argument_wrong_ammount("remove_effect", (2,), len(parts))

				entity = self.C.Game.get_entity(parts[1])[1]
				if not entity.body["effects"]:
					self.C.Print(f"Entity '{entity}' has no effects.")
					return

				self.C.Print(
						"%s\n" % "\n".join(f"{i}. {entity.get_effect_string(e)}" for i, e in enumerate(entity.body["effects"]))
					)
				effects_to_remove = self.C.Input("effects to remove >>>").split()

				#MUHAHAHAHA
				indexes = [int(i) if i.isdigit() else DnDException(f"'{i}' is not a non-negative integer.") for i in effects_to_remove]

				entity.remove_effects_by_index(indexes)

			elif parts[0] == "set":
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

				value = parts[3]

				if len(parts) == 4:
					entity.setStat(stat, value)
				elif len(parts) == 5:
					entity.setStat(stat, value, parts[4])

			elif parts[0] in ("spell", "s", "cast"):
				if len(parts) not in (3, 4):
					self.argument_wrong_ammount("spell", (3, 4), len(parts))
				do_input = len(parts) == 4

				caster = self.C.Game.get_entity(parts[1])[1]
				spell = get_library("spells", parts[2])

				# targets
				targets = self.C.Input("targets:\n>>>")
				targets = [self.C.Game.get_entity(target)[1] for target in targets.split()]

				caster.cast_spell(targets, spell, do_input)

			elif parts[0] in ("turn", "t"):
				if len(parts) == 1:
					self.C.Game.turn()
				else:
					self.argument_wrong_ammount("turn", tuple(), len(parts))

			elif parts[0] in ("window", "w"):
				if len(parts) >= 2:
					if parts[1] in ("show", "s"):
						if len(parts) == 3:
							if parts[2].isdigit():
								self.C.Curses.window_show(int(parts[2]))
							else:
								raise DnDException("Argument 'sleep_for' of command 'window show' must be integer, '%s' given." % parts[2])
						else:
							self.argument_wrong_ammount("window show", (3,), len(parts))
					elif parts[1] in ("get_size", "gs"):
						if len(parts) == 3:
								self.C.Curses.window_get_size(parts[2])
						else:
							self.argument_wrong_ammount("window get_size", (3,), len(parts))
					elif parts[1] in ("get_top_left", "gtl"):
						if len(parts) == 3:
								self.C.Curses.window_get_top_left(parts[2])
						else:
							self.argument_wrong_ammount("window get_top_left", (3,), len(parts))
					elif parts[1] in ("set_size", "ss"):
						if len(parts) == 5:
							if (parts[3].isdigit() and parts[4].isdigit()):
								self.C.Curses.window_set_size(parts[2], int(parts[3]), int(parts[4]))
							else:
								raise DnDException("ncols & nlines must be ints, %s, %s given." % (parts[3], parts[4]))
						else:
							self.argument_wrong_ammount("window set_size", (5,), len(parts))
					elif parts[1] in ("set_top_left", "stl"):
						if len(parts) == 5:
							if (parts[3].isdigit() and parts[4].isdigit()):
								self.C.Curses.window_set_top_left(parts[2], int(parts[3]), int(parts[4]))
							else:
								raise DnDException("y & x must be ints, %s, %s given." % (parts[3], parts[4]))
						else:
							self.argument_wrong_ammount("window set_top_left", (5,), len(parts))

			else:
				self.print_unrecognized_command(parts)

		except DnDException as exception:
			self.C.Print("?!: %s\n" % exception)
		except DnDExit:
			raise
		except Exception as exc:
			if settings.DEBUG:
				raise
			self.C.Print("EXCEPTION: %s\n" % exc)
			self.C.Print("fcked up\n")

		# entities window refresh
		try:
			self.C.Print.refresh_windows()
		except DnDException as exception:
			self.C.Print("?!: %s\n" % exception)
		except DnDExit:
			raise
		except Exception as exc:
			if settings.DEBUG:
				raise
			self.C.Print("EXCEPTION: %s\n" % exc)
			self.C.Print("fcked up\n")
