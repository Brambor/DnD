from random import randint
from modules.DnDException import DnDException


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

def dice_parser(expression):
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
		if cube == "":
			raise DnDException("'d' must be directly, withou spaces, followed by number of sides.")
		else:
			dice.append(int(cube))
	return dice

def dice_stat(n):
	if n >= 8:
		return D(20) + n - 8
	elif n < 0:
		return 0
	return D(list(all_dice)[n])

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
