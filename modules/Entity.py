from copy import copy

from modules.Dice import D, dice_crit, dice_stat
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
		self.cPrint("hp: %d/%d %s" % (self.body["hp"], self.body["hp_max"], dead))
		self.cPrint("mana: %d/%d" % (self.body["mana"], self.body["mana_max"]))
		self.cPrint("weapon: %s" % self.body["weapon"])
		self.cPrint("boj: %d" % self.body["boj"])
		# TURN effects and DICE effects
		effects = ", ".join(self.get_effect_string(e) for e in self.body["effects"])  # wont work for turn based effects
		if effects != "":
			self.cPrint("effects: %s" % effects)

	# RAW STAT MANIPULATION
	def printStats(self):
		for key in list(self.body.keys()) + ["nickname"]:
			if key == "nickname":
				value = self.nickname
			else:
				value = self.body[key]
			if type(value) == str:
				value = "%s%s%s" % ('"', value, '"')
			self.cPrint("%s = %s" % (key, value))

	def setStat(self, stat, value):
		if ( ( stat in self.body ) and ( type(self.body[stat]) == int ) ):
			self.body[stat] = int(value)
		elif ( ( stat in self.body ) and ( type(self.body[stat]) == bool ) ):
			# b = True if a == "False": False
			if value == "True":
				self.body[stat] = True
			elif value == "False":
				self.body[stat] = False
			else:
				self.cPrint("?")
		elif stat == "nickname":
			self.nickname = value
		#if stat == "weapon":
		#	self.body["weapon = int(value)
		# remove effect ?
		else:
			self.cPrint("?")

	# ALIVE / DEATH
	def alive(self):
		return self.body["alive"]

	def check_dead(self):  # not handeled at all
		if self.body["hp"] <= 0:
			self.cPrint("%s IS DEAD!" % self)
			self.body["alive"] = False

	def check_revived(self):
		if self.body["hp"] > 0:
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
			self_D = dice_stat(self.body["boj"])
		if opponent_D == -1:
			opponent_D = dice_stat(opponent.body["boj"])

		self_power = self.body["boj"] + self_D
		opponent_power = opponent.body["boj"] + opponent_D

		for e, total_power in ((self, self_power), (opponent, opponent_power)):
			self.cPrint("%s fights with power of %d (base %d + dice %d)" % (
				e, total_power, e.body["boj"], total_power - e.body["boj"]
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
			self_D = dice_stat(self.body["magie"])

		spell_cost = spell["mana_consumption"].get("base", 0) \
					+spell["mana_consumption"].get("per_target", 0) * len(targets)

		if self.body["mana"] >= spell_cost:
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
			dmg = max(dmg - self.body["armor"], 0)
		elif damage_type == "magic":
			dmg = max(dmg - self.body["magie"], 0)
		elif damage_type != "true":
			raise
		if statement == "":
			statement = "recived"
		if self.body["alive"]:
			self.cPrint("%s %s %d dmg" % (self, statement, dmg))
		self.body["hp"] -= dmg
		self.check_dead()

	def healed(self, heal):
		healed_for = min(self.body["hp"] + heal, self.body["hp_max"]) - self.body["hp"]
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
		for under_effect in self.body["effects"]:
			if "prevents" in under_effect:
				if set(under_effect["prevents"]).intersection(set(effect["flags"])):
					self.cPrint("%s is immune to %s because they are %s" % (
						self,
						effect["name"],
						self.get_effect_string(under_effect)
					))
					return



		# WET + CHILL -> FREEZE
		if effect["name"] == "chill":
			wet = self.get_effect("wet")
			if wet:
				# remove wettness, chill
				self.remove_effects(("WET", "CHILL"))
				self.add_effect(self.game.get_effect("freeze"), 3)
				return

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

		self.cPrint("%s is %s now%s" % (self, self.get_effect_string(effect), extra_comment))  # DUPLICATE

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

	#def del_effect(self, )

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
