import django
import json
import os
import subprocess
import webbrowser

from django.core.management import call_command
from sys import path
from tempfile import TemporaryFile

from modules.DnDException import DnDException


class DatabaseManager():
	def __init__(self, Connector):
		self.C = Connector
		self.server_is_running = False
		self.translate_skills = {
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

		path.append("DnDdatabase")
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "DnDdatabase.settings")
		django.setup()

		call_command("makemigrations", "--verbosity", "0")
		call_command("migrate", "--verbosity", "0")

	def json_from_database(self, what):
		tmpfile = TemporaryFile(mode="w+")
		a = call_command("dumpdata", what, stdout=tmpfile)
		tmpfile.seek(0)
		return json.load(tmpfile)

	def runserver(self, openwebbrowser=True):
		if not self.server_is_running:
			self.server = subprocess.Popen(["python", "DnDDatabase/manage.py", "runserver"], stdout=subprocess.DEVNULL)
			self.C.Print("Server is running.\n")
		else:
			self.C.Print("Server was running already.\n")
		self.server_is_running = True
		url = "http://localhost:8000/admin/database/entity/"
		if (openwebbrowser and not webbrowser.open(url)) or not openwebbrowser:
			self.C.Print(f"If no browser opened, just copy paste this url to your browser:\n{url}\n")

	def download(self):
		# Entity
		entities = {}
		for d in self.json_from_database("database.Entity"):
			entities[d["pk"]] = d["fields"]

		# Skills
		for d in self.json_from_database("database.Skills"):
			pk = d["fields"].pop("entity")
			new_dict = {}
			for key in d["fields"]:
				if d["fields"][key] != None:
					new_dict[self.translate_skills[str(key)]] = d["fields"][key]
			entities[pk]["skills"] = new_dict

		# Resistances
		for d in self.json_from_database("database.Resistances"):
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
		with open("library/templates/entities_database.py", "r") as template:
			with open("library/entities_database.py", "wb") as out_file:
				out_file.write(template.read().replace("%%DATA%%", json.dumps(entities, indent="\t", ensure_ascii=False)).encode('utf-8'))
		self.C.Print("Output exported. You have to restart the DnD to reimport the entities.\n")

	def stopserver(self, silent=False):
		if silent:
			if self.server_is_running:
				self.killserver()
			return

		if not self.server_is_running:
			raise DnDException("Server is not running, so you cannot stop it.\n")
#		os.killpg(os.getpgid(self.server.pid), signal.SIGTERM)
		self.killserver()
		self.C.Print("Server stopped.\n")

	def killserver(self):
		if os.name == 'nt':  # windows
			subprocess.Popen(f"TASKKILL /F /PID {self.server.pid} /T", stdout=subprocess.DEVNULL)
		else:  # 'postix' or 'java'
			subprocess.Popen(f"kill {self.server.pid}".split(), stdout=subprocess.DEVNULL)
		self.server_is_running = False
