from modules.DnDException import DnDException

texts = {
	"placeholder_input_sequence": "placeholder_input_sequence activates inputing sequence latter down the chain; for now any value just means True",
}

class Parser():
	def __init__(self, game, cInput, cPrint, DEBUG):
		self.game = game
		self.DEBUG = DEBUG
		self.cInput = cInput
		self.cPrint = cPrint

	def check(self, values, types):
		for v, t in zip(values.split(), types.split()):
			if t == "entity_library":
				if not (v in self.game.library):
					raise DnDException("Entity '%s' not found in library." % v)
			if t == "dice":
				if not v.isdigit():
					raise DnDException("'%s' is not a valid integer." % v)


	def process(self, cmd):
		parts = cmd.split()
		try:
			if len(parts) == 0:
				pass
			elif parts[0] in ("#", "//"):
				self.cPrint("\r# %s\n" % " ".join(parts[1:]))

			elif parts[0] in ("help", "h"):
				cmd = [
					("help", "h"),
					("create", "c"),
					("print", "p"),
					("info", "i"),
					("effect", "e"),
					("turn", "t"),
					("eval",),
					("set",),
					("fight", "f"),
					("spell", "s", "cast"),
					("attack", "a", "dmg", "d"),
					("library", "lib", "list", "l"),
				]
				complete_string = ("write command without any atributes for further help,\n"
									"(except for turn)\n"
									"commands:\n"
				)
				
				for c in (", ".join(c) for c in cmd):
					complete_string += "\t%s\n" % c
				self.cPrint(complete_string)

			elif parts[0] in ("create", "c"):
				if len(parts) == 1:
					self.cPrint("[c]reate pes nickname_to_be_set\n")
					return
				self.check(parts[1], "entity_library")

				if len(parts) > 2:
					e = self.game.create(parts[1], parts[2])
				else:
					e = self.game.create(parts[1])

			elif parts[0] in ("print", "p"):
				if len(parts) == 1:
					self.cPrint("[p]rint what\n"
								"\t[e]ntities - all entities\n")
					return
				if parts[1] in ("entities", "e"):
					if self.game.entities:
						self.cPrint("\n".join(str(entity) for entity in self.game.entities) + "\n")
					else:
						self.cPrint("no entities\n")
				else:
					self.cPrint("?\n")

			elif parts[0] in ("info", "i"):
				if len(parts) == 1:
					self.cPrint("[i]nfo entity\n")
					return

				e = self.game.get_entity(parts[1])
				e.info()

			elif parts[0] in ("effect", "e"):
				if len(parts) == 1:
					self.cPrint("[e]ffect entity effect dice\n")
					return
				entity = self.game.get_entity(parts[1])
				effect = self.game.get_effect(parts[2])
				self.check(parts[3], "dice")
				dice = int(parts[3])
				entity.add_effect(effect, dice)

			elif parts[0] in ("turn", "t"):
				self.game.turn()

			elif parts[0] == "eval":
				if len(parts) == 1:
					self.cPrint("eval command\n\tbetter not use that!\n")
					return
				parts = " ".join(parts[1:])
				try:
					self.cPrint("eval:\n")
					eval(parts)
				except:
					self.cPrint("eval done wrong\n")

			elif parts[0] == "set":
				if len(parts) == 1:
					self.cPrint("set entity stat to_value\n"
								"\tset entity - prints all stats of entity\n")
					return
				entity = self.game.get_entity(parts[1])
				if len(parts) == 2:
					entity.printStats()
					return
				stat = parts[2]
				value = parts[3]
				entity.setStat(stat, value)

			elif parts[0] in ("fight", "f"):
				if len(parts) == 1:
					complete_string = ( "[f]ight entity1 entity2 val1 val2 placeholder_input_sequence\n"
										"\tval* is integer, 'a' for auto\n" )
					complete_string +=  "\t%s\n" % texts["placeholder_input_sequence"]
					complete_string +=  "\tboj entity1 entity2 <==> boj entity1 entity2 a a <!=!=!> boj entity1 entity2 a a anything\n"
					self.cPrint(complete_string)
					return

				e1 = self.game.get_entity(parts[1])
				e2 = self.game.get_entity(parts[2])

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

			elif parts[0] in ("spell", "s", "cast"):
				if len(parts) == 1:
					complete_string = ( "[s]pell/cast caster_entity spell dice\n"
										"\tspell must be from library.spells\n"
										"\tdice is integer, 'a' for auto\n" )
					complete_string +=  "\t%s\n" % texts["placeholder_input_sequence"]

					complete_string +=  "target_entity_1 target_entity_2 ...\n"
					self.cPrint(complete_string)
					return

				if len(parts) == 2:
					raise DnDException("Command 'spell' takes 1, 3 or 4 arguments, %d given." % len(parts))

				caster = self.game.get_entity(parts[1])
				spell = self.game.get_spell(parts[2])
				if len(parts) >= 3:
					d = -1
				else:
					self.check(parts[3], "dice")
					d = int(parts[3])
				if len(parts) >= 4:
					theInput = self.cInput
				else:
					theInput = False

				# targets
				targets = self.cInput("targets:\n>>>")
				targets = [self.game.get_entity(target) for target in targets.split()]

				caster.cast_spell(targets, spell, d, theInput)

			elif parts[0] in ("attack", "a", "dmg", "d"):
				if len(parts) == 1:
					self.cPrint("[a]ttack/[d]mg source_text\n"
							"\tsource is string latter used in log message (it is NOT optional, thought it is vaguely saved)\n"

							"type_of_dmg base_dmg dice(die)\n"
							"\tdamage_type ([p]hysical/[m]agic/[t]rue)\n"
							"\tdie are row integers representing used dice(die)\n"

							"target(s)\n"
							"\ttarget_entity_1 target_entity_2 ...\n")
					return

				source_text = " ".join(parts[1:])

				damages = self.cInput("type base dice(die):\n>>>").split()
				if len(damages) >= 2:
					damage_type = damages[0]
					if damage_type not in ("physical", "p", "magic", "m", "true", "t"):
						raise DnDException("Damage type must be one of [p]hysical/[m]agic/[t]rue, '%s' is not either of them." % damage_type)

					base_dmg = damages[1]
					self.check(base_dmg, "dice")
					base_dmg = int(base_dmg)

					dice = damages[2:]
					self.check(" ".join(dice), " ".join(["dice"]*len(dice)))  # cubersome...
					dice = [int(d) for d in dice]

				targets = self.cInput("targets:\n>>>")
				targets = [self.game.get_entity(target) for target in targets.split()]

				threw_crit = self.game.throw_dice(dice)
				damage_sum = base_dmg + sum(t[0] for t in threw_crit)
				for target in targets:
					target.damaged(damage_sum, damage_type)

			elif parts[0] in ("library", "lib", "list", "l"):
				if len(parts) == 1:
					self.cPrint("[l]ist WHAT\n"
								"\tWHAT can be [en]tities/[ef]fects/[[s]p]ells\n")
				elif len(parts) == 2:
					lib = {
						"entities": "en",
						"effects": "ef",
						"spells": "s",
						"sp": "s",
					}.get(parts[1], parts[1])
					if lib == "en":
						lib = self.game.library
					elif lib == "ef":
						lib = self.game.effects
					elif lib == "s":
						lib = self.game.spells
					else:
						raise DnDException("No library '%s'." % lib)
					self.cPrint( str(list(lib)) + "\n" )
				else:
					raise DnDException("Command 'library' takes 1 or 2 arguments, %d given." % len(parts))

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
		except DnDException as exception:
			self.cPrint("?!: %s\n" % exception)
		except:
			if self.DEBUG:
				raise
			self.cPrint("fcked up\n")

