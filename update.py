import requests
import wx
import constants
import errorCodes
import globalVars
import simpleDialog
import webbrowser
import os
import subprocess
import sys
from views import updateDialog
import time
import threading
import win32api

def getUpdaterVersion():
	""" return (pyVersion, exeVersion) """
	return ["1.0.0", _getFileVersion("./updater.exe")]

def _getFileVersion(filePath):
	info = win32api.GetFileVersionInfo(filePath, os.sep)
	ms = info['FileVersionMS']
	ls = info['FileVersionLS']
	version = '%d.%d.%d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls))
	return version


class update(threading.Thread):
	def __init__(self):
		super().__init__()
		self.needStop = False

	def update(self, auto=False):
		# アップデータチェック
		updaterCheck = False
		try:
			if getUpdaterVersion()[0] == getUpdaterVersion()[1]: updaterCheck = True
		except: pass
		if not updaterCheck:
			simpleDialog.dialog(_("アップデート"), _("アップデータが利用できません。お手数ですが、再度ソフトウェアをダウンロードしてください。"))
			return
		
		params = {
			"name": constants.APP_NAME,
			"updater_version": constants.UPDATER_VERSION,
			"version": constants.APP_VERSION
		}
		timeout = globalVars.app.config.getint("general", "timeout", 3)
		try:
			response = requests.get(constants.UPDATE_URL, params, timeout = timeout)
		except requests.exceptions.ConnectTimeout:
			if not auto:
				simpleDialog.dialog(_("アップデート"), _("サーバーへの通信がタイムアウトしました。"))
			return
		except requests.exceptions.ConnectionError as e:
			print(e)
			if not auto:
				simpleDialog.dialog(_("アップデート"), _("サーバーへの接続に失敗しました。インターネット接続などをご確認ください"))
			return
		if not response.status_code == 200:
			if not auto:
				simpleDialog.dialog(_("アップデート"), _("サーバーとの通信に失敗しました。"))
			return
		self.info = response.json()
		code = self.info["code"]
		if code == errorCodes.UPDATER_LATEST:
			if not auto:
				simpleDialog.dialog(_("アップデート"), _("現在のバージョンが最新です。アップデートの必要はありません。"))
			return
		elif code == errorCodes.UPDATER_BAD_PARAM:
			if not auto:
				simpleDialog.dialog(_("アップデート"), _("リクエストパラメーターが不正です。開発者まで連絡してください"))
			return
		elif code == errorCodes.UPDATER_NOT_FOUND:
			if not auto:
				simpleDialog.dialog(_("アップデート"), _("アップデーターが登録されていません。開発者に連絡してください。"))
			return
		elif code == errorCodes.UPDATER_NEED_UPDATE or errorCodes.UPDATER_VISIT_SITE:
			self.dialog = updateDialog.updateDialog()
			self.dialog.Initialize()
			self.dialog.Show()
		return

	def open_site(self):
		webbrowser.open(self.info["URL"])
		return

	def run(self):
		url = self.info["updater_url"]
		file_name = "update_file.zip"
		response = requests.get(url, stream = True)
		total_size = int(response.headers["Content-Length"])
		wx.CallAfter(self.dialog.gauge.SetRange, (total_size))
		now_size = 0
		broken = False
		with open(file_name, mode="wb") as f:
			for chunk in response.iter_content(chunk_size = 1024):
				if self.needStop:
					broken = True
					print("broken!")
					break
				f.write(chunk)
				now_size += len(chunk)
				wx.CallAfter(self.dialog.gauge.SetValue, (now_size))
				wx.YieldIfNeeded()
		if broken:
			print("canceled!")
			os.remove(file_name)
			wx.CallAfter(self.dialog.end)
			return
		print("downloaded!")
		if os.path.exists("updater.exe"):
			pid = os.getpid()
			subprocess.Popen(("updater.exe", sys.argv[0], constants.UPDATER_WAKE_WORD, file_name, self.info["updater_hash"], str(pid)))
			wx.CallAfter(sys.exit)
		else:
			os.remove(file_name)			
			wx.CallAfter(self.dialog.updater_notFound)
			return

	def exit(self):
		self.needStop = True
		return
