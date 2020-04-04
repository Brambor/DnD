from modules.Misc import local_loader


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

output = local_loader(damage_types, "library.damage_types_local", "damage_types")
