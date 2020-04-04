from modules import DnDException

class WeaponUser():
	def __init__(self, game):
		self.weapons = []  # stack zbrani
		self.game = game
	def attack_with_weapon(self, weapon):
		self.weapons.append(weapon)
		self.weapon = weapon
		ret = self.use_weapon(weapon)
		# check ret
		return ret
	def use_weapon(self, weapon):
		dmg = weapon.get("basic_dmg", 0)
		for key in weapon.get("triggers_effects", set()):
			if key == "add_dmg_from_dice":
				dmg += add_dmg_from_dice_func(weapon[key])
			elif key == "add_dmg_from_key":
				dmg += add_dmg_from_key_func(weapon[key])
			elif key == "add_dmg_from_effect":
				dmg += add_dmg_from_effect_func(weapon[key])
			else:
				raise DnDException("In WeaponUser.use_weapon' undefined effect '%s'." % key)
		apply_effects = []
		return {
			"apply_effects": apply_effects,
			"dmg": dmg,
			}

def add_dmg_from_key_func(key):
	return self.key

def add_dmg_from_dice_func(dice):
	# check is dice
	return D(int(dice[1:]))

def add_dmg_from_effect_func(key):
	return self.key
