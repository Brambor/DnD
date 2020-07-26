from copy import copy

from library.Main import library

from modules.Dice import D, dice_crit, dice_stat
from modules.DnDException import DnDException
from modules.Misc import convert_string_to_bool, normal_round, parse_sequence, yield_valid


class Entity():
	def __init__(self, library_entity, i, game):
		self.id = i
		self.body = copy(library_entity)
		del self.body["nickname"]
		self.nickname = library_entity["nickname"]
		# setStat (and many others) counts with "hp"
		# if "hp" not in self.body:
		self.body["hp"] = library_entity["hp_max"]
		if "mana_max" in library_entity:
			self.body["mana"] = library_entity["mana_max"]
		self.body["group"] = library_entity.get("group", "")
		self.body["inventory"] = library_entity.get("inventory", [])
		self.body["resistances"] = library_entity.get("resistances", set())
		self.body["effects"] = []
		self.body["alive"] = True
		self.game = game
		self.cPrint = game.cPrint
		self.played_this_turn = False

	def __str__(self):
		return "%s_%d" % (self.nickname, self.id)

	# RAW STAT MANIPULATION
	def printStat(self, stat):
		self.cPrint(f'{stat} = {self.get_stat(stat, False, for_printing=True)}\n')

	def printStats(self):
		complete_string = "nickname = '%s'\nid = %d\n" % (self.nickname, self.id)
		for stat in sorted(self.body.keys()):
			complete_string += f'{stat} = {self.get_stat(stat, False, for_printing=True)}\n'
		complete_string += "played_this_turn = %s\n" % self.played_this_turn
		self.cPrint(complete_string)

	def get_stats_reduced(self):
		"yields set(text to be printed, color_pair number)"
		played_this_turn = ("basic", "entity_played_this_turn")[self.played_this_turn]
		yield (str(self), played_this_turn)
		hp = [f' {self.body["hp"]}/{self.body["hp_max"]}', "HP"]
		if "mana" in self.body:
			yield hp
			yield (f' {self.body["mana"]}/{self.body["mana_max"]}\n', "mana")
		else:
			hp[0] += "\n"
			yield hp
		if self.body["effects"]:
			yield ("%s%s\n" % (
				" " * (len(self.body["derived_from"]) + 2),
				", ".join(f'{i["name"]}ϟ{i["value"]}' if i["type"] == "duration" else i["name"] for i in self.body["effects"]),
			), "basic")

	def setStat(self, stat, value, stat_type=None):
		body = self.body["skills"] if stat in library["skills"] else self.body

		if stat_type:
			if stat in body:
				raise DnDException("Entity '%s' already has stat '%s' so it's type cannot be modified, do not try." % (self, stat))
			if stat_type == "int":
				if value.replace("-", "", 1).isdigit():
					value = int(value)
			elif stat_type == "bool":
				value = convert_string_to_bool(value)
			elif stat_type != "str":
				raise DnDException("'stat_type' must be one of 'int', 'bool', or 'str', not '%s'." % stat_type)
			body[stat] = value
			return

		if ( ( stat in body ) and ( type(body[stat]) == str ) ):
			body[stat] = value
		elif ( ( stat in body ) and ( type(body[stat]) == int ) ):
			if value.replace("-", "", 1).isdigit():
				value = int(value)
				before = body[stat]
				body[stat] = value
				if stat == "hp":  # if entity died or rose from dead
					if before <= 0 and value > 0:
						self.check_revived()
					elif before > 0 and value <= 0:
						self.check_dead()
			else:
				raise DnDException("Stat %s is integer, value '%s' is not." % (stat, value))
		elif ( ( stat in body ) and ( type(body[stat]) == bool ) ):
			# b = True if a == "False": False
			body[stat] = convert_string_to_bool(value)
		elif stat == "nickname":
			self.set_nickname(value)
		elif stat == "played_this_turn":
			self.played_this_turn = convert_string_to_bool(value)
		#if stat == "weapon":
		#	self.body["weapon = int(value)
		# remove effect ?
		else:
			raise DnDException("Unknown stat '%s'. If you want to set it, give it 'stat_type'." % stat)

	def set_nickname(self, nickname):
		if nickname == "":
			raise DnDException("Nickname cannot be empty string ''!")
		elif nickname.isdigit():
			raise DnDException("Nickname cannot be an integer!")
		elif " " in nickname:
			raise DnDException("Nickname cannot contain space ' '!")
		elif nickname in (ent.nickname for ent in self.game.entities):
			raise DnDException("Nickname is already in use by %s" % self.game.get_entity(nickname)[1])
		else:
			self.nickname = nickname

	def get_stat(self, stat, return_as_integer=True, for_printing=False):
		"return_as_integer False: returns string in form '7 (5 + 4 - 2)' base + bonus - penalty"
		"for_printing True: wraps type==str with '' eg. \"v\" -> \"'v'\""
		if stat in self.body:
			value = self.body[stat]
		elif stat in library["skills"] and "skills" in self.body and stat in self.body["skills"]:
			value = self.body["skills"][stat]
		else:
			raise DnDException("Entity %s does not have stat '%s'." % (self, stat))

		if for_printing and type(value) == str:
			return f"'{value}'"
		if type(value) != int:
			return value
		else:
			base = value
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
		if self.get_stat("hp") <= 0:  # get_stat might result in wierd bug
			if self.body["alive"]:
				self.cPrint("%s IS DEAD!\n" % self)
			self.body["alive"] = False

	def check_revived(self):
		if self.get_stat("hp") > 0:
			if not self.body["alive"]:
				self.cPrint("%s IS ALIVE!\n" % self)
			self.body["alive"] = True

	# CAST
	def cast_spell(self, targets, spell, cInput=False):
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
				target.damaged( (({"magic"}, damage),) )
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
			total_hp += self.body.get(bonus, 0) * spell["bonuses"][bonus]  # TODO: if stat is missing, we would like to have QUANTUM_STAT?
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
	def damaged(self, damage_list, statement="", caused_by_effect=False):
		"damage_list example: [{'physical', 'acid'}: 12, {'acid'}: 8, {'acid'}: 5]"
		for damage_types, dmg in damage_list:

			# resistance
			dmg, damage_resistance = self.apply_damage_resistance(
				damage_types, dmg, caused_by_effect
			)

			#printing
			if statement == "":
				statement = "recived"
			if damage_resistance != "":
				damage_resistance = " (%s)" % damage_resistance
			if self.get_stat("alive"):
				self.cPrint(f'{str(self)} {statement} {dmg} {" & ".join(damage_types)} dmg{damage_resistance}\n')

			# applying
			self.body["hp"] -= dmg
			self.check_dead()

	def healed(self, heal):
		healed_for = min(self.get_stat("hp") + heal, self.get_stat("hp_max")) - self.get_stat("hp")
		self.cPrint("%s healed for %d HladinPetroleje\n" % (self, healed_for))
		self.body["hp"] += healed_for
		self.check_revived()

	# partly effects
	def apply_damage_resistance(self, damage_types, dmg, caused_by_effect):
		for damage_type in damage_types:
			if damage_type not in library["damage_types"]:
				raise DnDException("Unknown damage type: '%s'.\n" % damage_type)

		dmg_mult = 1
		relevant = []
		for damage_type in damage_types:
			damage_type = library["damage_types"][damage_type]
			if damage_type == "physical":
				dmg = max(dmg - self.get_stat("armor"), 0)
				relevant.append("armor %d" % self.get_stat("armor"))
			elif damage_type == "magic":
				dmg = max(dmg - self.get_stat("magie"), 0)
				relevant.append("magie %d" % self.get_stat("magie"))

			if "resistances" in self.body:
				if damage_type in self.body["resistances"]:
					r = self.body["resistances"][damage_type]
					if not (-1 <= r <= 1):
						self.cPrint("Warning! Resistance is not in interval <-100%, 100%>!\n")
					dmg_mult *= (1 - r)
					relevant.append("resistance to %s %d%%" % (damage_type, int(100 * r)))

			if not(caused_by_effect) and self.turned_by_into(damage_type.upper()):
				dmg_mult *= 0.5
				relevant.append("removed effect 50%")
				self.cPrint("Rule (off screen): Nevýhoda na kostku.\n")

		return (normal_round(dmg * dmg_mult), ", ".join(relevant))

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
			effect = self.game.get("effects", effect)
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

	def remove_effects_by_index(self, indexes):
		self.cPrint("%s is no longer:\n" % self)
		for index in sorted(indexes, reverse=True):
			if index < len(self.body["effects"]):
				self.cPrint("\t%s\n" % self.get_effect_string(self.body["effects"][index]))
				del self.body["effects"][index]
			else:
				raise DnDException("%d is too much!" % index)

	def apply_effects(self):
		i = 0
		effects = self.body["effects"]
		while i < len(effects):
			effect = effects[i]

			if effect["name"] == "FIRE":
				threw = D(effect["value"])
				self.damaged((({"true"}, threw),), "burns for", caused_by_effect=True)
				if threw == 1:
					self.cPrint("\t and stopped %s\n" % self.get_effect_string(effect))
					del effects[i]
					continue

			if effect["name"] == "BLEED":
				threw = D(effect["value"])
				self.damaged((({"true"}, threw),), "bleeds for", caused_by_effect=True)

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

	def turned_by_into(self, flag, once="NOT IMPLEMENTED"):
		"apply flag on current effects (only the first one!) \
		return True: something was turned; False: wasn't"

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
						effect = self.game.get("effects", effect)
						into_str = self.get_effect_string(effect, value)
					else:
						into_str = "nothing"

					self.cPrint("%s's %s turns into %s by %s\n" % ( self, original, into_str, flag ))
					if turns_into:
						self.add_effect(effect, value)
					return True
			i_x -= 1
		return False

	# INVENTORY
	def get_item(self, cmd):
		"Returns pair (i, item) from inventory firstly by index, secondly by derived_from (name)."
		"Note that item names SHOULD NOT be integers or .isdigit() strings."
		if not self.body["inventory"]:
			raise DnDException("Inventory is empty.")
		if cmd.isdigit():
			cmd = int(cmd)
			if cmd < len(self.body["inventory"]):
				chosen_i = cmd
			else:
				raise DnDException(
					"There are only %d (indexes from 0 to %d) items in inventory. Invalid index %d." % (
						len(self.body["inventory"]), len(self.body["inventory"])-1, cmd
				))
		else:
			chosen_item = None
			for i, item in enumerate(self.body["inventory"]):
				if item["derived_from"] == cmd:
					if chosen_item == None:
						chosen_item = item
						chosen_i = i
					else:
						raise DnDException("There are more items derived_from %s, please use index notation." % cmd)
			if chosen_item == None:
				raise DnDException("Item %s not found in %s's inventory." % (cmd, self))
		return (chosen_i, self.body["inventory"][chosen_i])

	def put_item_into_inventory(self, item):
		self.body["inventory"].append(copy(item))
		self.cPrint("%s is now in %s's inventory.\n" % (item, self))

	def remove_item_from_inventory(self, cmd):
		item_i, item = self.get_item(cmd)
		self.cPrint("%s vanished from %s's inventory.\n" % (item, self))
		del self.body["inventory"][item_i]

	def set_inventory_item(self, cmd, key, value):
		item_i, item = self.get_item(cmd)
		self.body["inventory"][item_i][key] = value
		self.cPrint("%s's item now reads: %s.\n" % (self, item))
