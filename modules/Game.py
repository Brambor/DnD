from copy import copy

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

	def erase(self, cmd):
		entity_i, entity = self.get_entity(cmd)
		self.cPrint("Entity %s has been deleted.\n" % entity)
		del self.entities[entity_i]

	def turn(self):
		for e in self.entities:
			e.apply_effects()
		self.cPrint("Turn %d\n" % self.i_turn)
		if all(e.played_this_turn for e in self.entities):
			for e in self.entities:
				e.played_this_turn = False
			self.cPrint("All entities played. New round!\n")
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
		"returns pair (i, entity) from self.entities; i is index in self.entities != id"
		if nickname.isdigit():
			for i, e in enumerate(self.entities):
				if e.id == int(nickname):
					return (i, e)
			raise DnDException("Entity with id '%d' does not exist." % int(nickname))
		else:
			for i, e in enumerate(self.entities):
				if e.nickname == nickname:
					return (i, e)
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

	def save_dict(self, the_dict=None):
		from modules.CustomPrint import CustomPrint
		from modules.CustomCurses import CustomCurses
		from modules.Weapons import Fist, Axe
		from modules.Entity import Entity
		if the_dict == None:
			the_dict = self.__dict__
		save = {}
		for key in the_dict:
			value = the_dict[key]
			if type(value) == dict:
				value = self.save_dict(value)
			if type(value) == list:
				value = self.save_list(value)
			print("key:", key, "value:", value)
			if type(value) in {CustomPrint, CustomCurses}:
				continue
			elif type(value) == Entity:
				value = self.save_dict(value.__dict__)
			save[key] = value
		return save
	def save_list(self, the_list):

		for item in the_list:
			pass

