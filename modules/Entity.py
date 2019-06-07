from copy import copy

from modules.Dice import D, dice_crit, dice_stat
from modules.DnDException import DnDException
from modules.Misc import parse_sequence, yield_valid


class Entity():
	def __init__(self, library_entity, i, game):
		self.id = i
		self.body = copy(library_entity)
		del self.body["nickname"]
		self.nickname = library_entity["nickname"]
		self.body["hp"] = library_entity["hp_max"]
		self.body["mana"] = library_entity["mana_max"]
		self.body["effects"] = []
		self.body["alive"] = True
		self.game = game
		self.cPrint = game.cPrint

	def __str__(self):
		return "%s_%d" % (self.nickname, self.id)

	def info(self):
		complete_string = "nickname_id: %s\n" % self
		complete_string += "derived_from: %s\n" % self.body["derived_from"]
		dead = " (DEAD)" if not self.body["alive"] else ""
		complete_string += "hp: %d/%s%s\n" % (self.get_stat("hp"), self.get_stat("hp_max", False), dead)
		complete_string += "mana: %d/%s\n" % (self.get_stat("mana"), self.get_stat("mana_max", False))
		complete_string += "weapon: %s\n" % self.body["weapon"]
		complete_string += "boj: %s\n" % self.get_stat("boj", False)
		# TURN effects and DICE effects
		effects = ", ".join(self.get_effect_string(e) for e in self.body["effects"])  # wont work for turn based effects
		if effects != "":
			complete_string += "effects: %s\n" % effects
		self.cPrint(complete_string)

	# RAW STAT MANIPULATION
	def printStats(self):
		complete_string = "nickname = '%s'\nid = %d\n" % (self.nickname, self.id)
		for key in sorted(self.body.keys()):
			value = self.get_stat(key, False)
			if type(self.body[key]) == str:
				value = "'%s'" % value
			complete_string += "%s = %s\n" % (key, value)
		self.cPrint(complete_string)

	def setStat(self, stat, value):
		if ( ( stat in self.body ) and ( type(self.body[stat]) == int ) ):
			if value.isdigit():
				self.body[stat] = int(value)
			else:
				raise DnDException("%s's stat %s is integer, value '%s' is not." % (self, stat, value))
		elif ( ( stat in self.body ) and ( type(self.body[stat]) == bool ) ):
			# b = True if a == "False": False
			if value == "True":
				self.body[stat] = True
			elif value == "False":
				self.body[stat] = False
			else:
				raise DnDException("Unacceptable value '%s' accepting only 'True' and 'False'." % value)
		elif stat == "nickname":
			self.set_nickname(value)
		#if stat == "weapon":
		#	self.body["weapon = int(value)
		# remove effect ?
		else:
			raise DnDException("Unknown stat '%s'" % stat)

	def set_nickname(self, nickname):
		if nickname == "":
			raise DnDException("Nickname cannot be empty string ''!")
		elif nickname.isdigit():
			raise DnDException("Nickname cannot be an integer!")
		elif " " in nickname:
			raise DnDException("Nickname cannot contain space ' '!")
		elif nickname in (ent.nickname for ent in self.game.entities):
			raise DnDException("Nickname is already in use by %s" % self.game.get_entity(nickname))
		else:
			self.nickname = nickname


	def get_stat(self, stat, return_as_integer=True):
		"return_as_integer False: returns string in form '7 (5 + 4 - 2)' base + bonus - penalty"
		if type(self.body[stat]) != int:
			return self.body[stat]
		else:
			base = self.body[stat]
			bp = {
				"stat_penalty": 0,
				"stat_bonus": 0,
			}
			# lowered by effects
			for bonus_or_penalty in ("stat_penalty", "stat_bonus"):
				for effect in self.body["effects"]:
					if bonus_or_penalty in effect:
						bp[bonus_or_penalty] += effect[bonus_or_penalty].get(stat, 0)

			if return_as_integer:
				return base + bp["stat_bonus"] - bp["stat_penalty"]
			else:
				if bp["stat_bonus"] or bp["stat_penalty"]:
					bonus_str = " + %d" % bp["stat_bonus"] if bp["stat_bonus"] else ""
					penalty_str = " - %d" % bp["stat_penalty"] if bp["stat_penalty"] else ""
					return "%d (%d%s%s)" % (base + bp["stat_bonus"] - bp["stat_penalty"], base, bonus_str, penalty_str)  # 7 (5 + 4 - 2) base + bonus - penalty
				else:
					return str(base)

	# ALIVE / DEATH
	def alive(self):
		return self.get_stat("alive")

	def check_dead(self):  # not handeled at all
		if self.get_stat("hp") <= 0:
			self.cPrint("%s IS DEAD!\n" % self)
			self.body["alive"] = False

	def check_revived(self):
		if self.get_stat("hp") > 0:
			if self.body["alive"] == False:
				self.cPrint("%s IS ALIVE!\n" % self)
			self.body["alive"] = True

	# FIGHT, CAST
	def attack(self, target, dmg):
		target.damaged(dmg, "physical")

	def fight(self, opponent, self_D, opponent_D, cInput=False):
		"""... self_D, opponent_D are integers; -1 for auto
		cInput passed down if needed """
		# determining fight skill (who wins)
		if self_D == -1:
			self_D = dice_stat(self.get_stat("boj"))
		if opponent_D == -1:
			opponent_D = dice_stat(opponent.get_stat("boj"))

		self_power = self.get_stat("boj") + self_D
		opponent_power = opponent.get_stat("boj") + opponent_D

		for e, total_power in ((self, self_power), (opponent, opponent_power)):
			self.cPrint("%s fights with power of %d (base %d + dice %d)\n" % (
				e, total_power, e.get_stat("boj"), total_power - e.get_stat("boj")
			))

		# knowing who won, counting damage
		if self_power > opponent_power:
			self.attack(opponent, self.body["weapon"].use(cInput, self.cPrint))
		elif opponent_power > self_power:
			opponent.attack(self, opponent.body["weapon"].use(cInput, self.cPrint))
		else:
			# basic damage, no dice needed
			self.attack(opponent, self.body["weapon"].dmg)
			opponent.attack(self, opponent.body["weapon"].dmg)

	def cast_spell(self, targets, spell, self_D, cInput=False): #  so far only for healing
		if self_D == -1:
			self_D = dice_stat(self.get_stat("magie"))

		spell_cost = spell["mana_consumption"].get("base", 0) \
					+spell["mana_consumption"].get("per_target", 0) * len(targets)

		if self.get_stat("mana") >= spell_cost:
			self.body["mana"] -= spell_cost
		else:
			self.cPrint("%s does not have enought mana for %s\n" % (self, spell["name"]))
			return

		for target in targets:
			target.remove_effects(spell["effects"].get("removes", set()))

			crit = False
			if "damages" in spell["effects"]:
				damage, crit = self.count_spell_hp(spell["effects"]["damages"], cInput)
				target.damaged(damage, "magic")
				if crit:
					self.cPrint("Critical spell!!\n")
			if "heals" in spell["effects"]:
				heal = self.count_spell_hp(spell["effects"]["heals"], cInput)[0]
				target.healed(heal)

			target.add_effects(spell["effects"].get("adds", dict()).get("base", set()))
			if crit:
				target.add_effects(spell["effects"].get("adds", dict()).get("on_crit", set()))

	def count_spell_hp(self, spell, cInput):
		total_hp = spell.get("base", 0)
		for bonus in spell.get("bonuses", set()):
			total_hp += self.body.get(bonus, 0) * spell["bonuses"][bonus]
		crit = False
		# make seq
		dice = spell.get("dice")
		if dice:
			if cInput:
				threw = next(parse_sequence(cInput("threw >>>")))
			else:
				threw = D(dice)
			crit = dice_crit(dice, threw, self.cPrint)
			total_hp += threw
		return (total_hp, crit)

	# RECIVE DAMAGE, HEAL
	def damaged(self, dmg, damage_type, statement=""):
		if damage_type in ("physical", "p"):
			dmg = max(dmg - self.get_stat("armor"), 0)
		elif damage_type in ("magic", "m"):
			dmg = max(dmg - self.get_stat("magie"), 0)
		elif damage_type not in ("true", "t"):
			raise
		if statement == "":
			statement = "recived"
		if self.get_stat("alive"):
			self.cPrint("%s %s %d dmg\n" % (self, statement, dmg))
		self.body["hp"] -= dmg
		self.check_dead()

	def healed(self, heal):
		healed_for = min(self.get_stat("hp") + heal, self.get_stat("hp_max")) - self.get_stat("hp")
		self.cPrint("%s healed for %d HladinPetroleje\n" % (self, healed_for))
		self.body["hp"] += healed_for
		self.check_revived()

	# EFFECTS
	def get_effect_string(self, effect, sub_value=None):
		if sub_value != None:
			value = sub_value
		else:
			value = effect["value"]

		if value:
			if effect["type"] == "dice":
				str_duration = " (D%d)" % value
			elif effect["type"] == "duration":
				str_duration = " (for %d turns)" % value
			else:
				raise  # the programer screwed up!
		else:
			str_duration = ""

		if "on_print" in effect:
			return "%s%s" % (effect["on_print"], str_duration)
		elif effect["type"] == "duration":
			return "%s%s" % (effect["name"], str_duration)
		elif effect["type"] == "dice":
			return "%sing%s" % (effect["name"], str_duration)
		else:
			raise

	def get_effect(self, name):
		for effect in self.body["effects"]:
			if effect["name"] == name:
				return effect
		return None

	def add_effect(self, effect, value):
		# immunity:
		# by effect
		immunity_by = self.immune_to_effect(effect)
		if immunity_by:
			self.cPrint("%s is immune to %s because they are %s\n" % (
				self,
				effect["name"],
				self.get_effect_string(immunity_by)
			))
			return

		# turned by into
		if self.turned_by_into(effect["name"]):
			return

		effect = copy(effect)
		# Effect stat bonuses / penalties (throwing the dice)
		for bonus_or_penalty in ("stat_penalty", "stat_bonus"):
			if bonus_or_penalty in effect:
				effect[bonus_or_penalty] = copy(effect[bonus_or_penalty])
				for stat in effect[bonus_or_penalty]:
					stat_value = effect[bonus_or_penalty][stat]
					if type(stat_value) == tuple:
						# check format
						if not ( (stat_value[0] == "dice") and (type(stat_value[1]) == int) ):
							raise
						effect[bonus_or_penalty][stat] = D(stat_value[1])

		# Add/Refresh effect
		result = ""
		if effect["on_stack"] == "add":
			result = "add"
		elif effect["on_stack"] == "refresh":
			old_effect = self.get_effect(effect["name"])
			if old_effect:  # the refreshment
				result = "refresh"
			else:  # effect not yet present
				result = "add"

		extra_comment = ""
		if result == "add":
			effect["value"] = value
			self.body["effects"].append(effect)
		elif result == "refresh":
			old_effect["value"] = max(value, old_effect["value"])
			effect = old_effect
			extra_comment = " (refreshed)"
		else:
			raise

		self.cPrint("%s is %s now%s\n" % (self, self.get_effect_string(effect), extra_comment))

		# Remove effects that entity is now immune to
		if "prevents" in effect:
			self.remove_effects(effect["prevents"])

	def add_effects(self, effects):
		for effect, value in effects:
			effect = self.game.get_effect(effect)
			self.add_effect(effect, value)

	def remove_effects(self, flags):
		i = 0
		while i < len(self.body["effects"]):
			effect = self.body["effects"][i]
			if effect["name"] in flags:
				self.cPrint("%s is no longer %s\n" % (self, self.get_effect_string(effect)))
				del self.body["effects"][i]
			else:
				i += 1

	def apply_effects(self):
		i = 0
		effects = self.body["effects"]
		while i < len(effects):
			effect = effects[i]

			if effect["name"] == "FIRE":
				threw = D(effect["value"])
				self.damaged(threw, "true", "burns for")
				if threw == 1:
					self.cPrint("\t and stopped %s\n" % self.get_effect_string(effect))
					del effects[i]
					continue

			if effect["name"] == "BLEAD":
				threw = D(effect["value"])
				self.damaged(threw, "true", "bleads for")

			if effect["type"] == "duration":
				effect["value"] -= 1
				if effect["value"] == 0:
					self.cPrint("%s is no longer %s\n" % (self, self.get_effect_string(effect)))
					del effects[i]

			i += 1

	def immune_to_effect(self, effect):
		for under_effect in self.body["effects"]:
			if "prevents" in under_effect:
				if effect["name"] in under_effect["prevents"]:
					return under_effect  # imunity by
		return None  # Nothing gives imunity

	def turned_by_into(self, flag, once=False):
		"apply flag on current effects (only the first one!) \
		return True: something was turned; False: not"

		i_x = len(self.body["effects"]) - 1
		while i_x >= 0:
			under_effect = self.body["effects"][i_x]
			if "turned_by_into" in under_effect:
				if flag in under_effect["turned_by_into"]:
					turns_into = under_effect["turned_by_into"][flag]

					original = self.get_effect_string(self.body["effects"][i_x])
					del self.body["effects"][i_x]
					if turns_into:
						effect, value = turns_into
						effect = self.game.get_effect(effect)
						into_str = self.get_effect_string(effect, value)
					else:
						into_str = "nothing"

					self.cPrint("%s's %s turns into %s by %s\n" % ( self, original, into_str, flag ))
					if turns_into:
						self.add_effect(effect, value)
					return True
			i_x -= 1
		return False
