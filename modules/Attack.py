from library.Main import library

from modules.DnDException import DnDException
from modules.Misc import calculate

class Attack():
	"Call to attack"
	def __init__(self, Connector, attacker, attack_str, targets):
		if "attacks" not in attacker.body:
			raise DnDException(f"{attacker} nows no attacks.")
		self.C = Connector
		self.attacker = attacker
		self.targets = targets
		self.remove_effects = set()
		self.heal_list = []
		self.effect_list = []
		self.damage_list = []
		self.attack(attack_str, first_iteration=True)

		if self.remove_effects:
			for target in targets:
				target.remove_effects(self.remove_effects)
		if self.heal_list:
			for heal_for in self.heal_list:
				for target in self.targets:
					target.healed(heal_for)
		if self.effect_list:
			for target in self.targets:
				target.add_effects(self.effect_list)
		if self.damage_list:
			for target in self.targets:
				target.damaged(self.damage_list)

	def add_stuff(self, action, body, attack_str):
		"return False if no categry found"
		if action == "add_attack":
			self.attack(body, first_iteration=False)
		elif action == "add_effects":
			self.effect_list.extend(body)
		elif action == "print":
			self.C.Print(f"{body} (printed by {self.attacker}'s attack '{attack_str}').\n")
		else:
			return False
		return True

	def attack(self, attack_str, first_iteration):
		attack = self.get_attack(attack_str)
		for action, body in attack.items():
			if action == "mana_consumption":
				if not first_iteration:
					raise DnDException(
						"Attack was added by 'add_attack' and has mana_consumption. This is not supported.")
				mana_cost = (body.get("base", 0)
					+ body.get("per_target", 0) * len(self.targets))

				if self.attacker.get_stat("mana") >= mana_cost:
					self.attacker.body["mana"] -= mana_cost
				else:
					raise DnDException(
						f"{self.attacker} does not have enought mana for {attack_str}, it requires {mana_cost}.\n")

			elif action == "removes":
				self.remove_effects.update(body)

			elif action == "heal":
				self.heal_list.append(calculate(self.C.Dice.dice_eval(self.skill_eval(body))[0]))

			elif action == "dmg":
				damage_list, crits = self.C.Dice.parse_damage(self.skill_eval(body))
				self.damage_list.extend(damage_list)
				for c in crits:
					if not ("on_crit" in attack and c in attack["on_crit"]):
						raise DnDException(
							f"{self.attacker}'s attack {attack_str} doesn't have 'on_crit' for dice marked '{c}',"
							"which just critted.")
					if not self.add_stuff(*attack["on_crit"][c], attack_str):
						raise DnDException(
							f"{self.attacker}'s attack {attack_str} critted on dice marked '{c}',"
							f" but action {attack['on_crit'][c][0]} is undefined!")

			elif action in {"on_crit", "reaction"}:
				pass

			elif not self.add_stuff(action, body, attack_str):
				raise DnDException(f"{self.attacker}'s {attack_str}'s action '{action}' is undefined!")

	def get_attack(self, attack_str):
		if attack_str in self.attacker.body["attacks"]:
			return self.attacker.body["attacks"][attack_str]
		else:
			raise DnDException(f"Entity {self.attacker} does not know '{attack_str}'.")

	def skill_eval(self, string):
		"Goes through library.skills and replaces occurances in string with skill value."
		for skill in library["skills"]:
			if skill in string:
				string = string.replace(skill, str(self.attacker.get_stat(skill)))
		return string
