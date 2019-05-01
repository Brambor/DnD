from copy import copy

from modules.Dice import D, dice_crit, dice_stat
from modules.DnDException import DnDException
from modules.Misc import parse_sequence, yield_valid


class Entity():
	def __init__(self, library_entity, i, game):
		self.i = i
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
		return "%s_%d" % (self.nickname, self.i)

	def info(self):
		self.cPrint("nickname_id: %s" % self)
		self.cPrint("derived_from: %s" % self.body["derived_from"])
		if not self.body["alive"]:
			dead = " (DEAD)"
		else:
			dead = ""
		self.cPrint("hp: %d/%s %s" % (self.get_stat("hp"), self.get_stat("hp_max", False), dead))
		self.cPrint("mana: %d/%s" % (self.get_stat("mana"), self.get_stat("mana_max", False)))
		self.cPrint("weapon: %s" % self.body["weapon"])
		self.cPrint("boj: %s" % self.get_stat("boj", False))
		# TURN effects and DICE effects
		effects = ", ".join(self.get_effect_string(e) for e in self.body["effects"])  # wont work for turn based effects
		if effects != "":
			self.cPrint("effects: %s" % effects)

	# RAW STAT MANIPULATION
	def printStats(self):
		for key in sorted(list(self.body.keys()) + ["nickname"]):
			if key == "nickname":
				value = self.nickname
			else:
				value = self.get_stat(key, False)
			if type(self.body[key]) == str:
				value = "'%s'" % value
			self.cPrint("%s = %s" % (key, value))

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
				self.cPrint("?")
		elif stat == "nickname":
			self.set_nickname(value)
		#if stat == "weapon":
		#	self.body["weapon = int(value)
		# remove effect ?
		else:
			self.cPrint("?")

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
			bonus = 0
			penalty = 0
			# lowered by effects
			# TODO
			if return_as_integer:
				return base + bonus - penalty
			else:
				if bonus or penalty:
					if bonus:
						bonus_str = " + %d" % bonus
					else:
						bonus_str = ""
					if penalty:
						penalty_str = " - %d" % penalty
					else:
						penalty_str = ""
					return "%d (%d%s%s)" % (base + bonus - penalty, base, bonus_str, penalty_str)  # 7 (5 + 4 - 2) base + bonus - penalty
				else:
					return str(base)

	# ALIVE / DEATH
	def alive(self):
		return self.get_stat("alive")

	def check_dead(self):  # not handeled at all
		if self.get_stat("hp") <= 0:
			self.cPrint("%s IS DEAD!" % self)
			self.body["alive"] = False

	def check_revived(self):
		if self.get_stat("hp") > 0:
			if self.body["alive"] == False:
				self.cPrint("%s IS ALIVE!" % self)
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
			self.cPrint("%s fights with power of %d (base %d + dice %d)" % (
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
			self.cPrint("%s does not have enought mana for %s" % (self, spell["name"]))
			return

		for target in targets:
			target.remove_effects(spell["effects"].get("removes", set()))

			crit = False
			if "damages" in spell["effects"]:
				damage, crit = self.count_spell_hp(spell["effects"]["damages"], cInput)
				target.damaged(damage, "magic")
				if crit:
					self.cPrint("Critical spell!!")
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
		if damage_type == "physical":
			dmg = max(dmg - self.get_stat("armor"), 0)
		elif damage_type == "magic":
			dmg = max(dmg - self.get_stat("magie"), 0)
		elif damage_type != "true":
			raise
		if statement == "":
			statement = "recived"
		if self.get_stat("alive"):
			self.cPrint("%s %s %d dmg" % (self, statement, dmg))
		self.body["hp"] -= dmg
		self.check_dead()

	def healed(self, heal):
		healed_for = min(self.get_stat("hp") + heal, self.get_stat("hp_max")) - self.get_stat("hp")
		self.cPrint("%s healed for %d HladinPetroleje" % (self, healed_for))
		self.body["hp"] += healed_for
		self.check_revived()

	# EFFECTS
	def get_effect_string(self, effect):
		if effect["type"] == "dice":
			str_duration = "(D%d)" % effect["value"]
		elif effect["type"] == "duration":  # 
			str_duration = "(for %d turns)" % effect["value"]
		else:
			raise  # the programer screwed up!

		if "on_print" in effect:
			return "%s %s" % (effect["on_print"], str_duration)
		elif effect["type"] == "duration":
			return "%s %s" % (effect["name"], str_duration)
		elif effect["type"] == "dice":
			return "%sing %s" % (effect["name"], str_duration)
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
			self.cPrint("%s is immune to %s because they are %s" % (
				self,
				effect["name"],
				self.get_effect_string(immunity_by)
			))
			return

		# applies flags of effect that is being added
		changes_has_been_made = False
		for effect_flag in effect["flags"]:
			ret_flag = self.apply_flag(effect_flag)  # does quite a lot!
			changes_has_been_made = max(changes_has_been_made, ret_flag)
		if changes_has_been_made:
			return

		# Add/Refresh effect
		result = ""
		effect = copy(effect)
		if effect["on stack"] == "add":
			result = "add"
		elif effect["on stack"] == "refresh":
			old_effect = self.get_effect(effect["name"])
			if old_effect:  # the refreshment
				result = "refresh"
			else:  # effect not yet present
				result = "add"

		extra_comment = ""
		if result == "add":
			effect["value"] = value
			self.body["effects"].append(effect)
		elif result == "refresh":  # not very pretty, but meh...
			old_effect["value"] = max(value, old_effect["value"])
			effect = old_effect
			extra_comment = " (refreshed)"

		self.cPrint("%s is %s now%s" % (self, self.get_effect_string(effect), extra_comment))

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
			if set(flags).intersection(set(effect["flags"])):
				self.cPrint("%s is no longer %s" % (self, self.get_effect_string(effect)))
				del self.body["effects"][i]
			else:
				i += 1

	def apply_effects(self):
		i = 0
		effects = self.body["effects"]
		while i < len(effects):
			effect = effects[i]

			if ("FIRE" in effect["flags"]):
				threw = D(effect["value"])
				self.damaged(threw, "true", "burns for")
				if threw == 1:
					self.cPrint("\t and stopped %s" % self.get_effect_string(effect))
					del effects[i]
					continue

			if ("BLEADING" in effect["flags"]):
				threw = D(effect["value"])
				self.damaged(threw, "true", "bleads for")

			if effect["type"] == "duration":
				effect["value"] -= 1
				if effect["value"] == 0:
					self.cPrint("%s is no longer %s" % (self, self.get_effect_string(effect)))
					del effects[i]

			i += 1

	def immune_to_effect(self, effect):
		for under_effect in self.body["effects"]:
			if "prevents" in under_effect:
				if set(under_effect["prevents"]).intersection(set(effect["flags"])):
					return under_effect  # imunity by
		return None  # Nothing gives imunity

	def apply_flag(self, flag):
		# apply flag on current effects
		changes_has_been_made = False
		i = 0
		max_i = len(self.body["effects"])
		while i < max_i:
			inc = True
			under_effect = self.body["effects"][i]
			if "turned_by_into" in under_effect:
				for by_flag, into in under_effect["turned_by_into"]:
					if by_flag == flag:
						del self.body["effects"][i]
						self.add_effects([into])
						max_i -= 1
						inc = False
						changes_has_been_made = True
						break
			if inc:
				i += 1
		return changes_has_been_made
