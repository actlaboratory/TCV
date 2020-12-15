# -*- coding: utf-8 -*-
#Application startup file

import os
import sys
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
import globalVars
import winsound
import simpleDialog
import pathlib
import traceback
import simpleDialog

def main():
	if os.path.exists("errorLog.txt"): os.remove("errorLog.txt")
	app=application.Main()
	globalVars.app=app
	app.initialize()
	app.MainLoop()
	app.config.write()

def exchandler(type, exc, tb):
	winsound.Beep(1000, 1000)
	msg=traceback.format_exception(type, exc, tb)
	print("".join(msg))
	globalVars.app.say(str(msg[-1]))
	f=open("errorLog.txt", "a")
	f.writelines(msg)
	f.close()



#global schope
sys.excepthook=exchandler

if __name__ == "__main__": main()
