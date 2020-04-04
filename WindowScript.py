

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
	raise ValueError("'%s' is not in the list.")

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
			raise ValueError("Unfinished iteration i=%d, your input=%s." % (0, self.words))
		self.i = 1
		self.depth = 0
		self.splitted_depth = 0
		self.stack = ["body"]
		self.tree = []
		self.last_keyword = None
		self.solver(self.body)
		assert((self.depth, self.splitted_depth) == (0, 0))
		print("ending depth: real=%d splitted=%d" % (self.depth, self.splitted_depth))
		if self.i != len(self.words):
			raise ValueError("Unfinished iteration i=%d, left from your input %s." % (self.i, self.words[self.i:]))

	def into_words(self, string):
		# remove comments, lines -> spaces
		out = " ".join(line.split("#")[0] for line in string.split("\n"))
		# tabs -> spaces
		out = " ".join(out.split("\t"))
		# break into individual words
		return out.strip().split()

	def eval_expression(self, expression, window):
		ret = int(eval(expression.replace("x", str(window["width"])).replace("y", str(window["height"]))))
#		print("%s = %s" % (expression, ret))
		return ret

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
				count = int(self.words_pp())
				splitted_windows = self.window_split_column_row(count, window, word)
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
				raise ValueError("Unknown keyword %s." % word)

		else:
			if not(word.startswith('"') and word.endswith('"')):
				raise ValueError("Window name '%s' doesn't start and end with '\"'." % word)
			self.windows[word.strip('"')] = window
			self.splitted_depth -= 1
		self.depth -= 1
		self.stack.pop()

	def words_pp(self):
		if self.i == len(self.words):
			msg = ("Last keyword '%s'; i=%d => iteration stopped at '%s' in depth %d (splitted %d).\n" % (
				self.last_keyword,
				self.i,
				self.words[self.i-1],
				self.depth,
				self.splitted_depth,
			))
			msg += "stack = %s\n" % self.stack
			msg += self.tree_str()

			msg += "Ran out of list! Probably unparsed: %s.\n" % self.words[reverse_index(self.words, self.last_keyword):]

			raise IndexError(msg)

		ret = self.words[self.i]	
		self.i += 1
		return ret

	def window_split_trbl(self, expression, window, from_direction):
		splitted_size = self.eval_expression(expression, window)
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
			raise ValueError('Unaceptable from_direction %s, it must be in {"top", "right", "bottom", "left"}.' % from_direction)

		return splitted_window

	def window_split_column_row(self, count, window, column_row):
		if column_row == "column":
			size = "height"
			start = "top"
		elif column_row == "row":
			size = "width"
			start = "left"
		else:
			raise ValueError('Unaceptable column_row %s, it must be in {"column", "row"}.' % from_direction)


		splitted_size = window[size] // count
		size_left = window[size] % count

		current_start = window[start]
		for _ in range(count):
			splitted_window = window.copy()
			splitted_window[start] = current_start
			splitted_window[size] = splitted_size
			if size_left:
				splitted_window[size] += 1
				size_left -= 1
			current_start += splitted_window[size]
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
			print("!%s %d nemá správnou velikost: %s" % (obdelnik, i, m[obdelnik]))
			continue
		print(" %s %d" % (obdelnik, i))
		for row in screen[m[obdelnik]["top"]:m[obdelnik]["top"] + m[obdelnik]["height"]]:
			for cell in range(m[obdelnik]["width"]):
				row[m[obdelnik]["left"] + cell] = str(i)


	rectangle = []

	for row in screen:
		row = "".join(row)
		rectangle.append(row)

	return "\n".join(rectangle)



thing_0 = 'body "fight"'

thing_1 = """
# typical windows
body
	bottom 3 "console_input"
	left 2/3*x "fight"
	column 3 "entities" "inventory" "history"
"""

# because of partily supported min(x,y) doesn't work for (120, 30), works for (60, 30)
thing_3 = """
body
	left 3/4*x "game"
	bottom min(x,y) "minimap"  # gives a square x*x if x<y else y*x rectangle
	top 3
		left 3 "health_status"
		column 3
			"date"
			"mood_phase"
			row 2 "hunger" 
	top 1 "Zombols_or_Z's"
	"log"
"""
import json

x, y = 60, 30

for string in (thing_0, thing_1, thing_3):
	solution = Solver(string, x, y)
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

