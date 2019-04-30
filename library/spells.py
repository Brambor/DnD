ice_lance1_comment = """
ice lance
on crit: add CHILLED effect
if target has WET effect
on crit: don't add CHILLED effect, add FROZEN effect
"""

spells = {
	"heal": {
		"mana_consumption": { "per_target": 1 },  # "base": 0
		"effects": {
			"heals": {
	#			"base": 0,
				"bonuses": { "magie": 2, "víra": 2, },
				"dice": 6,
			},
			"removes": { "base": ("BLEADING",) },  # "on_crit": ()
		},
	},

	"burn": {
		"mana_consumption": { "per_target": 1 },
		"effects": {
			"adds": { "base": ( ("burn", 4), ) },
		},
	},

	"splash": {
		"mana_consumption": { "base": 1 },
		"effects": {
			"adds": { "base": ( ("wet", 5), ) },
		},
	},

	"fireball": {
		"mana_consumption": { "per_target": 1 },
		"effects": {
			"damages": {
				#base 0
				"bonuses": { "magie": 2 },
				"dice": 6,
			},
			"adds": { "on_crit": ( ("burn", 4), ) },
		},
		"flags": ("FIRE",),  # NOT IMPLEMENTED, for unfreazing
	},

	"ice_lance1": {
		"mana_consumption": { "per_target": 1 },
		"effects": {
			"damages": {
				#base 0
				"bonuses": { "magie": 2 },
				"dice": 6,
			},
			"adds": { "on_crit": ( ("chill", 5), ) },
		},
		"//": ice_lance1_comment,
	},
}

# Add names to spells
for spell in spells:
	spells[spell]["name"] = spell
