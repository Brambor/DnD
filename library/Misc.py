import importlib


def local_loader(global_dict, lib, dicts_name):
	try:
		output = []
		loc_dict = getattr(importlib.import_module(lib), dicts_name)
		output.append("'%s' loaded" % dicts_name)
		for e in loc_dict:
			if e in global_dict:
				output.append("\t'%s' overrode" % e)
		global_dict.update(loc_dict)
		return output
	except ImportError:
		return []
