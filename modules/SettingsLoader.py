from settings import settings_default as settings

try:
	from settings import settings_local
	print("Custom settings loaded.")
except ImportError:
	print("Custom settings not loaded. Look into settings/settings_default.py to see how to make it.")

deprecated = (set(dir(settings_local)) - set(dir(settings)))
if deprecated:
	print(
		"Warning! These settings in settings/settings_local.py are deprecated"
		" <==> do nothing. You should delete them:\n\t%s\n" % "\n\t".join(deprecated))

for value in dir(settings_local):
	if not value.startswith("__"):
		setattr(settings, value, getattr(settings_local, value))
