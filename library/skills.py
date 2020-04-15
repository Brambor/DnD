from modules.Misc import local_loader

skills = (  # a tuple so it can be ordered
	"boj",
	"síla",
	"houževnatost",
	"řemeslo",
	"víra",
	"obratnost",
	"přesnost",
	"plížení",
	"příroda",
	"zručnost",
	"magie",
	"intelekt",
	"znalosti",
	"vnímání",
	"charisma",
)

output = local_loader(skills, "library.skills_local", "skills")
