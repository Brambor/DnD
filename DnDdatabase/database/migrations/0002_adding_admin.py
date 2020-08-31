import os
from django.db import migrations

class Migration(migrations.Migration):
	def generate_superuser(apps, schema_editor):
		from django.contrib.auth.models import User

		superuser = User.objects.create_superuser(
			username="Admin",
			password="1234")

		superuser.save()

	dependencies = [
		('database', '0001_initial'),
	]

	operations = [
		migrations.RunPython(generate_superuser),
	]
