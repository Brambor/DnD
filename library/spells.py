from modules.Misc import local_loader


"""
GUIDLINE:

spell has uniqe name, such as "heal" or "fireball", then it can have following properities (and allowed values):
	"mana_consumption" {}
		(how much mana does the caster use)
		"base" (int) how much is spent on cast
		"per_target" (int) how much (more) is spent per target
	"effects" {}
		(what the spell does)
		"damages"
			"base" (int) basic spell damage
			"bonuses" (int) spell is (caster stat)*(bonus value) more damaging
			"dice" (int) what dice is thrown
		"heals"
			same as "damages" but heals instead
		"removes"
			(what effects does the spell remove)
			"base" always (even if critical dice throw)
				( effect, ... )
			"on_crit" on critical dice throw
				( effect, ... )
		"adds"
			(what effects does the spell apply/add to the target)
			"base" always (even if critical dice throw)
				( (effect, value), ... )
			"on_crit" on critical dice throw
				( (effect, value), ... )
	"flags"
		NOT IMPLEMENTED
		(what are the spell characteristic (probably elements))
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
			"removes": { "base": ("BLEAD",) },  # "on_crit": ()
		},
	},

	"burn": {
		"mana_consumption": { "per_target": 1 },
		"effects": {
			"adds": { "base": ( ("FIRE", 4), ) },
		},
	},

	"splash": {
		"mana_consumption": { "base": 1 },
		"effects": {
			"adds": { "base": ( ("WET", 5), ) },
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
			"adds": { "on_crit": ( ("FIRE", 4), ) },
		},
		"flags": ("FIRE",),  # NOT IMPLEMENTED
	},

	"ice_lance1": {
		"mana_consumption": { "per_target": 1 },
		"effects": {
			"damages": {
				#base 0
				"bonuses": { "magie": 2 },
				"dice": 6,
			},
			"adds": { "on_crit": ( ("CHILL", 5), ) },
		},
	},
}

# Add names to spells
for spell in spells:
	spells[spell]["name"] = spell

output = local_loader(spells, "library.spells_local", "spells")
