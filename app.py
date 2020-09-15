# -*- coding: utf-8 -*-
#Application Main

import AppBase
from views import main
import sys
import manager
import twitcasting.accountManager

class Main(AppBase.MainBase):
	def __init__(self):
		super().__init__()

	def initialize(self):
		"""アプリを初期化する。"""
		self.hMainView=main.MainView()
		if self.config.getboolean(self.hMainView.identifier,"maximized",False):
			self.hMainView.hFrame.Maximize()
		self.hMainView.Show()
		self.Manager = manager.manager(self.hMainView)
		self.accountManager = twitcasting.accountManager.AccountManager()
		if len(sys.argv) == 2:
			self.Manager.connect(sys.argv[1])
		return True

	def OnExit(self):
		#設定の保存やリソースの開放など、終了前に行いたい処理があれば記述できる
		#ビューへのアクセスや終了の抑制はできないので注意。


		#戻り値は無視される
		return 0

