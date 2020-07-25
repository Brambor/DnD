"""
This is an example of how to use 'library/*_local.py'.
You can copy this file and remove '_example' at the end making it 'entities_local.py'
After that, when you launch DnD.py, it should say:
	'''
	'entities' loaded
	        'weaping_angel' overrode
	'''
at the begining of the output.
"""


"""
DOCS: Notify the programmer that you wanted to make entities, but they didn't write the docs...
"""

entities = {
	"weaping_angel": {
		"nickname": "weaping_angel",
		"hp_max": 3,
	},
	"wolf": {
		"nickname": "wolf",
		"hp_max": 15,
	},
}

#entities["pes"]["weapon"]["dmg"] = 2
#entities["pes"]["weapon"]["dice"] = "d8"


# Add names to spells
for e in entities:
	entities[e]["derived_from"] = e
