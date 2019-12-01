from itertools import chain

from library.effects import effects, output as output_ef
from library.entities import entities, output as output_en
from library.items import items, output as output_it
from library.spells import spells, output as output_sp


library = {
	"entities": entities,
	"spells": spells,
	"effects": effects,
	"items": items,
}

output_library = chain( (*output_ef, *output_en, *output_it, *output_sp) )
