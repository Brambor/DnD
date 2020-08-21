from random import randint

from modules.DnDException import DnDException
from modules.Misc import calculate

from library.Main import library


class Dice():
	def __init__(self, C):
		self.C = C
		# dice : since which n does it crit
		self.all_dice = {
			4: 4,
			6: 5,
			8: 7,
			10: 8,
			12: 10,
			14: 11,
			16: 13,
			18: 14,
			20: 15,
		}

	def D(self, n):
		return randint(1, n)

	def dice_crit(self, dice, threw, print_crit=False):
		"pass arg. cPrint to print when crit"
		self.check_dice_exists(dice)
		if threw >= self.all_dice[dice] and print_crit:
			self.C.Print(f"Critical on D{dice}!!\n")
		return threw >= self.all_dice[dice]

	def check_dice_exists(self, n):
		if n not in self.all_dice:
			raise DnDException(f"Dice {n} doesn't exist. Existing die: {', '.join(str(d) for d in self.all_dice)}.")

	def dice_eval(self, expression):
		if (dice := self.dice_parser(expression)):
			threw_crit, crits = self.C.Game.throw_dice(dice)
			# put the results back into the expression
			for n_m, threw in zip(dice, threw_crit):
				expression = expression.replace(f"d{n_m[0]}{n_m[1]}", str(threw[0]), 1)
			return expression, crits
		return expression, set()

	def dice_parser(self, expression):
		dice = []
		i = expression.find("d")
		while i != -1:
			i = expression.find("d", i) + 1
			if i == 0:
				break
			cube = ""
			for ch in expression[i:]:
				if ch.isdigit():
					cube += ch
					i += 1
					continue
				break
			mark = ""
			for ch in expression[i:]:
				if ch.isalpha():
					mark += ch
					i += 1
					continue
				break
			if cube:
				dice.append((int(cube), mark))
		return dice

	def dice_stat(self, n):
		if n >= 8:
			return self.D(20) + n - 8
		elif n < 0:
			return 0
		return self.D(list(self.all_dice)[n])

	def get_int_from_dice(self, n_str):
		if n_str.replace("-", "", 1).isdigit():
			return int(n_str)
		elif n_str.startswith("d") and n_str[1:].isdigit():
			return self.D(int(n_str[1:]))
		raise DnDException("'%s' is not an integer nor in format 'dx'." % n_str)

	def parse_damage(self, string):
		"string = 'physical acid {7*d20} acid {7 + d4} acid { d12}'"
		"returns [{'physical', 'acid'}: 14, {'acid'}: 8, {'acid'}: 5]"
		damage_list = []
		crits = set()
		for whole in (type_damage.split("{") for type_damage in string.split("}") if type_damage != ""):
			if len(whole) != 2:
				raise DnDException("%s is %d long, 2 expected.\nMaybe you forgot '{' ?" % (whole, len(whole)))

			types = set()
			for damage_type in whole[0].strip().split():
				if damage_type not in library["damage_types"]:
					raise DnDException("Invalid damage_type '%s'." % damage_type)
				types.add(library["damage_types"][damage_type])  # a -> acid; acid -> acid	

			whole[1], c = self.dice_eval(whole[1])
			crits.update(c)

			# calculate
			damage_list.append((types, calculate(whole[1])))
		return damage_list, crits
