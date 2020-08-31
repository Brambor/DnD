# DnD
## Instalation:
Install libraries required. These are written in `requirements.txt`.

Usually done with command `pip install -r requirements.txt`.

## Use
If you need help using the commands, use command `help`.

## Custom Settings
Make file `settings/settings_local.py` and put there your preferences. These overwrite the defaults in `settings/settings_default.py`.
Look into `settings/settings_default.py` for inspiration.

## Custom entities
1) Run `DatabaseManager.py`.
2) Make changes you want in the opened browser.
3) When you are satisfied, press enter in the console running `DatabaseManager.py`. This closes the program and exports the data to `library/entities_database.py`.
