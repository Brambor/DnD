import os
import pickle

from modules.Entity import Entity
from modules.Dice import D, dice_crit
from modules.DnDException import DnDException
from modules.Misc import get_valid_filename


class Game():
	def __init__(self, library, cPrint, cCurses):
		self.i_entity = 0
		self.i_turn = 0
		self.library = library
		self.entities = []
		self.cPrint = cPrint
		self.cCurses = cCurses  # only for library of color usage used in Entity
		self.save_file_associated = None

	def create(self, entity, nickname=""):
		e = Entity(self.library["entities"][entity], self.i_entity, self)
		if nickname != "":
			e.set_nickname(nickname)
		self.i_entity += 1
		self.entities.append(e)
		return e

	def erase(self, cmd):
		entity_i, entity = self.get_entity(cmd)
		self.cPrint("Entity %s has been deleted.\n" % entity)
		self.cPrint.deselect_entity_inventory(entity)
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
		crits = set()
		for n, mark in dice_list:
			threw = D(n)
			if (crit := dice_crit(n, threw, self.cPrint)) and mark:
				crits.add(mark)
			threw_crit.append((threw, crit))
		if not (complete_string := "".join('{0: <4}'.format(mark) for _, mark in dice_list) + "\n").strip():
			complete_string = ""
		complete_string += "".join('D{0: <3}'.format(n) for n, _ in dice_list) + "\n"
		complete_string += "".join(
				'{1}{0: <3}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
		) + "\n"
		self.cPrint(complete_string)
		return threw_crit, crits

	# SAVE / LOAD
	def save(self, file_name=None):
		saves_path = f'{self.cPrint.path_to_DnD}/saves'

		if file_name in {"test_save_A", "test_save_B"}:
			self.cPrint(f"WARNING: '{file_name}' is rewritten on each run of 'test/test_save.py', do not use it!\n")
		elif file_name == None:
			if self.save_file_associated == None:
				raise DnDException(f"No save file is yet asscociated with this game.")
			file_name = self.save_file_associated
		if file_name != get_valid_filename(file_name):
			raise DnDException(f"'{file_name}' is not a valid filename.")

		save_path = f'{saves_path}/{file_name}.pickle'

		if file_name != self.save_file_associated and os.path.exists(save_path):
			self.cPrint("Saving overwrote non asscociated file!\n")
			# add date to save

		big_d = {key: self.__dict__[key] for key in self.__dict__ if key not in {"cCurses", "cPrint", "save_file_associated"}}
		for e in big_d["entities"]:
			e.__dict__ = {key:e.__dict__[key] for key in e.__dict__ if key not in {"game", "cPrint"}}

		if not os.path.exists(saves_path):
			os.mkdir(saves_path)
		with open((save_path), "wb") as save_file:
			pickle.dump(big_d, save_file)
		self.save_file_associated = file_name
		self.cPrint(f"Saved as '{file_name}'.\n")

	def load(self, file_name):
		save_path = f'{self.cPrint.path_to_DnD}/saves/{file_name}.pickle'
		if not os.path.exists(save_path):
			raise DnDException(f"Save file '{file_name}' does not exist.")
		# warn, then load
		with open(save_path, "rb") as save_file:
			big_d = pickle.load(save_file)
		big_d["cCurses"] = self.cCurses
		big_d["cPrint"] = self.cPrint
		for e in big_d["entities"]:
			e.game = self
			e.cPrint = self.cPrint
		self.cPrint.inventory_entity = None  # restarting to refresh
		self.__dict__ = big_d
		self.save_file_associated = file_name
		self.cPrint(f"File '{file_name}' loaded.\n")

	def list_saves(self):
		saves_path = f'{self.cPrint.path_to_DnD}/saves'
		self.cPrint("\n".join(f[:-7] for f in os.listdir(saves_path)) + "\n")

	def delete(self, file_name):
		save_path = f'{self.cPrint.path_to_DnD}/saves/{file_name}.pickle'
		if not os.path.exists(save_path):
			raise DnDException(f"Save file '{file_name}' does not exist.")
		os.remove(save_path)
		if self.save_file_associated == file_name:
			self.save_file_associated = None
			self.cPrint(f"This game was associated with '{file_name}', so it is no longer associated.\n")
		self.cPrint(f"Save '{file_name}' deleted.\n")
