# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import logging
import os
import sys
import wx
import re
import ctypes
import pywintypes

import constants
import errorCodes
import globalVars
import menuItemsStore

from logging import getLogger
from simpleDialog import dialog
from .base import *
from simpleDialog import *

import views.connect


class MainView(BaseView):
	def __init__(self):
		super().__init__()
		self.identifier="mainView"#このビューを表す文字列
		self.log=getLogger(self.identifier)
		self.log.debug("created")
		self.app=globalVars.app
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",800),
			self.app.config.getint(self.identifier,"sizeY",600),
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY")
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.FileMenu=wx.Menu()
		self.HelpMenu=wx.Menu()

		#メニューの中身
		self.RegisterMenuCommand(self.FileMenu,"connect",_("接続"))
		self.RegisterMenuCommand(self.FileMenu,"disconnect",_("切断"))
		self.RegisterMenuCommand(self.FileMenu,"exit",_("終了"))
		self.RegisterMenuCommand(self.HelpMenu,"versionInfo",_("バージョン情報"))

		#メニューバーの生成
		self.hMenuBar=wx.MenuBar()
		self.hMenuBar.Append(self.FileMenu,_("ファイル"))
		self.hMenuBar.Append(self.HelpMenu,_("ヘルプ"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る


		if selected==menuItemsStore.getRef("exit"):
			self.Exit()
		elif selected==menuItemsStore.getRef("versionInfo"):
			dialog(_("バージョン情報"), _("%(appName)s Version %(versionNumber)s.\nCopyright (C) %(year)s %(developerName)s") %{"appName": constants.APP_NAME, "versionNumber": constants.APP_VERSION, "year":constants.APP_COPYRIGHT_YEAR, "developerName": constants.APP_DEVELOPERS})
		elif selected==menuItemsStore.getRef("connect"):
			connectDialog = views.connect.Dialog()
			connectDialog.Initialize()
			ret = connectDialog.Show()
