# Dice.py

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

def dice_parser(expression):
	"returns list [(2, None), (8, 'a')]"
	dice = []
	i = expression.find("d")
	while i != -1:
		# find the next d
		i = expression.find("d", i) + 1
		if i == 0:
			break
		# read number
		cube = ""
		for c in expression[i:]:
			if c.isdigit():
				cube += c
				i += 1
				continue
			break
		# read optional mark
		mark = ""
		for c in expression[i:]:
			if c.isspace():
				break
			mark += c
			i += 1
		# checks
		if cube == "":
			raise DnDException("'d' must be directly, withou spaces, followed by number of sides.")
		dice.append((int(cube), mark))
	return dice

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


# end Dice.py








def list_2d_to_table(list_2d, header, char_set=None):
	""" 
	┌──┬────────────┐
	│O.│Název cesty │
	├──┼────────────┤
	│8c│Pučmeloun   │
	│7a│Modrá jablka│
	│6b│Zelená Madla│
	└──┴────────────┘"""
	if char_set == None: 
		s = {
			"│": "│",
			"┬": "┬",
			"─": "─",
		}
	else:
		s = char_set

	listdelek = []
	for column in range(len(header)):
		maxdelka = len(header[column])
		for line in list_2d:
			delka = len(line[column])
			maxdelka = max(delka, maxdelka)
		listdelek.append(maxdelka)

	table = "┌%s┐\n" % s["┬"].join(s["─"] * d for d in listdelek)

	table += s["│"]
	separator = ""
	for delka, cell in zip(listdelek, header):
		table += separator
		table += ("%%-%ds" % delka) % cell 
		separator = "│"
	table += "│\n"

	table += "├%s┤\n" % "┼".join(s["─"] * d for d in listdelek)

	table += s["│"]
	separator = ""
	for row in list_2d:
		for cell, delka in zip(row, listdelek):
			table += separator	
			table += ("%%-%ds" % delka) % cell
			separator = "│"
		table += s["│"]
		table += "\n"

	table += "└%s┘\n" % "┴".join(s["─"] * d for d in listdelek)	
	return table


def throw_dice_false(dice_list, tuples=False):
	"throws die in list, prints results and returns list of sets (set)((int) threw, (bool)crit)"
	"tuples=False: dice_list is list of integers"
	"tuples=False: dice_list is list of tuples ( (int)dice, (None/str)mark )"
	threw_crit = []
	for n in dice_list:
		threw = D(n)
		crit = dice_crit(n, threw, print)
		threw_crit.append((threw, crit))
	complete_string = "".join('D{0: <4}'.format(n) for n in dice_list) + "\n"
	complete_string += "".join(
			'{1}{0: <4}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
	) + "\n"
	print(complete_string)
	return threw_crit



def throw_dice_true(dice_list, tuples=False):
	"throws die in list, prints results and returns list of sets (set)((int) threw, (bool)crit)"
	"tuples=False: dice_list is list of integers"
	"tuples=False: dice_list is list of tuples ( (int)dice, (None/str)mark )"
	threw_crit = []
	crit_set = set()
	for n_mark in dice_list:
		n = n_mark[0]
		threw = D(n)
		crit = dice_crit(n, threw, print)
		if crit and n_mark[1] != None:
			crit_set.add(n_mark[1])
		threw_crit.append((threw, crit))
	complete_string = "".join('D{0: <4}'.format("%d%s" % (n[0], n[1])) for n in dice_list) + "\n"
	complete_string = "".join('D{0: <4}'.format(n[0]) for n in dice_list) + "\n"
	complete_string += "".join(
			'{1}{0: <4}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
	) + "\n"
	print(complete_string)
	return (threw_crit, crit_set)


dice = dice_parser("50 + d6a + d10b")
print("dice:", dice)

print("threw_dice:", throw_dice_true(dice, tuples=True))


print()
