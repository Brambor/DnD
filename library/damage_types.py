from library.Misc import local_loader


damage_types = {
	'acid',
	'blunt',
	'elemental',
	'fire',
	'ice',
	'lightning',
	'magic',
	'necrotic',
	'physical',
	'piercing',
	'poison',
	'psychic',
	'radiant',
	'slashing',
	'true',
	'water',
	'wind',
}

damage_types = dict(((d, d) for d in damage_types))

for alias, original in (
	("a", "acid"),
	("b", "blunt"),
	("e", "elemental"),
	("ele", "elemental"),
	("f", "fire"),
	("i", "ice"),
	("c", "ice"),
	("cold", "ice"),
	("cool", "ice"),
	("l", "lightning"),
	("lig", "lightning"),
	("light", "lightning"),
	("m", "magic"),
	("mag", "magic"),
	("n", "necrotic"),
	("nec", "necrotic"),
	("necro", "necrotic"),
	("p", "physical"),
	("phys", "physical"),
	("pie", "piercing"),
	("pierce", "piercing"),
	("poi", "poison"),
	("psy", "psychic"),
	("psych", "psychic"),
	("r", "radiant"),
	("rad", "radiant"),
	("s", "slashing"),
	("slash", "slashing"),
	("blade", "slashing"),
	("t", "true"),
	("w", "water"),
	("wat", "water"),
	("wi", "wind"),
	("air", "wind"),
):
	if alias in damage_types:
		raise ValueError("damage_types already contains %s." % alias)
	damage_types[alias] = original

output = local_loader(damage_types, "library.damage_types_local", "damage_types")
