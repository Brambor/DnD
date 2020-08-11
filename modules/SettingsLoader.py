from settings import settings_default as settings


output_settings = []
try:
	from settings import settings_local
	output_settings.append("Custom settings loaded.")

	deprecated = (set(dir(settings_local)) - set(dir(settings)))
	if deprecated:
		output_settings.append(
			"Warning! These settings in settings/settings_local.py are deprecated"
			" <==> do nothing. You should delete them:\n\t%s\n" % "\n\t".join(deprecated)
		)

	for value in dir(settings_local):
		if not value.startswith("__"):
			setattr(settings, value, getattr(settings_local, value))

except ImportError:
	output_settings.append("Custom settings not loaded."
		" Look into settings/settings_default.py to see how to make it.")
