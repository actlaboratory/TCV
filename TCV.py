# -*- coding: utf-8 -*-
#Application startup file

import win32timezone#ダミー
def _(string): pass#dummy

#dllを相対パスで指定した時のため、カレントディレクトリを変更
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import app as application
import constants
import globalVars
import winsound
import simpleDialog
import sys
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
