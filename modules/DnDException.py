class DnDException(Exception):
	def __init__(self, *args):
		super(DnDException, self).__init__(*args)
		raise self


class DnDExit(Exception):
	pass
