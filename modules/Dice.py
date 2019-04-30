from random import randint


def dice_stat(n):
	if n >= 5:
		return D(20)
	return D([4, 6, 8, 10, 12][n])

def D(n):
	return randint(1, n)

def dice_which(n):
	return {
		4: 0,
		6: 1,
		8: 2,
		10: 3,
		12: 4,
		20: 5
	}[n]

def dice_crit(dice, threw, cPrint):
	if dice - threw <= dice_which(dice):
		cPrint("Critical on D%d!!" % dice)
		return True
	else:
		return False
