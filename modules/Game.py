from modules.Entity import Entity
from modules.Dice import D, dice_crit, dice_stat
from modules.DnDException import DnDException


class Game():
	def __init__(self, library, cPrint, cCurses):
		self.i = 0
		self.i_turn = 0
		self.library = library
		self.entities = []
		self.cPrint = cPrint
		self.cCurses = cCurses  # only for library of color usage used in Entity

	def create(self, entity, nickname=""):
		e = Entity(self.library["entities"][entity], self.i, self)
		if nickname != "":
			e.set_nickname(nickname)
		self.i += 1
		self.entities.append(e)
		return e

	def turn(self):
		self.cPrint("Turn %d\n" % self.i_turn)
		for e in self.entities:
			e.apply_effects()
		self.i_turn += 1

	def get(self, library, thing):
		"getting things from self.library"
		if library not in self.library:
			raise DnDException("Unknown library '%s'." % library)
		else:
			ret = self.library[library].get(thing, None)
			if ret:
				return ret
			raise DnDException("'%s' is not in '%s' library." % (thing, library))

	def get_entity(self, nickname):
		"getting entities from self.entities"
		if nickname.isdigit():
			for e in self.entities:
				if e.id == int(nickname):
					return self.entities[int(nickname)]
			raise DnDException("Entity with id '%d' does not exist." % nickname)
		else:
			for e in self.entities:
				if e.nickname == nickname:
					return e
			raise DnDException("Entity '%s' does not exist." % nickname)

	def throw_dice(self, dice_list):
		"throws die in list, prints results and returns list of sets (set)((int) threw, (bool)crit)"
		threw_crit = []
		for n in dice_list:
			threw = D(n)
			crit = dice_crit(n, threw, self.cPrint)
			threw_crit.append((threw, crit))
		complete_string = "".join('D{0: <4}'.format(n) for n in dice_list) + "\n"
		complete_string += "".join(
				'{1}{0: <4}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
		) + "\n"
		self.cPrint(complete_string)
		return threw_crit
