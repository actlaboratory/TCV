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

	def initialize(self):
		_import()
		"""アプリを初期化する。"""
		self.proxyEnviron = proxyUtil.virtualProxyEnviron()
		if self.config.getboolean("proxy", "usemanualsetting", False) == True:
			self.proxyEnviron.set_environ(self.config["proxy"]["server"], self.config.getint("proxy", "port", 8080, 0, 65535))
		else:
			self.proxyEnviron.set_environ()
		self.setGlobalVars()
		# update関係を準備
		if self.config.getboolean("general", "update"):
			globalVars.update.update(True)
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		self.accountManager = twitcasting.accountManager.AccountManager()
		self.Manager = manager.manager(self.hMainView)
		if len(self.accountManager.tokens) == 0:
			simpleDialog.dialog("", _("アカウントが登録されていません。ライブに接続する前に、設定メニューのアカウントマネージャからアカウントの登録を行ってください。"))
			return True
		for i in self.accountManager.tokens:
			if datetime.datetime.now().timestamp() > i["expires_at"]:
				simpleDialog.dialog("", _("期限が切れたトークンが見つかりました。設定メニューのアカウントマネージャから、再度アカウントの追加を行ってください。"))
				self.accountManager.deleteAccount(self.accountManager.tokens.index(i))
		if len(sys.argv) == 2:
			self.Manager.connect(sys.argv[1])
		return True

	def setGlobalVars(self):
		globalVars.update = update.update()
		return

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。

		if self.Manager.livePlayer != None:
			self.Manager.livePlayer.exit()

		#戻り値は無視される
		return 0

