"""
The rules of printing seems to be:
If an effect has "on_print", then that is the form it is printed in.
Elif effect's "type" is "duration", then effect's name is used.
Else: the effect "type" is "dice". Effect's name+"ing" is used.
see Entity.get_effect_string in file Entity.py
"""


chill_comment = """
(chilled = lowered DEXTERITY (obratnost) and Combat (Boj) by d6 (when effect is created, one d6 is thrown per every stat) for duration of effect,
duration = 5 turns or until removed by FIRE spell, or manually - via console
"""

frozen_comment = """
(frozen = target cannot move, attack, fight and cast spell; susceptible to PHYSICAL dmg (x2 multiplied incoming dmg);
duration: 3 turns or until replaced by WET effect when hit by FIRE spell, or manually via console or until break free;
break free: target tries to break free every turn - choose highest stat from: Constitution (Houževnatost), Strenght (Síla), Magie + its respective dice -> if sum is higher than 12, effect ends)
"""

# prevents = imunity_to

effects = {
	"burn": {
		"type": "dice",
		"on stack": "add",
		"flags": ("FIRE",),
		# "dice": 0,  # rewriten on use
		# removed by
		"turned_by_into" : ( ("WET", None), ("CHILL", None) ),
	},
	"blead": {
		"type": "dice",
		"on stack": "add",
		"flags": ("BLEADING",),
		# "dice": 0,  # rewriten on use
	},
	"chill": {
		"type": "duration",
		"on stack": "add",
		"flags": ("CHILL",),
		# "duration": 5  # rewriten on use
		# removed by FIRE
		"turned_by_into" : ( ("FIRE", None), ),
		"//": chill_comment,
	},
	"wet": {
		"type": "duration",
		"on stack": "refresh",
		"flags": ("WET",),
		# "duration": 5  # rewriten on use
		"turned_by_into" : ( ("CHILL", ("freeze", 3)), ("FIRE", None) ),
	},
	"freeze": {
		"type": "duration",
		"on stack": "refresh",
		"flags": ("FREEZE",),
		"on_print": "frozen",  # entity is frozen (3 turns)
		"//": frozen_comment,
		# "duration": 3  # rewriten on use
		"prevents": ("WET", "CHILL"),
		"turned_by_into" : ( ("FIRE", ("wet", 5)), ),
	},
}


for effect in effects:
	effects[effect]["name"] = effect


effects["f"] = effects["burn"]
effects["b"] = effects["blead"]
