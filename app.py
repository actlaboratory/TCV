# -*- coding: utf-8 -*-
#Application Main

import AppBase
from views import main
import sys
import manager
import twitcasting.accountManager
import simpleDialog
import datetime

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
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
				simpleDialog.dialog("", _("期限が切れたトークンが見つかりました。ツールメニューのアカウントマネージャから、再度アカウントの追加を行ってください。"))
				self.accountManager.deleteAccount(self.accountManager.tokens.index(i))
		if len(sys.argv) == 2:
			self.Manager.connect(sys.argv[1])
		return True

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。


		#戻り値は無視される
		return 0

