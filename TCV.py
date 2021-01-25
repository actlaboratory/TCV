# -*- coding: utf-8 -*-
#Application startup file

import sys
import winsound
import requests.exceptions
import simpleDialog
import traceback
import globalVars

def exchandler(type, exc, tb):
	try:
		for i in globalVars.app.Manager.timers:
			i.Stop()
		globalVars.app.Manager.livePlayer.exit()
	except:
		pass
	if type == requests.exceptions.ConnectionError:
		simpleDialog.errorDialog(_("通信に失敗しました。インターネット接続を確認してください。プログラムを終了します。"))
		os._exit(1)
	elif type == requests.exceptions.ProxyError:
		simpleDialog.errorDialog(_("通信に失敗しました。プロキシサーバーの設定を確認してください。プログラムを終了します。"))
		os._exit(1)
	msg=traceback.format_exception(type, exc, tb)
	print("".join(msg))
	try:
		f=open("errorLog.txt", "a")
		f.writelines(msg)
		f.close()
	except:
		pass
	if not hasattr(sys, "frozen"):
		winsound.Beep(1000, 1000)
		globalVars.app.say(str(msg[-1]))
	else:
		simpleDialog.winDialog("error", "An error has occured. Contact to the developer for further assistance. Detail:" + "\n".join(msg[-2:]))
	os._exit(1)

#global schope
sys.excepthook=exchandler

import os
#カレントディレクトリを設定
if hasattr(sys,"frozen"): os.chdir(os.path.dirname(sys.executable))
else: os.chdir(os.path.abspath(os.path.dirname(__file__)))

import win32timezone#ダミー

#dllを相対パスで指定した時のため、カレントディレクトリを変更
os.chdir(os.path.dirname(os.path.abspath(__file__)))

#Python3.8対応
#dllやモジュールをカレントディレクトリから読み込むように設定
if sys.version_info.major>=3 and sys.version_info.minor>=8:
	os.add_dll_directory(os.path.dirname(os.path.abspath(__file__)))
	sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app as application
import constants
import pathlib

def main():
	if os.path.exists("errorLog.txt"):
		try:
			os.remove("errorLog.txt")
		except:
			pass
	app=application.Main()
	globalVars.app=app
	app.initialize()
	app.MainLoop()
	app.config.write()

if __name__ == "__main__": main()
