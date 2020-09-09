from modules.Misc import calculate


keywords = {"body", "bottom", "top", "left", "right", "row", "column", "grid", "scrollnotok"}

"""
body
	the stream containing the whole window
[bottom top left right] expression out_1 out_2
	splits input to two streams
[row column] count out_1 out_2 ... out_count
	splits input to count streams
grid count_columns count_rows out_1 ... out_rows ... out_rows+1 ... out_rows*2 ... ... out_rows*columns
	splits input to count_columns * count_rows streams
	iterates over grid, column by column (not row by row), item by item in each column
scrollnotok window
	sets the following window to scrollok = False, so it doesn't scroll
"""

# TODO add functionality: after "body" finishes it's run, other windows can take control and be splitted as body was
# When "body" finished execution, it is removed. Don't require user to write "body", add it automatically.

def reverse_index(lst, value):
	i = len(lst) - 1
	while i >= 0:
		if lst[i] == value:
			return i
		i -= 1
	raise ValueError(f"'{value}' is not in the list.")

class Solver():
	def __init__(self, string, width, height):
		self.body = {
			"left": 0,
			"top": 0,
			"width": width,
			"height": height,
		}
		self.windows = {}
		self.words = self.into_words(string)
		if self.words[0] != "body":
			raise ValueError(f"Unfinished iteration i=0, your input={self.words}.")
		self.i = 1
		self.depth = 0
		self.splitted_depth = 0
		self.stack = ["body"]
		self.tree = []
		self.last_keyword = None
		self.solver(self.body)
		#assert((self.depth, self.splitted_depth) == (0, 0))
		print(f"ending depth: real={self.depth} splitted={self.splitted_depth}")
		if self.i != len(self.words):
			raise ValueError(f"Unfinished iteration i={self.i}, left from your input {self.words[self.i:]}.")

	def into_words(self, string):
		# remove comments, lines -> spaces
		out = " ".join(line.split("#")[0] for line in string.split("\n"))
		# tabs -> spaces
		out = " ".join(out.split("\t"))
		# break into individual words
		return out.strip().split()

	def calc_expression(self, expression, window):
		return int(calculate(expression.replace("x", str(window["width"])).replace("y", str(window["height"]))))
#		print("%s = %s" % (expression, ret))

	def solver(self, window):
		self.depth += 1
		self.splitted_depth += 1
		word = self.words_pp()
		self.stack.append(word)
		if word in keywords:
			self.last_keyword = word
			if word in {"top", "right", "bottom", "left"}:
				splitted_window = self.window_split_trbl(self.words_pp(), window, word)
				self.solver(splitted_window)
#				self.stack.pop()
				self.splitted_depth -= 1
				self.solver(window)
			elif word in {"column", "row"}:
				ratio = self.words_pp(give_ratio=True)
				count = len(ratio)
				splitted_windows = self.window_split_column_row(ratio, window, word)
				for splitted_window in splitted_windows:
					self.solver(splitted_window)
					count -= 1
					if count == 1:
#						self.stack.pop()
						self.splitted_depth -= 1
			elif word == "grid":
				columns, rows = int(self.words_pp()), int(self.words_pp())
				count = columns * rows
				for splitted_window_column in self.window_split_column_row(columns, window, "column"):
					for splitted_window in self.window_split_column_row(rows, splitted_window_column, "row"):
						self.solver(splitted_window)
						count -= 1
						if count == 1:
#							self.stack.pop()
							self.splitted_depth -= 1
			elif word == "scrollnotok":
				window["scrollok"] = False
				self.splitted_depth -= 1
#				self.stack.pop()
				self.solver(window)
			else:
				raise ValueError(f"Unknown keyword {word}.")

		else:
			if not(word.startswith('"') and word.endswith('"')):
				raise ValueError(f"Window name '{word}' doesn't start and end with '\"'.")
			self.windows[word.strip('"')] = window
			self.splitted_depth -= 1
		self.depth -= 1
		self.stack.pop()

	def words_pp(self, give_ratio=False):
		"if give_ratio, return list of ratios instead of a word"
		if self.i == len(self.words):
			msg = (f"Last keyword '{self.last_keyword}'; i={self.i} => iteration stopped at '{self.words[self.i-1]}' "
				f"in depth {self.depth} (splitted {self.splitted_depth}).\n"
				f"stack = {self.stack}\n")
			msg += self.tree_str()

			msg += f"Ran out of list! Probably unparsed: {self.words[reverse_index(self.words, self.last_keyword):]}.\n"

			raise IndexError(msg)
		if give_ratio:
			return self.pop_ratio()
		else:
			ret = self.words[self.i]
			self.i += 1
		return ret

	def pop_ratio(self):
		s = " ".join(self.words[self.i:])
		ratios = []
		intg = ""
		for used, ch in enumerate(s):
			if ch.isdigit():
				intg += ch
				continue
			if ch.isspace(): #maybe merge?
				continue
			if ch != ":":
				break
			ratios.append(int(intg))
			intg = ""
		else:
			s = ""
			used += 1
		if intg:
			ratios.append(int(intg))

		catch = 0
		for i, w in enumerate(self.words[self.i:]):
			if catch < used:
				catch += len(w) + 1  # +1 for join space
			else:
				self.i += i
				break
		else:
			self.i = len(self.words)
		return ratios

	def window_split_trbl(self, expression, window, from_direction):
		splitted_size = self.calc_expression(expression, window)
		splitted_window = window.copy()

		if from_direction == "left":
			splitted_window["width"] = splitted_size
			window["left"] += splitted_size
			window["width"] -= splitted_size
		elif from_direction == "right":
			splitted_window["width"] = splitted_size
			splitted_window["left"] = window["left"] + window["width"] - splitted_size
			window["width"] -= splitted_size
		elif from_direction == "top":
			splitted_window["height"] = splitted_size
			window["top"] += splitted_size
			window["height"] -= splitted_size
		elif from_direction == "bottom":
			splitted_window["height"] = splitted_size
			splitted_window["top"] = window["top"] + window["height"] - splitted_size
			window["height"] -= splitted_size
		else:
			raise ValueError(f'Unaceptable from_direction {from_direction}, it must be in {{"top", "right", "bottom", "left"}}.')

		return splitted_window

	def window_split_column_row(self, ratio, window, column_row):
		if column_row == "column":
			size = "height"
			start = "top"
		elif column_row == "row":
			size = "width"
			start = "left"
		else:
			raise ValueError(f'Unaceptable column_row {column_row}, it must be in {{"column", "row"}}.')
		if any(r <= 0 for r in ratio):
			raise ValueError(f"Ratio must consist of positive integers, {ratio} given.")

		sizes = [int(r * window[size] / sum(ratio)) for r in ratio]
		for i in range(window[size] - sum(sizes)):
			sizes[i] += 1

		current_start = window[start]
		for splitted_size in sizes:
			splitted_window = window.copy()
			splitted_window[start] = current_start
			splitted_window[size] = splitted_size
			current_start += splitted_size
			yield splitted_window

	def tree_str(self):
		self.words
		return ""

def m_to_rectangle(m, width, height):
	key = list(m)

	screen = []

	for i in range(height):
		row = []
		for j in range(width):
			row.append(".")
		screen.append(row)

	for i, obdelnik in enumerate(m):
		if width < m[obdelnik]["width"] + m[obdelnik]["left"] or any(m[obdelnik][x] < 0 for x in m[obdelnik])\
			or height < m[obdelnik]["height"] + m[obdelnik]["top"]:
			print(f"!{obdelnik} {i} nemá správnou velikost: {m[obdelnik]}")
			continue
		print(f" {obdelnik} {i}")
		for row in screen[m[obdelnik]["top"]:m[obdelnik]["top"] + m[obdelnik]["height"]]:
			for cell in range(m[obdelnik]["width"]):
				row[m[obdelnik]["left"] + cell] = str(i)


	rectangle = []

	for row in screen:
		row = "".join(row)
		rectangle.append(row)

	return "\n".join(rectangle)


things = []
things.append('body "fight"')

things.append("""
# typical windows
body
	bottom 3 "console_input"
	left 2/3*x "fight"
	column 1:1:1 "entities" "inventory" "history"
""")

# without row 2:1 cannot do typical windows with two columns of unequal size
things.append("""
# typical windows
body
	row 2:1
		bottom 3 "console_input"
		"fight"

		column 2:1 "entities" "history"
""")

# because of partily supported min(x,y) doesn't work for (120, 30), works for (60, 30)
things.append("""
body
	left 3/4*x "game"
	bottom x "minimap"  # gives a square x*x if x<y else y*x rectangle
	top 3
		left 3 "health_status"
		column 1:1:1
			"date"
			"mood_phase"
			row 1:1 "hunger" "thirst"
	top 1 "Zombols_or_Z's"
	"log"
""")

import json

x, y = 60, 30

for thing in things:
	solution = Solver(thing, x, y)
#	print(json.dumps(solution.windows, indent=4))
	print(m_to_rectangle(solution.windows, x, y))







"""
indetation = "│     │    │      "


body─left 3/4*x─"game" [20 : 50]
     │
     bottom min(x,y)─"minimap"
     │
     top 3─left 3─"health_status"
     │     │
     │     column 4─"date"
     │     │└───────"mood_phase"
     │     │└───────"mood_phase2"
     │     row 2─"hunger"
     │     │
     │     "thirst"
     top 1─"Zombols_or_Z's"
     │
     "log"
"log 2"

outputs = 2
self.iterator



body
	left 3/4*x
		"game"
		bottom min(x,y)
			"minimap"
			top 3
				left 3
					"health_status"
					column 3
						"date"
						"mood_phase"
						row 2
							"hunger"
							"thirst"
				top 1
					"Zombols_or_Z's"
					"log"



body
	left 3/4*x
		"game"
		bottom min(x,y)
			"minimap"
			top 3
				left 3
					"health_status"
					column 3
						"mood_phase"
						row 2
							"hunger"
							"thirst"
						top 1
							"Zombols_or_Z's"
							"log"
				MISSING
"""

