from modules.Weapons import Fist, Axe

entities = {
	"pes": {
		"nickname": "psík",
		"group": "enemies",
		"hp_max": 100,
		"mana_max": 1,
		"weapon": Fist(2, 8),
		"armor": 1,
		"boj": 1,
		"magie": 1,
		"víra": 1,
	},
	"weaping_angel": {
		"nickname": "weaping_angel",
		"hp_max": 10000,
	},
	"Thorbald": {
		"nickname": "Thorbald",
		"group": "players",
		"hp_max": 100,
		"mana_max": 2,  # added, not Thorbald
		"weapon": Axe(29, 8),
		"armor": 22,
		"boj": 13,
		"magie": 1,
		"víra": 1,
	},
}


# Add names to spells
for e in entities:
	entities[e]["derived_from"] = e
