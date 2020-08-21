import importlib


def local_loader(global_dict, lib, dicts_name):
	try:
		output = []
		loc_dict = getattr(importlib.import_module(lib), dicts_name)
		output.append(f"'{dicts_name}' loaded")
		for e in loc_dict:
			if e in global_dict:
				output.append(f"\t'{e}' overwritten")
		global_dict.update(loc_dict)
		return output
	except ImportError:
		return []
