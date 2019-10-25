import re

from modules.DnDException import DnDException

try:
	from settings import local_settings as settings
except ImportError:
	print("Did you forget to copy 'settings/local_settings_default.py' to a file named 'settings/local_settings.py'?")
	input()
	raise

texts = {
	"placeholder_input_sequence": "placeholder_input_sequence activates inputing sequence latter down the chain; for now any value just means True",
	"help": {},
}

cmd = (
	("help", "h"),
	("create", "c"),
	("dmg", "d", "attack", "a"),
	("effect", "e"),
	("erase",),
	("eval",),
	("fight", "f"),
	("inventory", "i"),
	("library", "lib", "list", "l"),
	("move", "m"),
	("remove", "r"),
	("set",),
	("spell", "s", "cast"),
	("turn", "t"),
	("window", "w"),
)
texts["help"]["commands"] = (
	"COMMANDS:\n"
		"\twrite command without any more arguments for further help,\n"
		"\t(except for turn)\n"
)

for c in (", ".join(c) for c in cmd):
	texts["help"]["commands"] += "\t%s\n" % c

texts["help"]["entity_reference"] = ("'entity' can be referenced via entity nickname or entity id.\n"
					"e.g. for entity 'a_0' either 'a' (entity nickname) or '0' (entity id) works.\n"
					"Then commands 'move a' & 'move 0' are equivalent.\n"
)

texts["help"]["symbol"] = {
	"+": "Symbol '+' means at least one, as many as you want.\n",
	"*": "Symbol '*' means optional (at least zero), as many as you want.\n",
	"|": "Symbol '|' is separator, required when there are more arguments with '+' or '*'."
	" Separators are %s set in 'settings.SEPARATORS.'\n" % ", ".join("'%s'" % s for s in settings.SEPARATORS),
}

texts["help_general"] = (
	"General help: use 'help WHAT' for more detailed help.\n"
	"\tWHAT can be: %s\n" % ", ".join(texts["help"])
	+"If something doesn't work or you don't understand somethin TELL ME IMIDIATELY please!\n"
	"It means that something is wrongly implemented or documented!\n"
)

def separate(splitted_parts):
	splitted_parts = [part.strip() for part in re.split("|".join("\\%s" % s for s in settings.SEPARATORS), " ".join(splitted_parts))]
	return splitted_parts

class Parser():
	def __init__(self, game, cInput, cPrint, DEBUG):
		self.game = game
		self.DEBUG = DEBUG
		self.cInput = cInput
		self.cPrint = cPrint
		self.inventory_of_entity = None

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
		command = self.cInput(">>>")
		if command == "exit":
			return False # force break
		self.process(command)
		return True

	def process(self, cmd):
		parts = cmd.split()
		try:
			if len(parts) == 0:
				pass
			elif parts[0] in ("#", "//"):
				self.cPrint("\r# %s\n" % " ".join(parts[1:]))

			elif parts[0] in ("help", "h"):
				if len(parts) == 1:
					self.cPrint(texts["help_general"])
				elif len(parts) == 2:
					if parts[1] in texts["help"]:
						d = texts["help"][parts[1]]
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
						raise DnDException("'%s' is not helped with. These are: %s." % (parts[1], ", ".join(texts["help"])))

			elif parts[0] in ("create", "c"):
				if len(parts) == 1:
					self.cPrint("[c]reate entity_library nickname_to_be_set\n"
								"\t'entity_library' can be listed via command 'library entities' 'l en' for short.\n")
					return
				self.check(parts[1], "entity_library")

				if len(parts) > 2:
					e = self.game.create(parts[1], parts[2])
				else:
					e = self.game.create(parts[1])

			elif parts[0] in ("dmg", "d", "attack", "a"):
				if len(parts) == 1:
					self.cPrint("[d]mg/[a]ttack source_text | type_of_dmg base_dmg dice(die)+ | target(s)+\n"
							"\tsource_text is string latter used in log message (it is NOT optional, thought it is vaguely saved)\n"
							"\tdamage_type ([p]hysical/[m]agic/[t]rue)\n"
							"\tdie are row integers representing used dice(die)\n"
							"\ttarget_entity_1 target_entity_2 ...\n"
							"\t"+texts["help"]["symbol"]["+"]
							+"\t"+texts["help"]["symbol"]["|"]
							)
					return
				parts = separate(parts[1:])
				source_text = parts[1:]

				damages = parts[1].split()

				damage_type = damages[0]
				if damage_type not in ("physical", "p", "magic", "m", "true", "t"):
					raise DnDException("Damage type must be one of [p]hysical/[m]agic/[t]rue, '%s' is not either of them." % damage_type)

				base_dmg = damages[1]
				self.check(base_dmg, "dice")
				base_dmg = int(base_dmg)

				dice = damages[2:]
				self.check(" ".join(dice), " ".join(["dice"]*len(dice)))  # cubersome...
				dice = [int(d) for d in dice]

				targets = parts[2].split()
				targets = [self.game.get_entity(target)[1] for target in targets]

				threw_crit = self.game.throw_dice(dice)
				damage_sum = base_dmg + sum(t[0] for t in threw_crit)
				for target in targets:
					target.damaged(damage_sum, damage_type)

			elif parts[0] in ("effect", "e"):
				if len(parts) == 1:
					self.cPrint("[e]ffect entity effect dice\n")
					return
				if len(parts) != 4:
					raise DnDException("Command 'effect' takes 1 or 4 arguments, %d given." % len(parts))

				entity = self.game.get_entity(parts[1])[1]
				effect = self.game.get("effects", parts[2])
				self.check(parts[3], "dice")
				dice = int(parts[3])
				entity.add_effect(effect, dice)

			elif parts[0] == "erase":
				if len(parts) == 1:
					self.cPrint("erase entity\n"
								"\tnot to be confused with 'remove'\n"
								"\terases entity\n")
				elif len(parts) == 2:
					self.game.erase(parts[1])
				else:
					raise DnDException("Command 'erase' takes 1 or 2 arguments, %d given." % len(parts))

			elif parts[0] == "eval":
				if len(parts) == 1:
					self.cPrint("eval command\n"
								"\tbetter not use that!\n")
					return
				parts = " ".join(parts[1:])
				try:
					self.cPrint("eval:\n")
					eval(parts)
				except:
					self.cPrint("eval done wrong\n")

			elif parts[0] in ("fight", "f"):
				if len(parts) == 1:
					complete_string = ( "[f]ight entity1 entity2 val1 val2 placeholder_input_sequence\n"
										"\tval* is integer, 'a' for auto\n" )
					complete_string +=  "\t%s\n" % texts["placeholder_input_sequence"]
					complete_string +=  "\tboj entity1 entity2 <==> boj entity1 entity2 a a <!=!=!> boj entity1 entity2 a a anything\n"
					self.cPrint(complete_string)
					return

				e1 = self.game.get_entity(parts[1])[1]
				e2 = self.game.get_entity(parts[2])[1]

				if len(parts) in (3, 4):  # fight + 2 entities ?+placeholder_input_sequence
					d1 = -1
					d2 = -1
				elif len(parts) in (5, 6):  # fight + 2 entities + 2 dice rolls ?+placeholder_input_sequence
					if parts[3] == "a":
						d1 = -1
					else:
						self.check(parts[3], "dice")
						d1 = int(parts[3])

					if parts[4] == "a":
						d2 = -1
					else:
						self.check(parts[4], "dice")
						d2 = int(parts[4])

				if len(parts) in (4, 6):  # placeholder_input_sequence
					e1.fight(e2, d1, d2, self.cInput)
				else:
					e1.fight(e2, d1, d2)

			elif parts[0] in ("inventory", "i"):
				if len(parts) == 1:
					self.cPrint("[i]nventory entity\n"
								"\tchoose entity's inventory to be listed in inventory window; lists items in inventory\n"
								"[i]nventory entity add/del item\n"
								"\titem is from item_library\n"
								"[i]nventory entity mod item key value\n"
								"\titem is from entity's inventory\n"
								"\tkey & value are it's key & value respectively\n"
								"\tvalue is transformed into int if possible\n")
				elif len(parts) in (2, 4, 6):
					entity = self.game.get_entity(parts[1])[1]
					self.inventory_of_entity = entity
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
				else:
					raise DnDException("Command 'inventory' takes 1, 2, 4 or 6 arguments, %d given." % len(parts))

			elif parts[0] in ("library", "lib", "list", "l"):
				if len(parts) == 1:
					self.cPrint("[[l]ib]rary/list WHAT\n"
								"\tWHAT can be [en]tities, [ef]fects, [[s]p]ells, [i]tems\n")
				elif len(parts) == 2:
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
				else:
					raise DnDException("Command 'library' takes 1 or 2 arguments, %d given." % len(parts))

			elif parts[0] in ("move", "m"):
				if len(parts) == 1:
					self.cPrint("[m]ove target_entity_1 target_entity_2 ...\n"
								"\ttoggles all selected entities played_this_turn\n")
					return
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

			elif parts[0] in ("remove", "r"):
				if len(parts) == 1:
					self.cPrint("remove entity\n"
								"\tnot to be confused with 'erase'\n"
								"\tprints all effects of entity in numbered order\n"
								"ef+\n"
								"\tef are numbers of effects to remove\n"
								+texts["help"]["symbol"]["+"])
					return
				entity = self.game.get_entity(parts[1])[1]
				self.cPrint(
						"\n".join("%d. %s" % (i, entity.get_effect_string(e)) for i, e in enumerate(entity.body["effects"])) + "\n"
					)
				effects_to_remove = self.cInput("effects to remove:\n>>>").split()
				
				indexes = [int(i) if i.isdigit() else DnDException("%s is not a non-negative integer." % i) for i in effects_to_remove]

				entity.remove_effects_by_index(indexes)

			elif parts[0] == "set":
				if len(parts) == 1:
					self.cPrint("set entity\n"
								"\tprints all stats of entity\n"
								"set entity stat to_value\n")
					return
				entity = self.game.get_entity(parts[1])[1]
				if len(parts) == 2:
					entity.printStats()
					return
				if len(parts) == 3:
					raise DnDException("Command 'set' takes 1, 2 or 4 arguments, %d given." % len(parts))
				stat = parts[2]
				value = parts[3]
				entity.setStat(stat, value)

			elif parts[0] in ("spell", "s", "cast"):
				if len(parts) == 1:
					complete_string = ( "1) [s]pell/cast caster_entity spell manual_dice\n"
										"\tspell must be from library.spells\n"
										"\tif manual_dice, dice are not thrown automatically\n" )
					complete_string +=  "\t%s\n" % texts["placeholder_input_sequence"]

					complete_string +=  "2) target_entity_1 target_entity_2 ...\n"
					self.cPrint(complete_string)
					return
				elif len(parts) == 3:
					theInput = False
				elif len(parts) >= 4:
					theInput = self.cInput
				else:
					raise DnDException("Command 'spell' takes 1, 3 or 4 arguments, %d given." % len(parts))

				caster = self.game.get_entity(parts[1])[1]
				spell = self.game.get("spells", parts[2])

				# targets
				targets = self.cInput("targets:\n>>>")
				targets = [self.game.get_entity(target)[1] for target in targets.split()]

				caster.cast_spell(targets, spell, theInput)

			elif parts[0] in ("turn", "t"):
				self.game.turn()

			elif parts[0] in ("window", "w"):
				if len(parts) == 1:
					self.cPrint("w <==> window; ([w]indow)\n"
								"w show sleep_for\n"
								"\tdisplays windows (what + size) for sleep_for secs\n\n"  # TODO until enter is pressed
								
								"w get_size/gs what_window\n"
								"\tprints (height, width) of window\n"
								"w get_top_left/gtl what_window\n"
								"\tprints (y, x) of top left corner\n\n"

								"w set_size/ss what_window ncols nlines\n"
								"\tset window size to (ncols, nlines)\n"
								"w set_top_left/stl what_window y x\n"
								"\tset window top left corner to (y, x)\n")
				elif len(parts) >= 2:
					if parts[1] in ("show", "s"):
						if len(parts) == 3:
							if parts[2].isdigit():
								self.cPrint.cCurses.window_show(int(parts[2]))
							else:
								raise DnDException("Argument 'sleep_for' of command 'window show' must be integer, '%s' given." % parts[2])
						else:
							raise DnDException("Command 'window show' takes 3 arguments, %d given." % len(parts))
					elif parts[1] in ("get_size", "gs"):
						if len(parts) == 3:
								self.cPrint.cCurses.window_get_size(parts[2])
						else:
							raise DnDException("Command 'window get_size' takes 3 arguments, %d given." % len(parts))
					elif parts[1] in ("get_top_left", "gtl"):
						if len(parts) == 3:
								self.cPrint.cCurses.window_get_top_left(parts[2])
						else:
							raise DnDException("Command 'window get_top_left' takes 3 arguments, %d given." % len(parts))
					elif parts[1] in ("set_size", "ss"):
						if len(parts) == 5:
							if (parts[3].isdigit() and parts[4].isdigit()):
								self.cPrint.cCurses.window_set_size(parts[2], int(parts[3]), int(parts[4]))
							else:
								raise DnDException("ncols & nlines must be ints, %s, %s given." % (parts[3], parts[4]))
						else:
							raise DnDException("Command 'window set_size' takes 5 arguments, %d given." % len(parts))
					elif parts[1] in ("set_top_left", "stl"):
						if len(parts) == 5:
							if (parts[3].isdigit() and parts[4].isdigit()):
								self.cPrint.cCurses.window_set_top_left(parts[2], int(parts[3]), int(parts[4]))
							else:
								raise DnDException("y & x must be ints, %s, %s given." % (parts[3], parts[4]))
						else:
							raise DnDException("Command 'window set_top_left' takes 5 arguments, %d given." % len(parts))

			else:
				self.cPrint("?\n")

		except DnDException as exception:
			self.cPrint("?!: %s\n" % exception)
		except:
			if self.DEBUG:
				raise
			self.cPrint("fcked up\n")

		# entities window refresh
		try:
			self.cPrint.refresh_entities(self.game.entities)
			self.cPrint.refresh_inventory(self.inventory_of_entity)
		except DnDException as exception:
			self.cPrint("?!: %s\n" % exception)
		except:
			if self.DEBUG:
				raise
			self.cPrint("fcked up\n")

