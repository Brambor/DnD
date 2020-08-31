"""
when in library/templates/
	This is templte, don't mess with it.
when in library/
	This is exported from Django database (run DnD/DatabaseManager.py).
	Don't mess with this file, it is overwritten each run of DatabaseManager.py
"""

entities = %%DATA%%


# Add names to spells
for e in entities:
	entities[e]["derived_from"] = e
