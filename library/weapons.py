"""
DOCS: Notify the programmer that you wanted to make weapons, but they didn't write the docs...
"""

weapons = {
	"axe": {
		"weapon_type": "axe",  # TODO bleed on crit
		"basic_dmg": 15,
		"on_crit": {
			"triggers_effects": {
				"add_dmg_from_effect": "axe_crit_D6",
			},
		},
		"kill_counter": 0,
	},
	"požíračka": {
		"basic_dmg": 17,
		"triggers_effects": {"add_dmg_from_key": "souls_consumed"},
		"on_kill": {"add_x_to_this_weapons": (1, "souls_consumed")},
		"souls_consumed": 17,
	},
}

weapon_effects = {
#	"add_x_to_this_weapons": <func_0x...>,
	"axe_crit_D6": {
		"triggers_effects": {"add_dmg_from_dice": "d6"},
		"on_crit": {
			"triggers_effects": {"add_dmg_from_effect": "axe_crit_D6"},
		}
	}

}
# Add names to weapons
for w in weapons:
	weapons[w]["derived_from"] = w
