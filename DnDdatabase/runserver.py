import django
import json
import os
import signal
import subprocess
import webbrowser

from django.core.management import call_command
from tempfile import TemporaryFile


def json_from_database(what):
	tmpfile = TemporaryFile(mode="w+")
	a = call_command("dumpdata", what, stdout=tmpfile)
	tmpfile.seek(0)
	data = json.load(tmpfile)
	return data

# CONSTANTS
translate_skills = {
	"boj": "boj",
	"sila": "síla",
	"houzevnatost": "houževnatost",
	"remeslo": "řemeslo",
	"vira": "víra",
	"obratnost": "obratnost",
	"presnost": "přesnost",
	"plizeni": "plížení",
	"priroda": "příroda",
	"zrucnost": "zručnost",
	"magie": "magie",
	"intelekt": "intelekt",
	"znalosti": "znalosti",
	"vnimani": "vnímání",
	"charisma": "charisma",
}

# RUN SERVER & CHANGE DATA
server = subprocess.Popen(["python", "manage.py", "runserver"], stdout=subprocess.DEVNULL)
url = "http://localhost:8000/admin/database/entity/"
if not webbrowser.open(url):
	print(f"If no browser opened, just copy paste this url to your browser:\n{url}")


input("Once you are done, press enter to terminate Django server and export results to 'out_file.py'.\n"
	"PRESS ENTER TO EXIT >>>")

# DATA PROCESS
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DnDdatabase.settings")
django.setup()

# Entity
entities = {}
for d in json_from_database("database.Entity"):
	entities[d["pk"]] = d["fields"]

# Skills
for d in json_from_database("database.Skills"):
	pk = d["fields"].pop("entity")
	new_dict = {}
	for key in d["fields"]:
		if d["fields"][key] != None:
			new_dict[translate_skills[str(key)]] = d["fields"][key]
	entities[pk]["skills"] = new_dict

# Resistances
for d in json_from_database("database.Resistances"):
	pk = d["fields"].pop("entity")
	new_dict = {}
	for key in d["fields"]:
		if d["fields"][key]:
			new_dict[key] = d["fields"][key]/100
	entities[pk]["resistances"] = new_dict


# referrence entities by name, delete pk
len_data = len(entities)
for pk in tuple(entities.keys()):
	name = entities[pk].pop("name")
	entities[name] = entities[pk]
	entities[name]["nickname"] = name
	del entities[pk]

# OUT
with open("out_file.py", "w") as out_file:
	out_file.write(json.dumps(entities, indent="\t", ensure_ascii=False))
print("Output exported.")

# EXIT
server.send_signal(signal.CTRL_BREAK_EVENT)

