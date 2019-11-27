from modules.Misc import local_loader


"""
DOCS: This does nothing / To Be Implemented
"""

items = {
	"healing_mushroom": {
		"hp_restore": 40,
	},
	"mana_potion": {
		"mana_restore": 3,
	},
}


# Add names to items
for i in items:
	items[i]["derived_from"] = i

local_loader(items, "items.items_local", "items")
