from __future__ import absolute_import
import ctypes
import os
import sys
import types

def load_library(libname, cdll=False):
	if is_frozen():
		libfile = os.path.join(embedded_data_path(), 'accessible_output2', 'lib', libname)
	else:
		libfile = os.path.join(module_path(), 'lib', libname)
	if cdll:
		return ctypes.cdll[libfile]
	else:
		return ctypes.windll[libfile]

def get_output_classes():
	from . import outputs
	module_type = types.ModuleType
	classes = [m.output_class for m in outputs.__dict__.values() if type(m) == module_type and hasattr(m, 'output_class')]
	return sorted(classes, key=lambda c: c.priority)

def find_datafiles():
	import os
	import platform
	from glob import glob
	import accessible_output2
	if platform.system() != 'Windows':
		return []
	path = os.path.join(accessible_output2.__path__[0], 'lib', '*.dll')
	results = glob(path)
	dest_dir = os.path.join('accessible_output2', 'lib')
	return [(dest_dir, results)]

def is_frozen():
	"""Return a bool indicating if application is compressed"""
	import imp
	return hasattr(sys, 'frozen') or imp.is_frozen("__main__")

#------------------------------------------------------
#
#platform_utilsからのぬきだし
#
#------------------------------------------------------
import inspect

def embedded_data_path():
	"""Returns the full executable path/name if frozen, or the full path/name of the main module if not."""
	if is_frozen():
		executable =  sys.executable
	else:
		try:
			import __main__
			executable =  os.path.abspath(__main__.__file__)
		except AttributeError:
			executable = sys.argv[0]

	path = os.path.abspath(os.path.dirname(executable))
	return path

def module_path(level=2):
	return os.path.abspath(os.path.dirname(get_module(level)))

def get_module(level=2):
	"""Hacky method for deriving the caller of this function's module."""
	return inspect.getmodule(inspect.stack()[level][0]).__file__