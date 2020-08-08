from copy import copy

from library.Main import library

from modules.Dice import D, dice_crit
from modules.DnDException import DnDException
from modules.Misc import calculate, convert_string_to_bool, get_library, normal_round, parse_damage, parse_sequence


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
		for value, default in (("group", ""), ("inventory", []), ("resistances", {})):
			self.body[value] = library_entity.get(value, default)
		self.body["effects"] = []
		self.body["alive"] = True
		self.game = game
		self.cPrint = game.cPrint
		self.played_this_turn = False

	def __str__(self):
		return f"{self.nickname}_{self.id}"

	# RAW STAT MANIPULATION
	def printStat(self, stat):
		self.cPrint(f'{stat} = {self.get_stat(stat, False, for_printing=True)}\n')

	def printStats(self):
		complete_string = f"nickname = '{self.nickname}'\nid = {self.id}\n"
		for stat in sorted(self.body.keys()):
			complete_string += f'{stat} = {self.get_stat(stat, False, for_printing=True)}\n'
		complete_string += f"played_this_turn = {self.played_this_turn}\n"
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
			spaces = " " * (len(self.body["derived_from"]) + 2)
			eff = tuple(", ".join(f'{e["name"]}{ch}{e["value"]}' for e in self.body["effects"] if e["type"] == tpe)
				for ch, tpe in (("ϟ", "duration"), ("ϗ", "dice")))
			yield f"{spaces}{eff[0]}{', ' if all(eff) else ''}{eff[1]}\n", "basic"

	def setStat(self, stat, value, stat_type=None):
		type_forced = False
		if stat in library["skills"]:
			body = self.body["skills"]
		elif stat in library["damage_types"]:
			body = self.body["resistances"]
			type_forced = True
			type_required = "float"
		else:
			body = self.body

		if stat_type:
			if type_forced and type_required != stat_type:
				raise DnDException(f"Stat '{stat}' must be of type '{type_required}', it cannot be '{stat_type}'.")
			if stat in body:
				raise DnDException(f"Entity '{self}' already has stat '{stat}' so it's type cannot be modified, do not try.")
			if stat_type == "int":
				value = int(calculate(value))
			elif stat_type == "float":
				value = float(calculate(value))
			elif stat_type == "bool":
				value = convert_string_to_bool(value)
			elif stat_type != "str":
				raise DnDException(f"'stat_type' must be one of 'int', 'float', 'bool', or 'str', not '{stat_type}'.")
			body[stat] = value
			return

		if ( ( stat in body ) and ( type(body[stat]) == str ) ):
			body[stat] = value
		elif ( ( stat in body ) and ( type(body[stat]) == float ) ):
			body[stat] = float(calculate(value))
		elif ( ( stat in body ) and ( type(body[stat]) == int ) ):
			value = int(calculate(value))
			before = body[stat]
			body[stat] = value
			if stat == "hp":  # if entity died or rose from dead
				if before <= 0 and value > 0:
					self.check_revived()
				elif before > 0 and value <= 0:
					self.check_dead()
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
			raise DnDException(f"Unknown stat '{stat}'. If you want to set it, give it 'stat_type'.")

	def set_nickname(self, nickname):
		if nickname == "":
			raise DnDException("Nickname cannot be empty string ''!")
		elif nickname.isdigit():
			raise DnDException("Nickname cannot be an integer!")
		elif " " in nickname:
			raise DnDException("Nickname cannot contain space ' '!")
		elif nickname in (ent.nickname for ent in self.game.entities):
			raise DnDException(f"Nickname is already in use by {self.game.get_entity(nickname)[1]}")
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
			raise DnDException(f"Entity {self} does not have stat '{stat}'.")

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
					bonus_str = f' + {bp["stat_bonus"]}' if bp["stat_bonus"] else ""
					penalty_str = f' - {bp["stat_penalty"]}' if bp["stat_penalty"] else ""
					# 7 (5 + 4 - 2)
					return f'{base + bp["stat_bonus"] - bp["stat_penalty"]} ({base}{bonus_str}{penalty_str})'
				else:
					return str(base)

	# ALIVE / DEATH
	def alive(self):
		return self.get_stat("alive")

	def check_dead(self):  # not handeled at all
		if self.get_stat("hp") <= 0:  # get_stat might result in wierd bug
			if self.body["alive"]:
				self.cPrint(f"{self} IS DEAD!\n")
			self.body["alive"] = False

	def check_revived(self):
		if self.get_stat("hp") > 0:
			if not self.body["alive"]:
				self.cPrint(f"{self} IS ALIVE!\n")
			self.body["alive"] = True

	# ATTACK
	def attack(self, attack_str):
		attack = self.get_attack(attack_str)
		if "dmg" in attack:
			damage_list, crits = parse_damage(attack["dmg"], self.game)
		else:
			return []
		for c in crits:
			if not("on_crit" in attack and c in attack["on_crit"]):
				raise DnDException(f"{self}'s attack {attack_str} doesn't have 'on_crit' for dice marked '{c}', which just critted.")
			att = attack["on_crit"][c]
			if att[0] == "add_attack":
				damage_list.extend(self.attack(att[1]))
			elif att[0] == "print":
				self.cPrint(f"{att[1]} (prints {self}'s attack '{attack_str}' by critting on '{c}').\n")
		return damage_list

	def attack_list_print(self):
		if "attacks" in self.body and self.body["attacks"]:
			s = "\n".join(f" *{k}" if "reaction" in self.body["attacks"][k] else f"  {k}" for k in self.body["attacks"].keys())
			if any("reaction" in self.body["attacks"][k] for k in self.body["attacks"].keys()):
				note = "Attacks starting with * are ment only as reactions and shouldn't be used.\n"
			else:
				note = ""
			self.cPrint(f"{self}'s attacks:\n{s}\n{note}")
		else:
			self.cPrint(f"{self} has no attacks\n")

	def get_attack(self, attack_str):
		if attack_str in self.body["attacks"]:
			return self.body["attacks"][attack_str]
		else:
			raise DnDException(f"Entity {self} does not know {attack_str}.")

	# CAST
	def cast_spell(self, targets, spell, cInput=False):
		spell_cost = spell["mana_consumption"].get("base", 0) \
					+spell["mana_consumption"].get("per_target", 0) * len(targets)

		if self.get_stat("mana") >= spell_cost:
			self.body["mana"] -= spell_cost
		else:
			self.cPrint(f'{self} does not have enought mana for {spell["name"]}\n')
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
		"applies resistances, result rounds to two decimal places"
		"self.receive sum of results rounded to int"
		total_dmg = 0
		dmg_string = []
		for damage_types, dmg in damage_list:
			# resistance
			dmg, damage_resistance = self.apply_damage_resistance(
				damage_types, dmg, caused_by_effect
			)
			dmg = round(dmg, 2)
			total_dmg += dmg

			# string
			if dmg == int(dmg):
				dmg = int(dmg)
			if (damage_types := " & ".join(damage_types)):
				damage_types = f" {damage_types}"
			if damage_resistance:
				damage_resistance = f" ({damage_resistance})"
			dmg_string.append(f"{dmg}{damage_types}{damage_resistance}")
		total_dmg = normal_round(total_dmg)

		#printing
		if not statement:
			statement = "received"
		if self.get_stat("alive"):
			self.cPrint(f'{self} {statement} {total_dmg} dmg: {", ".join(dmg_string)}\n')

		# applying
		self.body["hp"] -= total_dmg
		self.check_dead()

	def healed(self, heal):
		healed_for = min(self.get_stat("hp") + normal_round(heal), self.get_stat("hp_max")) - self.get_stat("hp")
		self.cPrint(f"{self} healed for {healed_for} HladinPetroleje\n")
		self.body["hp"] += healed_for
		self.check_revived()

	# partly effects
	def apply_damage_resistance(self, damage_types, dmg, caused_by_effect):
		for damage_type in damage_types:
			if damage_type not in library["damage_types"]:
				raise DnDException(f"Unknown damage type: '{damage_type}'.\n")

		dmg_mult = 1
		relevant = []
		for damage_type in damage_types:
			damage_type = library["damage_types"][damage_type]
			if damage_type == "physical":
				dmg = max(dmg - self.get_stat("armor"), 0)
				relevant.append(f'armor {self.get_stat("armor")}')
			elif damage_type == "magic":
				dmg = max(dmg - self.get_stat("magie"), 0)
				relevant.append(f'magie {self.get_stat("magie")}')

			if damage_type in self.body["resistances"]:
				r = self.body["resistances"][damage_type]
				if not (-1 <= r <= 1):
					self.cPrint("Warning! Resistance is not in interval <-100%, 100%>!\n")
				dmg_mult *= (1 - r)
				relevant.append(f"resistance to {damage_type} {int(100 * r)}%")

			if not(caused_by_effect) and self.turned_by_into(damage_type.upper()):
				dmg_mult *= 0.5
				relevant.append("removed effect 50%")
				self.cPrint("Rule (off screen): Nevýhoda na kostku.\n")

		return (dmg * dmg_mult, ", ".join(relevant))

	# EFFECTS
	def get_effect_string(self, effect, sub_value=None):
		if sub_value != None:
			value = sub_value
		else:
			value = effect["value"]

		if value:
			if effect["type"] == "dice":
				str_duration = f" (D{value})"
			elif effect["type"] == "duration":
				str_duration = f" (for {value} turns)"
			else:
				raise  # the programer screwed up!
		else:
			str_duration = ""

		if "on_print" in effect:
			return f'{effect["on_print"]}{str_duration}'
		elif effect["type"] == "duration":
			return f'{effect["name"]}{str_duration}'
		elif effect["type"] == "dice":
			return f'{effect["name"]}ing{str_duration}'
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
			self.cPrint(f'{self} is immune to {effect["name"]} because they are {self.get_effect_string(immunity_by)}\n')
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
			if (old_effect := self.get_effect(effect["name"])):  # the refreshment
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

		self.cPrint(f"{self} is {self.get_effect_string(effect)} now{extra_comment}\n")

		# Remove effects that entity is now immune to
		if "prevents" in effect:
			self.remove_effects(effect["prevents"])

	def add_effects(self, effects):
		for effect, value in effects:
			effect = get_library("effects", effect)
			self.add_effect(effect, value)

	def remove_effects(self, flags):
		i = 0
		while i < len(self.body["effects"]):
			effect = self.body["effects"][i]
			if effect["name"] in flags:
				self.cPrint(f"{self} is no longer {self.get_effect_string(effect)}\n")
				del self.body["effects"][i]
			else:
				i += 1

	def remove_effects_by_index(self, indexes):
		string = f"{self} is no longer:\n"
		for index in sorted(indexes, reverse=True):
			if index < len(self.body["effects"]):
				string += f'\t{self.get_effect_string(self.body["effects"][index])}\n'
				del self.body["effects"][index]
			else:
				raise DnDException(f"{index} is too much!")
		if indexes:
			self.cPrint(string)
		else:
			self.cPrint("Nothing removed.\n")

	def apply_effects(self):
		i = 0
		effects = self.body["effects"]
		while i < len(effects):
			effect = effects[i]

			if effect["name"] in {"FIRE", "BLEED"}:
				threw = D(effect["value"])
				self.damaged((({"true"}, threw),), ("burns for" if effect["name"] == "FIRE" else "bleeds for"), caused_by_effect=True)
				if threw == 1:
					self.cPrint(f"\tand stopped {self.get_effect_string(effect)}\n")
					del effects[i]
					continue

			if effect["type"] == "duration":
				effect["value"] -= 1
				if effect["value"] == 0:
					self.cPrint(f"{self} is no longer {self.get_effect_string(effect)}\n")
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
						effect = get_library("effects", effect)
						into_str = self.get_effect_string(effect, value)
					else:
						into_str = "nothing"

					self.cPrint(f"{self}'s {original} turns into {into_str} by {flag}\n")
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
				l = len(self.body["inventory"])
				raise DnDException(
					f"There are only {l} (indexes from 0 to {l-1}) items in inventory. Invalid index {cmd}.")
		else:
			chosen_item = None
			for i, item in enumerate(self.body["inventory"]):
				if item["derived_from"] == cmd:
					if chosen_item == None:
						chosen_item = item
						chosen_i = i
					else:
						raise DnDException(f"There are more items derived_from {cmd}, please use index notation.")
			if chosen_item == None:
				raise DnDException(f"Item {cmd} not found in {self}'s inventory.")
		return (chosen_i, self.body["inventory"][chosen_i])

	def put_item_into_inventory(self, item):
		self.body["inventory"].append(copy(item))
		self.cPrint(f"{item} is now in {self}'s inventory.\n")

	def remove_item_from_inventory(self, cmd):
		item_i, item = self.get_item(cmd)
		self.cPrint(f"{item} vanished from {self}'s inventory.\n")
		del self.body["inventory"][item_i]

	def set_inventory_item(self, cmd, key, value):
		item_i, item = self.get_item(cmd)
		self.body["inventory"][item_i][key] = value
		self.cPrint(f"{self}'s item now reads: {item}.\n")
