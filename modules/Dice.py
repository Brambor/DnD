from random import randint
from modules.DnDException import DnDException


def dice_stat(n):
	if n >= 5:
		return D(20)
	elif n < 0:
		return D(4)
	return D([4, 6, 8, 10, 12][n])

def D(n):
	return randint(1, n)

def dice_which(n):
	if n not in all_dice:
		raise DnDException("Dice %d doesn't exist. Existing die: %s." % (n, ", ".join(str(k) for k in all_dice.keys())))
	return all_dice[n]

def dice_crit(dice, threw, cPrint):
	if dice - threw <= dice_which(dice):
		cPrint("Critical on D%d!!\n" % dice)
		return True
	else:
		return False

all_dice = {
	4: 0,
	6: 1,
	8: 2,
	10: 3,
	12: 4,
	20: 5,
}
