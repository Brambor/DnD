from copy import deepcopy
import os
import pickle

from library.Main import library

from modules.Entity import Entity
from modules.Dice import D, dice_crit
from modules.DnDException import DnDException
from modules.Misc import get_valid_filename


class Game():
	def __init__(self, Connector):
		self.C = Connector
		self.i_entity = 0
		self.i_turn = 0
		self.entities = []
		self.entities_history = [[]]
		self.entities_history_pointer = 0
		self.save_file_associated = None

	def create(self, entity, nickname=""):
		e = Entity(self.C, library["entities"][entity], self.i_entity)
		if nickname != "":
			e.set_nickname(nickname)
		self.i_entity += 1
		self.entities.append(e)
		return e

	def erase(self, entities):
		changes = ""
		errors = ""
		for e in entities:
			try:
				entity_i, entity = self.get_entity(e)
			except DnDException as e:
				errors += f"?!: {e}\n"
				continue
			del self.entities[entity_i]
			changes += f"Entity {entity} has been deleted.\n"

		if changes:
			self.C.Print(f"{changes}\n{errors}")
		elif errors:
			self.C.Print(errors)

	def turn(self):
		for e in self.entities:
			e.apply_effects()
		self.C.Print("Turn %d\n" % self.i_turn)
		if all(e.played_this_turn for e in self.entities):
			for e in self.entities:
				e.played_this_turn = False
			self.C.Print("All entities played. New round!\n")
		self.i_turn += 1

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

	def get_entity_by_id(self, i_id):
		"for nonexistant returns None"
		for e in self.entities:  # bin search would be faster
			if e.id == i_id:
				return e

	def throw_dice(self, dice_list):
		"""throws die in list, prints results
		returns tuple of
		\t0: list of sets (set)((int) threw, (bool)crit)
		\t1: set of marked die (marks only), that crit"""
		threw_crit = []
		crits = set()
		for n, mark in dice_list:
			threw = D(n)
			if (crit := dice_crit(n, threw)) and mark:
				crits.add(mark)
			threw_crit.append((threw, crit))
		if (complete_string := "".join('{0: <4}'.format(mark) for _, mark in dice_list) + "\n").isspace():
			complete_string = ""
		complete_string += "".join('D{0: <3}'.format(n) for n, _ in dice_list) + "\n"
		complete_string += "".join(
				'{1}{0: <3}'.format(threw, "!" if crit else " ") for threw, crit in threw_crit
		) + "\n"
		self.C.Print(complete_string)
		return threw_crit, crits

	# ENTITY HISTORY
	def history_add(self):
		if (self.entities_history_pointer +1 < len(self.entities_history)):
			del self.entities_history[self.entities_history_pointer+1 :]
		for e in self.entities:
			e.C = None
		self.entities_history.append(deepcopy(self.entities))
		for e in self.entities:
			e.C = self.C
		self.entities_history_pointer += 1

	def history_move(self, move_in_history):
		"move_in_history is typically +1 or -1"
		if 0 <= self.entities_history_pointer + move_in_history < len(self.entities_history):
			self.entities_history_pointer += move_in_history
			self.entities = deepcopy(self.entities_history[self.entities_history_pointer])
			for e in self.entities:
				e.C = self.C
		else:
			self.C.Print("At history boundary.\n")
		self.C.Print.refresh_windows()

	# SAVE / LOAD
	def save(self, file_name=None):
		saves_path = f'{self.C.path_to_DnD}/saves'

		if file_name in {"test_save_A", "test_save_B"}:
			self.C.Print(f"WARNING: '{file_name}' is rewritten on each run of 'test/test_save.py', do not use it!\n")
		elif file_name == None:
			if self.save_file_associated == None:
				raise DnDException(f"No save file is yet asscociated with this game.")
			file_name = self.save_file_associated
		if file_name != get_valid_filename(file_name):
			raise DnDException(f"'{file_name}' is not a valid filename.")

		save_path = f'{saves_path}/{file_name}.pickle'

		if file_name != self.save_file_associated and os.path.exists(save_path):
			self.C.Print("Saving overwrote non asscociated file!\n")
			# add date to save

		big_d = {key: self.__dict__[key] for key in self.__dict__ if key not in {"save_file_associated", "C"}}
		for e in big_d["entities"]:
			e.__dict__ = {key:e.__dict__[key] for key in e.__dict__ if key != "C"}

		if not os.path.exists(saves_path):
			os.mkdir(saves_path)
		with open((save_path), "wb") as save_file:
			pickle.dump(big_d, save_file)
		self.save_file_associated = file_name
		self.C.Print(f"Saved as '{file_name}'.\n")

	def load(self, file_name):
		save_path = f'{self.C.path_to_DnD}/saves/{file_name}.pickle'
		if not os.path.exists(save_path):
			raise DnDException(f"Save file '{file_name}' does not exist.")
		# warn, then load
		with open(save_path, "rb") as save_file:
			big_d = pickle.load(save_file)
		big_d["C"] = self.C
		for e in big_d["entities"]:
			e.C = self.C
		self.__dict__ = big_d
		self.save_file_associated = file_name
		self.C.Print(f"File '{file_name}' loaded.\n")

	def list_saves(self):
		saves_path = f'{self.C.path_to_DnD}/saves'
		self.C.Print("\n".join(f[:-7] for f in os.listdir(saves_path)) + "\n")

	def delete(self, file_name):
		save_path = f'{self.C.path_to_DnD}/saves/{file_name}.pickle'
		if not os.path.exists(save_path):
			raise DnDException(f"Save file '{file_name}' does not exist.")
		os.remove(save_path)
		if self.save_file_associated == file_name:
			self.save_file_associated = None
			self.C.Print(f"This game was associated with '{file_name}', so it is no longer associated.\n")
		self.C.Print(f"Save '{file_name}' deleted.\n")
