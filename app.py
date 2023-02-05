# -*- coding: utf-8 -*-
#Application Main

import os
import AppBase
import sys
import simpleDialog
import datetime
import proxyUtil
import globalVars
import update
import threading
import constants
import soundPlayer

def _import():
	global main, manager, twitcasting
	from views import main
	import manager
	import twitcasting.accountManager
	import twitcasting.advancedAccountManager

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()
		if self.config["autoReadingOptions"]["viewersIncreasedAnnouncement"] == "@@@viewers_increased@@@":
			self.config["autoReadingOptions"]["viewersIncreasedAnnouncement"] = _("閲覧者が$viewers人に増えました。")
		if self.config["autoReadingOptions"]["viewersDecreasedAnnouncement"] == "@@@viewers_decreased@@@":
			self.config["autoReadingOptions"]["viewersDecreasedAnnouncement"] = _("閲覧者が$viewers人に減りました。")

	def initialize(self):
		_import()
		"""アプリを初期化する。"""
		self.setGlobalVars()

		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		self.setProxyEnviron()
		self.installThreadExcepthook()
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		# sessions.dat対応
		if self.config.getint("general", "fileVersion", 100) == 100:
			if os.path.exists(constants.SESSION_FILE_NAME):
				try:
					os.remove(constants.SESSION_FILE_NAME)
					self.log.debug("File %s deleted." % constants.SESSION_FILE_NAME)
				except Exception as e:
					self.log.error("Failed to delete file %s: e" % constants.SESSION_FILE_NAME)
			self.config["general"]["fileVersion"] = 101
		self.accountManager = twitcasting.accountManager.AccountManager()
		self.hasAccountIssue = False
		self.Manager = manager.manager(self.hMainView)
		self.advancedAccountManager = twitcasting.advancedAccountManager.AdvancedAccountManager()
		if len(self.accountManager.tokens) == 0:
			simpleDialog.dialog(_("アカウント登録"), _("アカウントが登録されていません。ライブに接続する前に、設定メニューのアカウントマネージャからアカウントの登録を行ってください。"))
			self.hasAccountIssue = True
			return True
		for i in self.accountManager.tokens:
			if datetime.datetime.now().timestamp() > i["expires_at"]:
				simpleDialog.dialog(_("アカウントの再登録"), _("期限が切れたトークンが見つかりました。設定メニューのアカウントマネージャから、再度アカウントの追加を行ってください。"))
				self.accountManager.deleteAccount(self.accountManager.tokens.index(i))
				self.hasAccountIssue = True
		self.accountManager.removeUnavailableTokens()
		if len(sys.argv) == 2:
			self.hMainView.Clear()
			self.Manager.connect(sys.argv[1])
			return True
		if self.hasAccountIssue == False and self.config.getboolean("general", "autoconnect", True) == True:
			self.hMainView.events.connect()
			return True

	def setProxyEnviron(self):
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()
		if "http_proxy" in os.environ:
			soundPlayer.player.setProxy(os.environ["http_proxy"])

	def installThreadExcepthook(self):
		_init = threading.Thread.__init__

		def init(self, *args, **kwargs):
			_init(self, *args, **kwargs)
			_run = self.run

			def run(*args, **kwargs):
				try:
					_run(*args, **kwargs)
				except:
					sys.excepthook(*sys.exc_info())
			self.run = run

		threading.Thread.__init__ = init

	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		if self.Manager.livePlayer != None:
			self.Manager.livePlayer.exit()

		# アップデート
		globalVars.update.runUpdate()

		#戻り値は無視される
		return 0

	def getProxyInfo(self):
		"""プロキシサーバーの情報を取得

		:return: (URL, port)のタプル
		:rtype: tuple
		"""
		data = os.environ.get("HTTP_PROXY")
		self.log.debug("Retrieving proxy information from environment variable...")
		if data == None:
			self.log.info("Proxy information could not be found.")
			return (None, None)
		self.log.debug("configured data: %s" %data)
		separator = data.rfind(":")
		if separator == -1:
			self.log.info("Validation Error.")
			return (None, None)
		url = data[:separator]
		port = data[separator + 1:]
		try:
			port = int(port)
		except ValueError:
			self.log.info("Validation Error.")
			return (None, None)
		self.log.info("Proxy URL: %s, Port: %s." %(url, port))
		return (url, port)
