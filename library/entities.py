from modules.Misc import local_loader
from modules.Weapons import Fist, Axe
from library.weapons import weapons


"""
DOCS: Notify the programmer that you wanted to make entities, but they didn't write the docs...
"""

entities = {
	"pes": {
		"nickname": "psík",
		"group": "enemies",
		"hp_max": 100,
		"mana_max": 1,
		"weapon": Fist(2, 8), # weapons["fist"],  # 
		"armor": 1,
		"skills": {
			"boj": 1,
			"magie": 1,
			"víra": 1,
		},
	},
	"weaping_angel": {
		"nickname": "weaping_angel",
		"hp_max": 10000,
		"resistances": {
			"radiant": 2,  # trigers warning, this heals the char by 100% insead of damaging it
			"psychic": -0.15, # 15% more dmg from psychic
		},
		"armor": 40,
	},
	"Thorbald": {
		"nickname": "Thorbald",
		"group": "players",
		"hp_max": 100,
		"mana_max": 2,  # added, not Thorbald
		"weapon": Axe(29, 8),
		"armor": 22,
		"skills": {
			"boj": 13,
			"magie": 1,
			"víra": 1,
		},
		"resistances": {  # how much resistance does this creature have.
			"fire": 1/3, # 1/3 = 33.3% reduction in incoming damage
		},
	},
}

#entities["pes"]["weapon"]["dmg"] = 2
#entities["pes"]["weapon"]["dice"] = "d8"


# Add names to spells
for e in entities:
	entities[e]["derived_from"] = e

output = local_loader(entities, "library.entities_local", "entities")
