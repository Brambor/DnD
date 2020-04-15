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

output_library = chain( (*output_df, *output_ef, *output_en, *output_it, *output_sk, *output_sp) )
