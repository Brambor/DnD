from random import randint
from modules.DnDException import DnDException


def dice_stat(n):
	if n >= 8:
		return D(20)
	elif n < 0:
		return D(4)
	return D(list(all_dice)[n])

def D(n):
	return randint(1, n)

def dice_crit(dice, threw, cPrint):
	check_dice_exists(dice)
	if threw >= all_dice[dice]:
		cPrint("Critical on D%d!!\n" % dice)
		return True
	else:
		return False

def check_dice_exists(n):
	if n not in all_dice:
		raise DnDException("Dice %d doesn't exist. Existing die: %s." % (n, ", ".join(str(d) for d in all_dice)))

# dice : since which n does it crit
all_dice = {
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
