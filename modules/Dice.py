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

	def D(self, n, message="", show_result=False):
		while self.C.Game.manual_dice:
			if (d := self.C.Input(f"{message + ' ' if message else ''}D{n} or '[inter]rupt'")).isdigit():
				if 1 <= int(d) <= n:
					return int(d)
				self.C.Print(f"1 <= {d} <= {n} must be true.\n")
			elif d in {"inter", "interrupt"}:
				raise DnDException("Throwing interrupted.")
			else:
				self.C.Print(f"'{d}' must be integer and 1 <= {d} <= {n} must be true.\n")
		# not manual
		d = randint(1, n)
		if show_result:
			self.C.Print(f'Threw {d}{" (crit)" if self.dice_crit(n, d) else ""} on D{n}.\n')
		return d

	def dice_crit(self, dice, threw, print_crit=False):
		self.check_dice_exists(dice)
		if threw >= self.all_dice[dice] and print_crit:
			self.C.Print(f"Critical on D{dice}!!\n")
		return threw >= self.all_dice[dice]

	def check_dice_exists(self, n):
		if n not in self.all_dice:
			raise DnDException(f"Dice {n} doesn't exist. Existing die: {', '.join(str(d) for d in self.all_dice)}.")

	def dice_eval(self, expression):
		"""
		evaulate dice in 'expression' by throwing

		return string containing throw results
		"""
		if (dice := self.dice_parser(expression)):
			threw_crit, crits = self.throw_dice(dice)
			# put the results back into the expression
			for n_m, threw in zip(dice, threw_crit):
				expression = expression.replace(f"{'V' if n_m[2] else ''}d{n_m[0]}{n_m[1]}", str(threw[0]), 1)
			return expression, crits
		return expression, set()

	def dice_parser(self, expression):
		"""
		find occurances of "(V)*d{X}{M}" in 'expression', where
		(V*) is optional, presence indicateadvantage
		{X} is a natural integer
		{M} is mark/name of dice

		return (list)((int)dice, (str)mark, (bool)advantage)
		"""
		dice = []

		i = 0
		while i < len(expression):
			advantage = 0
			while True:
				s = expression[i].upper()
				if s == "V":
					advantage += 1
				elif s == "N":
					advantage -= 1
				else:
					break
				i += 1
			
			# not d? skip this word!
			if expression[i] == "d":
				i += 1
			else:
				skip = True
			
			cube = ""
			while expression[i].isdigit():
				cube += expression[i]
				i += 1
			
			mark = ""
			while expression[i].isalpha():
				mark += expression[i]
				i += 1

			if cube and not skip:
				dice.append((int(cube), mark, advantage))
			# -1 nevyhoda, 0 nothing, 1 vyhoda
			# (future): VvVd6 vyhoda ze 4
			#           NNd20 nevyhoda ze 3

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
		raise DnDException(f"'{n_str}' is not an integer nor in format 'dx'.")

	def parse_damage(self, string):
		# should accept Vd20
		"""
		string = 'physical acid {7*d20} acid {7 + d4} acid { d12}'
		return [{'physical', 'acid'}: 14, {'acid'}: 8, {'acid'}: 5]
		"""
		damage_list = []
		crits = set()
		for whole in (type_damage.split("{") for type_damage in string.split("}") if type_damage != ""):
			if len(whole) != 2:
				raise DnDException(f"{whole} is {len(whole)} long, 2 expected.\nMaybe you forgot '{{' ?")

			types = set()
			for damage_type in whole[0].strip().split():
				if damage_type not in library["damage_types"]:
					raise DnDException(f"Invalid damage_type '{damage_type}'.")
				types.add(library["damage_types"][damage_type])  # a -> acid; acid -> acid	

			whole[1], c = self.dice_eval(whole[1])
			crits.update(c)

			# calculate
			damage_list.append((types, calculate(whole[1])))
		return damage_list, crits

	def print_dice_table(self, dice_list, threw_crit):
		# TODO print advantage (also pass that info)
		# <4 Jsem si vycucal z prstu, pro mark "abcde" nefunguje, pro "abcd" je hnusny
		if (complete_string := "".join('{0: <4}'.format(mark) for _, mark, _advantage in dice_list) + "\n").isspace():
			complete_string = ""
		complete_string += "".join('D{0: <3}'.format(n) for n, _, _advantage in dice_list) + "\n"
		complete_string += "".join(
				'{1}{0: <3}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
		) + "\n"
		return complete_string

	def throw_dice(self, dice_list):
		"""throws die in list, prints results
		dice_list contains ((int)die, (str)mark), if mark is unimportant, mark should be ""
		returns tuple of
		\t0: list of sets (set)((int) threw, (bool)crit)
		\t1: set of marked die (marks only), that crit"""
		threw_crit = []
		crits = set()
		for n, mark, advantage in dice_list:
			if advantage:
				#self.C.Print(f"Threw {a}, {b} for advantage.\n")
				threw = max(self.D(n), self.D(n))
			else:
				threw = self.D(n)
			if (crit := self.dice_crit(n, threw)) and mark:
				crits.add(mark)
			threw_crit.append((threw, crit))
		self.C.Print(self.print_dice_table(dice_list, threw_crit))
		return threw_crit, crits
