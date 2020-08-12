from library.Misc import local_loader


"""
GUIDLINE:

effect has uniqe name, such as "chill" or "blead", then it can have following properities (and allowed values):
	"type", "value"
		"dice": "value" is interpreted as what dice to throw
		"duration": "value" is how many more turns will the effect last
	"on_stack"
		"add": more of the same effect can be on one entity
		"refresh": when applied on entity, it refreshes the duration
	"on_print" 'Entity is ...' full explanation:
		If an effect has "on_print", then that is the form it is printed in.
		Elif effect's "type" is "duration", then effect's name is used.
		Else: the effect "type" is "dice". Effect's name+"ing" is used.
		see Entity.get_effect_string in file Entity.py
	"stat_bonus"
		( (stat, value), ... )
		entity's stat is increased by value
	"stat_penalty"
		( (stat, value), ... )
		entity's stat is lowered by value
	"prevents"
		(effect, ...)
		entity is immune to all listed effects
	"turned_by_into"
		( (by_effect, (into_effect, value)), ... )
		instead of '(into_effect, value)', None can be used for one-for-one removal (e.g. one FIRE cancels with one CHILL)
"""

frozen_comment = """
(frozen = target cannot move, attack, fight and cast spell; susceptible to PHYSICAL dmg (x2 multiplied incoming dmg);
duration: 3 turns or until replaced by WET effect when hit by FIRE spell, or manually via console or until break free;
break free: target tries to break free every turn - choose highest stat from: Constitution (Houževnatost), Strenght (Síla), Magie + its respective dice -> if sum is higher than 12, effect ends)
"""

effects = {
	"FIRE": {
		"type": "dice",
		"on_stack": "add",
		"on_print": "burning",
		# "dice": 0,  # rewriten on use
		# removed by
		"turned_by_into" : { "WET": None, "CHILL": None },
	},
	"BLEED": {
		"type": "dice",
		"on_stack": "add",
		"on_print": "bleeding",
		# "dice": 0,  # rewriten on use
		"activate_on_acquisition": True,
	},
	"CHILL": {
		"type": "duration",
		"on_stack": "add",
		"on_print": "chill",
		#"stat_bonus":
		"stat_penalty": { "obratnost": ("dice", 6), "boj": ("dice", 6) },  # ("dice", 6) Will be converted into specific throw on d6.
		# "duration": 5  # rewriten on use
		# removed by FIRE
		"turned_by_into" : { "FIRE": None },
	},
	"WET": {
		"type": "duration",
		"on_stack": "refresh",
		"on_print": "wet",
		# "duration": 5  # rewriten on use
		"turned_by_into" : { "CHILL": ("FREEZE", 3), "FIRE": None },
	},
	"FREEZE": {
		"type": "duration",
		"on_stack": "refresh",
		"on_print": "frozen",  # entity is frozen (3 turns)
		"//": frozen_comment,
		# "duration": 3  # rewriten on use
		"prevents": ("WET", "CHILL"),
		"turned_by_into" : { "FIRE": ("WET", 5) },
	},
	"STORM": {
		"type": "dice",  # well, it is not "duration"...
		# "dice": 0,  # NOT USED, but required
		"on_stack": "add",
		"on_print": "in storm",
		"print_when": "d10 == 10",
		"print_what": "is STRUCK by lightning!",
	}
}


for effect in effects:
	effects[effect]["name"] = effect

# shortcuts
effects["f"] = effects["FIRE"]
effects["b"] = effects["BLEED"]

output = local_loader(effects, "library.effects_local", "effects")
