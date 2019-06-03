from modules.Entity import Entity
from modules.Dice import D, dice_crit, dice_stat
from modules.DnDException import DnDException


class Game():
	def __init__(self, library, cPrint):
		self.i = 0
		self.i_turn = 0
		self.library = library["entities"]
		self.effects = library["effects"]
		self.spells = library["spells"]
		self.entities = []
		self.cPrint = cPrint

	def create(self, entity, nickname=""):
		e = Entity(self.library[entity], self.i, self)
		if nickname != "":
			e.set_nickname(nickname)
		self.i += 1
		self.entities.append(e)
		return e

	def turn(self):
		self.cPrint("Turn %d" % self.i_turn)
		for e in self.entities:
			e.apply_effects()
		self.i_turn += 1

	def get_entity(self, nickname):
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

	def get_spell(self, spell_name):
		for spell in self.spells:
			if spell == spell_name:
				return self.spells[spell]
		raise DnDException("Spell '%s' is not in library." % spell_name)


	def get_effect(self, effect_name):
		effect = self.effects.get(effect_name, None)
		if effect:
			return effect
		raise DnDException("Effect '%s' is not in library." % effect_name)

	def throw_dice(self, dice_list):
		"throws die in list, prints results and returns list of sets (set)((int) threw, (bool)crit)"
		threw_crit = []
		for n in dice_list:
			threw = D(n)
			crit = dice_crit(n, threw, self.cPrint)
			threw_crit.append((threw, crit))
		complete_string = "".join('D{0: <4}'.format(n) for n in dice_list)
		complete_string += "".join(
				'{1}{0: <4}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
		)
		self.cPrint(complete_string)
		return threw_crit
