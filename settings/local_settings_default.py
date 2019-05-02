# Copy this file, make one named 'local_settings.py'
# in that file is your personal settings


DEBUG = True  # True: The program crashes when something goes wrong; False: it prints "fcked up" and carries on
AUTO_INPUT = True  # False: regular use; True: One of the tests (or all of them, this is based on setup/code) are run
LOG = False  # AUTO_INPUT must be False for this to work. False: Nothing; True: As the program runs, it logs all input and outputs into two files (one for inputs only, the other for everything, inputs are not numbered, unlike with tests)
