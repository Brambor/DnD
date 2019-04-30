from modules.Dice import D, dice_crit
from modules.DnDException import DnDException
from modules.Misc import parse_sequence, yield_valid


class Fist():
	def __init__(self, dmg, dice):
		self.dmg = dmg
		self.dice = dice

	def __str__(self):
		return "type: fist; dmg: %d, dice: %d" % (self.dmg, self.dice)

	def use(self, cInput, cPrint):  # cPrint unused
		"cInput - False/None: automatic throwing; <cInput object>: input the sequence"
		# will throw (or more importantly, write in the threwed) only once
		if cInput:
			threw = next(parse_sequence(cInput("(using %s)\nthrew >>>" % self)))
		else:
			threw =  D(self.dice)
		return self.dmg + threw


class Axe():
	def __init__(self, dmg, dice, crit_dice=6):
		self.dmg = dmg
		self.dice = dice
		self.crit_dice = crit_dice

	def __str__(self):
		return "type: axe; dmg: %d, dice: %d, crit_dice: %d" % (self.dmg, self.dice, self.crit_dice)

	def use(self, cInput, cPrint):
		if cInput:
			threw_sequence = parse_sequence(cInput("(using %s)\nthrew >>>" % self), carry_when_crit=True)
			threw = yield_valid(threw_sequence)
		else:
			threw_sequence = None
			threw = D(self.dice)
		total_dmg = self.dmg + threw
		if dice_crit(self.dice, threw, cPrint):
			total_dmg += self.axe_crit(threw_sequence, cPrint)
		if threw_sequence:
			if "Perfectly right lenght." != next(threw_sequence):
				raise DnDException("Sequence was too long!")
		return total_dmg

	def axe_crit(self, threw_sequence, cPrint):
		if threw_sequence:
			threw = yield_valid(threw_sequence)
		else:
			threw = D(self.crit_dice)
		if dice_crit(self.crit_dice, threw, cPrint):
			threw += self.axe_crit(threw_sequence, cPrint)
		return threw
