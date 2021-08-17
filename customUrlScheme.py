# Custom URL Scheme Utility

import itertools
import logging
import sys
import traceback
import winreg

import constants
import errorCodes
import globalVars

log = logging.getLogger("%s.%s" % (constants.LOG_PREFIX, "CustomURLSchemeUtility"))

def register(scheme, application=None):
	if application == None:
		application = globalVars.app.getAppPath()
	try:
		with winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, "software\\classes\\" + scheme) as k1:
			winreg.SetValueEx(k1, None, 0, winreg.REG_SZ, scheme)
			winreg.SetValueEx(k1, "URL Protocol", 0, winreg.REG_SZ, "")
			with winreg.CreateKeyEx(k1, "shell") as k2:
				with winreg.CreateKeyEx(k2, "open") as k3:
					with winreg.CreateKeyEx(k3, "command") as k4:
						winreg.SetValueEx(k4, None, 0, winreg.REG_SZ, r'"%s" %%1' % application)
		return True
	except WindowsError as e:
		log.error(traceback.format_exc())
		return False

def unregister(scheme):
	_deleteKeyAndSubkeys(winreg.HKEY_CURRENT_USER, "software\\classes\\" + scheme)

def isRegistered(scheme):
	with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "software\\classes") as k:
		return scheme in _getSubKeys(k)

def _deleteKeyAndSubkeys(key, subkey):
	isFinished = False
	tryCount = 0
	while isFinished == False and tryCount <= 10:
		try:
			with winreg.OpenKey(key, subkey, 0, winreg.KEY_WRITE|winreg.KEY_READ) as k:
				for i in itertools.count():
					try:
						subkeyName = winreg.EnumKey(k, i)
					except WindowsError as e:
						break
					_deleteKeyAndSubkeys(k, subkeyName)
				winreg.DeleteKey(k, "")
			isFinished = True
		except Exception as e:
			tryCount += 1

def _getSubKeys(key):
	ret = []
	for i in itertools.count():
		try:
			ret.append(winreg.EnumKey(key, i))
		except WindowsError:
			break
	return ret
