from copy import deepcopy
import os
import pickle

from library.Main import library

from modules.Entity import Entity
from modules.DnDException import DnDException
from modules.Misc import get_now_str, get_valid_filename, pretty_print_filename, remove_date_from_filename
from modules.SettingsLoader import settings


class Game():
	def __init__(self, Connector):
		self.C = Connector
		self.i_entity = 0
		self.i_turn = 0
		self.entities = []
		self.entities_history = [[]]
		self.entities_history_pointer = 0
		self.save_file_associated = None
		self.autosave_slot = 0

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

		if changes and errors:
			self.C.Print(f"{changes}\n{errors}")
		elif changes:
			self.C.Print(changes)
		elif errors:
			self.C.Print(errors)

	def turn(self):
		for e in self.entities:
			e.apply_effects()
		self.C.Print(f"Turn {self.i_turn}\n")
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
			raise DnDException(f"Entity with id '{nickname}' does not exist.")
		else:
			for i, e in enumerate(self.entities):
				if e.nickname == nickname:
					return (i, e)
			raise DnDException(f"Entity '{nickname}' does not exist.")

	def get_entity_by_id(self, i_id):
		"for nonexistant returns None"
		for e in self.entities:  # bin search would be faster
			if e.id == i_id:
				return e

	def throw_dice(self, dice_list):
		"""throws die in list, prints results
		dice_list contains ((int)die, (str)mark), if mark is unimportant, mark should be ""
		returns tuple of
		\t0: list of sets (set)((int) threw, (bool)crit)
		\t1: set of marked die (marks only), that crit"""
		threw_crit = []
		crits = set()
		for n, mark in dice_list:
			threw = self.C.Dice.D(n)
			if (crit := self.C.Dice.dice_crit(n, threw)) and mark:
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
			del e.C
		self.entities_history.append(deepcopy(self.entities))
		for e in self.entities:
			e.C = self.C

		self.entities_history_pointer += 1
		self.autosave()

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
	def autosave(self):
		if settings.AUTOSAVE_SLOT_COUNT <= 0:
			return
		self.save(f"autosave_{self.autosave_slot}", autosave=True)
		self.autosave_slot = (self.autosave_slot+1) % settings.AUTOSAVE_SLOT_COUNT

	def delete(self, filename):
		filename_date = self.get_the_one_save_filename(filename)
		# warning
		if (ans := self.C.Input(
				f"Are you sure you wanna delete '{filename}'? 'yes'")) != "yes":
			raise DnDException(f"Wrote '{ans}' not 'yes', Aborting deleting '{filename}'.")

		os.remove(f"{self.C.path_to_DnD}/saves/{filename_date}.pickle")
		if self.save_file_associated == filename:
			self.save_file_associated = None
			self.C.Print(f"This game was associated with '{filename}', so it is no longer associated.\n")
		self.C.Print(f"Save '{filename}' deleted.\n")

	def get_the_one_save_filename(self, filename):
		saved_filenames = tuple(self.list_same_filenames(filename))
		if len(saved_filenames) == 0:
			raise DnDException(f"Save file '{filename}' does not exist.")
		elif len(saved_filenames) > 1:
			raise DnDException((
				f"Save file '{filename}' has {len(saved_filenames)} different saves associated.\n"
				f"Go to '{self.C.path_to_DnD}/saves/' and fix this problem (rename some)"
				f", then you can load & delete '{filename}'."))
		return saved_filenames[0]

	def list_same_filenames(self, filename, remove_date=False):
		saves_path = f'{self.C.path_to_DnD}/saves'
		if not os.path.exists(saves_path):
			return tuple()
		for saved_filename in (f[:-7] for f in os.listdir(saves_path)):
			if remove_date_from_filename(saved_filename) == filename:
				if remove_date:
					yield remove_date_from_filename(saved_filename)
				else:
					yield saved_filename

	def list_saves(self):
		saves_path = f'{self.C.path_to_DnD}/saves'
		if os.path.exists(saves_path) and os.listdir(saves_path):
			self.C.Print("\n".join(
				pretty_print_filename(f[:-7]) for f in os.listdir(saves_path)
			) + "\n")
		else:
			self.C.Print("No saved files yet.\n")

	def load(self, filename):
		filename_date = self.get_the_one_save_filename(filename)
		# warn
		if (ans := self.C.Input((f"Are you sure you wanna load '{filename}'? "
				"All current progress will be lost! 'yes'"))) != "yes":
			raise DnDException(f"Wrote '{ans}' not 'yes', Aborting loading '{filename}'.")
		# load
		with open(f"{self.C.path_to_DnD}/saves/{filename_date}.pickle", "rb") as save_file:
			big_d = pickle.load(save_file)

		C, ASS, AFS = self.C, self.autosave_slot, self.save_file_associated
		self.__dict__ = big_d
		for e in self.entities:
			e.C = C
		self.C, self.autosave_slot = C, ASS

		if filename[:9] == "autosave_" and filename[9:].isdigit():
			self.C.Print(f"File not associated, since {filename} is an autosave. Still associated to {AFS}.\n")
			self.save_file_associated = AFS
		else:
			self.save_file_associated = filename
		self.C.Print(f"File '{filename}' loaded.\n")

	def save(self, filename=None, autosave=False):
		saves_path = f'{self.C.path_to_DnD}/saves'

		if filename in {"test_save_A", "test_save_B"}:
			self.C.Print((f"WARNING: '{filename}' is rewritten and then deleted "
				"on each run of 'test/test_save.py', do not use it!\n"))
		elif filename == None:
			if self.save_file_associated == None:
				raise DnDException(f"No save file is yet asscociated with this game.")
			filename = self.save_file_associated
		if not autosave and filename[:9] == "autosave_" and filename[9:].isdigit():
			self.C.Print(f"WARNING: '{filename}' is overwritten on autosave, do not use it!\n")
		if filename != get_valid_filename(filename):
			raise DnDException(f"'{filename}' is not a valid filename.")

		if autosave:
			pass
		elif filename != self.save_file_associated and filename in self.list_same_filenames(filename, remove_date=True):
			self.C.Print("Saving overwrote non asscociated file!\n")
			new_file = ""
		elif filename == self.save_file_associated:
			new_file = ""
		else:
			new_file = " (new file)"

		C, SFA, ASS = self.C, self.save_file_associated, self.autosave_slot
		del self.C, self.save_file_associated, self.autosave_slot
		for e in self.entities:
			del e.C
		big_d = deepcopy(self.__dict__)
		for e in self.entities:
			e.C = C
		self.C, self.save_file_associated, self.autosave_slot = C, SFA, ASS

		if not os.path.exists(saves_path):
			os.mkdir(saves_path)
		# delete all old save files, if they exist
		for old_filename in self.list_same_filenames(filename):
			os.remove(f"{saves_path}/{old_filename}.pickle")
		# write file
		with open(f'{saves_path}/{filename}--{get_now_str()}.pickle', "wb") as save_file:
			pickle.dump(big_d, save_file)
		if not autosave:
			self.save_file_associated = filename
			self.C.Print(f"Saved as '{filename}'{new_file}.\n")
