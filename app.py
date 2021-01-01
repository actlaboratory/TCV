# -*- coding: utf-8 -*-
#Application Main

import AppBase
import sys
import simpleDialog
import datetime
import proxyUtil
import globalVars
import update

def _import():
	global main, manager, twitcasting
	from views import main
	import manager
	import twitcasting.accountManager

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
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		self.accountManager = twitcasting.accountManager.AccountManager()
		self.hasAccountIssue = False
		self.Manager = manager.manager(self.hMainView)
		if len(self.accountManager.tokens) == 0:
			simpleDialog.dialog(_("アカウント登録"), _("アカウントが登録されていません。ライブに接続する前に、設定メニューのアカウントマネージャからアカウントの登録を行ってください。"))
			self.hasAccountIssue = True
			return True
		for i in self.accountManager.tokens:
			if datetime.datetime.now().timestamp() > i["expires_at"]:
				simpleDialog.dialog("", _("期限が切れたトークンが見つかりました。設定メニューのアカウントマネージャから、再度アカウントの追加を行ってください。"))
				self.accountManager.deleteAccount(self.accountManager.tokens.index(i))
				self.hasAccountIssue = True
		if len(sys.argv) == 2:
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

