from modules.Entity import Entity
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
			if nickname.isdigit():
				raise DnDException("Nickname cannot be an integer!")
			elif " " in nickname:
				raise DnDException("Nickname cannot contain space ' '!")
			elif nickname in (ent.nickname for ent in self.entities):
				ent = self.get_entity(nickname)
				raise DnDException("Nickname is already in use by %s" % ent)
			else:
				e.nickname = nickname
		self.i += 1
		self.entities.append(e)
		return e

	def turn(self):
		self.cPrint("Turn %d" % self.i_turn)
		i = 0
		while i < len(self.entities):
			e = self.entities[i]
			e.apply_effects()
			if not e.alive():
				del self.entities[i]
			else:
				i += 1
		self.i_turn += 1

	def get_entity(self, nickname):
		if nickname.isdigit():
			return self.entities[int(nickname)]
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
