from library.Main import library

from modules.DnDException import DnDException, DnDExit
from modules.Dice import D, dice_stat, dice_parser
from modules.Misc import get_int_from_dice  # imports its own Dice
from modules.SettingsLoader import settings
from modules.Strings import strs, separate

class Parser():
	def __init__(self, game, cInput, cPrint, DEBUG):
		self.game = game
		self.DEBUG = DEBUG
		self.cInput = cInput
		self.cPrint = cPrint

	def argument_wrong_ammount(self, cmd, takes, count, separators=False):
		count -= 1
		takes = tuple(t-1 for t in ((1,) + takes))
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
				if not (v in self.game.library["entities"]):
					raise DnDException("Entity '%s' not found in library." % v)
			if t == "dice":
				if not v.isdigit():
					raise DnDException("'%s' is not a valid integer." % v)

	def input_command(self):
		"Handles one line of input. Returns True if game while loop should continue. False otherwise."
		try:
			command = self.cInput(">>>")
			self.process(command)
		except DnDExit as exception:
			print("Exiting due to %s\n" % exception)  # for some reason this doesn't print
			return False
		return True

	def print_unrecognized_command(self, parts):
		self.cPrint("?: Unrecognized command '%s'.%s\n" % (
			parts[0],
			["", " Maybe you forgot a space between command and first separator?"][any(separator in parts[0] for separator in settings.SEPARATORS)],
		))
		if settings.TEST_CRASH_ON_UNKNOWN_COMMAND and self.cInput.test_environment:
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
					self.cPrint(strs["commands"][parts[0]])
				else:
					self.print_unrecognized_command(parts)

			elif parts[0] in ("#", "//"):
				self.cPrint("\r# %s\n" % " ".join(parts[1:]))

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
						self.cPrint(text)
					else:
						raise DnDException("'%s' is not helped with. These are: %s." % (parts[1], ", ".join(strs["help"])))
				elif len(parts) == 3:
					if parts[1] not in ("commands", "cmd"):
						raise DnDException("Command 'help' with 3 arguments accepts only 'commands'/'cmd' as second argument.")
					if parts[2] in strs["commands"]:
						self.cPrint(strs["commands"][parts[2]])
					else:
						raise DnDException("Help for command '%s' not found. See 'help commands' for avaiable commands." % parts[2])
				else:
					self.argument_wrong_ammount("help", (2, 3), len(parts))

			elif parts[0] in ("create", "c"):
				self.check(parts[1], "entity_library")

				if len(parts) == 2:
					parts.append("_")

				for nickname in parts[2:]:
					try:
						if nickname == "_":
							self.game.create(parts[1])
						else:
							self.game.create(parts[1], nickname)
					except DnDException as e:
						self.cPrint("?!: %s\n" % str(e))

			elif parts[0] in ("compare", "cmp"):
				if len(parts) == 3:
					val1 = get_int_from_dice(parts[1])
					val2 = get_int_from_dice(parts[2])
					self.cPrint("%d %s %d\n" % (val1, ("<" if val1 < val2 else ">" if val1 > val2 else "="), val2))
				elif len(parts) == 7:
					e1 = self.game.get_entity(parts[1])[1]
					e2 = self.game.get_entity(parts[4])[1]
					if parts[3] in ("auto", "a"):
						val1 = dice_stat(e1.get_stat(parts[2], return_as_integer=True))
					else:
						val1 = get_int_from_dice(parts[3])
					if parts[6] in ("auto", "a"):
						val2 = dice_stat(e2.get_stat(parts[5], return_as_integer=True))
					else:
						val2 = get_int_from_dice(parts[6])


					self.cPrint("%s's %s: %d %s %s's %s: %d\n" % (
						e1, parts[2], val1,
						("<" if val1 < val2 else ">" if val1 > val2 else "="),
						e2, parts[5], val2,
						))
				else:
					self.argument_wrong_ammount("compare", (3, 7), len(parts))

			elif parts[0] in ("damage", "dmg", "d"):
				parts = separate(parts[1:])

				if len(parts) != 3:
					self.argument_wrong_ammount("damage", (2,), len(parts), separators=True)

				source_text = parts[0]  # TODO wrong, also, use it somewhere...

				damage_list = []
				for whole in (type_damage.split("{") for type_damage in parts[1].split("}") if type_damage != ""):
					if len(whole) != 2:
						raise DnDException("%s is %d long, 2 expected.\nMaybe you forgot '{' ?" % (whole, len(whole)))

					types = set()
					for damage_type in whole[0].strip().split():
						if damage_type not in library["damage_types"]:
							raise DnDException("Invalid damage_type '%s'." % damage_type)
						types.add(damage_type)

					dice = dice_parser(whole[1])

					if dice:
						threw_crit = self.game.throw_dice(dice)
						# put the results back into the expression
						for n, threw in zip(dice, threw_crit):
							whole[1] = whole[1].replace("d%d" % n, str(threw[0]), 1)

					# eval
					damage_list.append((types, eval(whole[1])))

				targets = parts[2].split()
				if len(targets) == 0:
					raise DnDException("Command 'dmg' after second separator (targets) takes at least 1 arguments, %d given." % len(targets))

				for target in [self.game.get_entity(target)[1] for target in targets]:
					target.damaged(damage_list)

			elif parts[0] in ("effect", "e"):
				if len(parts) != 4:
					self.argument_wrong_ammount("effect", (4,), len(parts))

				entity = self.game.get_entity(parts[1])[1]
				effect = self.game.get("effects", parts[2])
				self.check(parts[3], "dice")
				dice = int(parts[3])
				entity.add_effect(effect, dice)

			elif parts[0] == "erase":
				if len(parts) == 2:
					self.game.erase(parts[1])
				else:
					self.argument_wrong_ammount("erase", (2,), len(parts))

			elif parts[0] == "eval":
				parts = " ".join(parts[1:])
				try:
					self.cPrint("eval:\n")
					eval(parts)
				except:
					self.cPrint("eval done wrong\n")

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
						self.game.save()
					elif parts[1] == "list":
						self.game.list_saves()
					else:
						raise DnDException("Second argument of command 'file' with 2 arguments must be one of 'save' or 'list'.")
				else:
					if parts[1] == "save":
						self.game.save(file_name=parts[2])
					elif parts[1] == "load":
						self.game.load(file_name=parts[2])
					elif parts[1] == "delete":
						self.game.delete(file_name=parts[2])
					else:
						raise DnDException("Second argument of command 'file' with 3 arguments must be one of 'save', 'load' or 'delete'.")

			elif parts[0] in ("inventory", "i"):
				if len(parts) not in (2, 4, 6):
					self.argument_wrong_ammount("inventory", (2, 4, 6), len(parts))

				entity = self.game.get_entity(parts[1])[1]
				self.cPrint.select_entity_inventory(entity)
				if len(parts) == 2:
					if entity.body["inventory"]:
						self.cPrint("\n".join("%d: %s" % (i, str(item)) for i, item in enumerate(entity.body["inventory"])) + "\n")
					else:
						self.cPrint("%s's inventory is empty.\n" % entity)
				elif len(parts) == 4:
					if parts[2] == "add":
						item = self.game.get("items", parts[3])
						entity.put_item_into_inventory(item)
					elif parts[2] == "del":
						entity.remove_item_from_inventory(parts[3])
					else:
						raise DnDException("On 4 arguments, command's 'inventory' third argument should be add/del, %s given." % parts[2])
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
				if lib in self.game.library:
					lib = self.game.library[lib]
				else:
					raise DnDException("No library '%s'." % lib)

				# print duplicates in 'a1/a2/a3, b1, c1/c2' form
				if type(lib) == set:
					lib = dict(zip(sorted(lib), (i for i in lib)))
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

				self.cPrint(complete_string + "\n")

			elif parts[0] in ("move", "m"):
				changes = ""
				errors = ""
				for p in parts[1:]:
					try:
						entity = self.game.get_entity(p)[1]
						entity.played_this_turn = not entity.played_this_turn
						changes += ("\n\t%s->%s" % (entity, "played" if entity.played_this_turn else "didn't play"))
					except DnDException as e:
						errors += str(e) + "\n"

				if changes == "":
					self.cPrint(errors)
				else:
					self.cPrint("Toggled:%s\n%s" % (changes, errors))

			elif parts[0] in ("remove_effect", "remove", "r"):
				if len(parts) != 2:
					self.argument_wrong_ammount("remove_effect", (2,), len(parts))

				entity = self.game.get_entity(parts[1])[1]
				if not entity.body["effects"]:
					self.cPrint("Entity '%s' has no effects." % entity)
					return

				self.cPrint(
						"%s\n" % "\n".join("%d. %s" % (i, entity.get_effect_string(e)) for i, e in enumerate(entity.body["effects"]))
					)
				effects_to_remove = self.cInput("effects to remove:\n>>>").split()

				#MUHAHAHAHA
				indexes = [int(i) if i.isdigit() else DnDException("'%s' is not a non-negative integer." % i) for i in effects_to_remove]

				entity.remove_effects_by_index(indexes)

			elif parts[0] == "set":
				if len(parts) not in (2, 3, 4, 5):
					self.argument_wrong_ammount("set", (2, 3, 4, 5), len(parts))

				entity = self.game.get_entity(parts[1])[1]
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
				if len(parts) == 3:
					theInput = False
				elif len(parts) == 4:
					theInput = self.cInput
				else:
					self.argument_wrong_ammount("spell", (3, 4), len(parts))

				caster = self.game.get_entity(parts[1])[1]
				spell = self.game.get("spells", parts[2])

				# targets
				targets = self.cInput("targets:\n>>>")
				targets = [self.game.get_entity(target)[1] for target in targets.split()]

				caster.cast_spell(targets, spell, theInput)

			elif parts[0] in ("turn", "t"):
				if len(parts) == 1:
					self.game.turn()
				else:
					self.argument_wrong_ammount("turn", tuple(), len(parts))

			elif parts[0] in ("window", "w"):
				if len(parts) >= 2:
					if parts[1] in ("show", "s"):
						if len(parts) == 3:
							if parts[2].isdigit():
								self.cPrint.cCurses.window_show(int(parts[2]))
							else:
								raise DnDException("Argument 'sleep_for' of command 'window show' must be integer, '%s' given." % parts[2])
						else:
							self.argument_wrong_ammount("window show", (3,), len(parts))
					elif parts[1] in ("get_size", "gs"):
						if len(parts) == 3:
								self.cPrint.cCurses.window_get_size(parts[2])
						else:
							self.argument_wrong_ammount("window get_size", (3,), len(parts))
					elif parts[1] in ("get_top_left", "gtl"):
						if len(parts) == 3:
								self.cPrint.cCurses.window_get_top_left(parts[2])
						else:
							self.argument_wrong_ammount("window get_top_left", (3,), len(parts))
					elif parts[1] in ("set_size", "ss"):
						if len(parts) == 5:
							if (parts[3].isdigit() and parts[4].isdigit()):
								self.cPrint.cCurses.window_set_size(parts[2], int(parts[3]), int(parts[4]))
							else:
								raise DnDException("ncols & nlines must be ints, %s, %s given." % (parts[3], parts[4]))
						else:
							self.argument_wrong_ammount("window set_size", (5,), len(parts))
					elif parts[1] in ("set_top_left", "stl"):
						if len(parts) == 5:
							if (parts[3].isdigit() and parts[4].isdigit()):
								self.cPrint.cCurses.window_set_top_left(parts[2], int(parts[3]), int(parts[4]))
							else:
								raise DnDException("y & x must be ints, %s, %s given." % (parts[3], parts[4]))
						else:
							self.argument_wrong_ammount("window set_top_left", (5,), len(parts))

			else:
				self.print_unrecognized_command(parts)

		except DnDException as exception:
			self.cPrint("?!: %s\n" % exception)
		except DnDExit:
			raise
		except Exception as exc:
			if self.DEBUG:
				raise
			self.cPrint("EXCEPTION: %s\n" % exc)
			self.cPrint("fcked up\n")

		# entities window refresh
		try:
			self.cPrint.refresh_entity_window()
			self.cPrint.refresh_inventory_window()
			self.cPrint.refresh_history_window()
		except DnDException as exception:
			self.cPrint("?!: %s\n" % exception)
		except DnDExit:
			raise
		except Exception as exc:
			if self.DEBUG:
				raise
			self.cPrint("EXCEPTION: %s\n" % exc)
			self.cPrint("fcked up\n")
