questions
	1) co všechno má durabirity (weapons, armor, clothes, items?)
	2) 


TODO = """
useful as
	weapon
		Weapons use dmg, count kills, they further identifies as bows, axes,
		swords...
	wearable
		Wearables are clothes, armors etc. that add stats or should be tracked
		for purposes of clothes burning, so that PJ doesn't have to think about
		these. If something shouldn't be destroyed, it doesn't have durabirity.
	usable
		Items such as healing potions. They usually have ammount or charges.


weapon
	dmg_formula
		formula containing dice and math symbols such as
			"12 + d6 + d12"
		should be expanded to contain individual atributes of weapon,
		such as kills
	weapon_type
		

usable
	Amount
		The ammount of these objects on person. The object will disapear out of
		inventory once it runs to zero. When another item, that has the same
		name is added to the inventory, it just sums the ammounts.
	Charges
		There is current charges and capacity defined. When item is used it
		consumes some ammount of charges. Somehow items can be recharged.
		Typycally done by PJ manually.
"""

IMPLEMENTED = """
None
"""

"sekera": {
	"useful_as": {"weapon"}
}


fireball je magic, fire, elemental
