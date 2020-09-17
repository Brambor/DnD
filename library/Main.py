from itertools import chain

from library.damage_types import damage_types, output as output_df
from library.effects import effects, output as output_ef
from library.entities import entities, output as output_en
from library.items import items, output as output_it
from library.skills import skills, output as output_sk
from library.spells import spells, output as output_sp


library = {
	"damage_types": damage_types,
	"effects": effects,
	"entities": entities,
	"items": items,
	"spells": spells,
	"skills": skills,
}

warnings = []
if (overlap := set(skills).intersection(set(damage_types))):
	warnings.append(f"These are both, skills and damage_types: {overlap}. It's a problem when attacking.")


# Check if things in entities.py are defined in respective libraries
for e_name in entities:
	e = entities[e_name]
	if "skills" in e:
		for skill in e["skills"]:
			if skill not in skills:
				warnings.append(f"Skill '{skill}' of entity '{e_name}' is not in library of skills.")
	if "resistances" in e:
		for resistance in e["resistances"]:
			if resistance not in damage_types:
				warnings.append(f"Resistance '{resistance}' of entity '{e_name}' is not in library of damage_types.")

output_library = chain((
	*output_df,
	*output_ef,
	*output_en,
	*output_it,
	*output_sk,
	*output_sp,
	*(f"WARNING: {w}" for w in warnings),
))
