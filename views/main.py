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
import keymap

import constants
import errorCodes
import globalVars
import menuItemsStore

from logging import getLogger
import simpleDialog
from .base import *

import views.connect
import views.viewComment
import views.viewBroadcaster
import views.viewHistory
import views.viewFavorites
import views.accountManager
import views.changeDevice
import views.settings
import views.indicatorSoundSettings
import views.commentReplace
import views.userNamereplace
import webbrowser
import constants
import subprocess

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
		self.events=Events(self,self.identifier)
		title=constants.APP_NAME
		super().Initialize(
			title,
			self.app.config.getint(self.identifier,"sizeX",600),
			self.app.config.getint(self.identifier,"sizeY",540),
			self.app.config.getint(self.identifier,"positionX"),
			self.app.config.getint(self.identifier,"positionY")
		)
		self.InstallMenuEvent(Menu(self.identifier),self.events.OnMenuSelect)
		self.createStartScreen()

	def createStartScreen(self):
		self.hFrame.SetMinSize((600,540))

		#タイトル表示
		self.titleText = self.creator.staticText("TCV",sizerFlag=wx.CENTER | wx.ALL, margin=20)
		font = self.titleText.GetFont()
		font.SetPointSize(60)
		font.SetNumericWeight(1000)
		self.titleText.SetFont(font)

		#メニューボタン
		self.connectButton = self.creator.button(_("接続") + "(Ctrl+N)", self.events.connect, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.viewHistoryButton = self.creator.button(_("接続履歴を開く") + "(Ctrl+H)", self.events.viewHistory, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.viewFavoritesButton = self.creator.button(_("お気に入り一覧を開く") + "(Ctrl+I)", self.events.viewFavorites, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.settingsButton = self.creator.button(_("設定"), self.events.settings, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.accountManagerButton = self.creator.button(_("アカウントマネージャを開く"), self.events.accountManager, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.helpButton = self.creator.button(_("ヘルプを表示"), None, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.exitButton = self.creator.button(_("プログラムの終了"), self.events.Exit, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
		self.hPanel.Layout()
		self.connectButton.SetFocus()

	def createMainView(self):
		self.keymap=keymap.KeymapHandler(defaultKeymap.defaultKeymap)
		self.commentListAcceleratorTable=self.keymap.GetTable("commentList")
		self.commentBodyAcceleratorTable=self.keymap.GetTable("commentBody")
		self.userInfoAcceleratorTable=self.keymap.GetTable("userInfo")

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.VERTICAL, style=wx.EXPAND | wx.ALL, proportion=2)
		self.c1=creator.GetSizer()
		self.commentList, self.commentListStatic = creator.listCtrl(_("コメント一覧"), None, wx.LC_REPORT, size=(-1,100), sizerFlag=wx.EXPAND, proportion=1)
		self.commentList.InsertColumn(0, _("名前"))
		self.commentList.InsertColumn(1, _("投稿"))
		self.commentList.InsertColumn(2, _("時刻"))
		self.commentList.InsertColumn(3, _("ユーザ名"))
		self.commentList.loadColumnInfo(self.identifier,"commentList")

		self.commentList.SetAcceleratorTable(self.commentListAcceleratorTable)
		self.commentList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.events.commentSelected)
		self.commentList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.events.commentSelected)
		self.commentList.Bind(wx.EVT_CONTEXT_MENU, self.events.commentContextMenu)

		self.events.commentSelected(None)

		self.selectAccount, self.selectAccountstatic = self.creator.combobox(_("コメント投稿アカウント"), [], textLayout=None)
		for i in globalVars.app.accountManager.tokens:
			self.selectAccount.Append("%s(%s)" %(i["user"]["screen_id"], i["user"]["name"]))
		self.selectAccount.SetSelection(0)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.HORIZONTAL, style=wx.LEFT | wx.RIGHT | wx.EXPAND)
		self.commentBodyEdit, self.commentBodyStatic = creator.inputbox(_("コメント内容"), None, "", wx.TE_MULTILINE|wx.TE_DONTWRAP | wx.TE_NOHIDESEL , sizerFlag=wx.EXPAND, proportion=1, textLayout=None)
		self.commentBodyEdit.SetAcceleratorTable(self.commentBodyAcceleratorTable)
		self.commentBodyEdit.hideScrollBar(wx.VERTICAL | wx.HORIZONTAL)
		self.commentSend = creator.button(_("送信"), self.events.postComment, sizerFlag=wx.ALIGN_BOTTOM | wx.ALL)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.HORIZONTAL, space=20, style=wx.EXPAND | wx.ALL, proportion=1)
		self.liveInfo, self.liveInfoStatic = creator.listbox(_("ライブ情報"), proportion=1, size=(100,100), sizerFlag=wx.EXPAND, textLayout=wx.VERTICAL)
		self.liveInfo.SetAcceleratorTable(self.userInfoAcceleratorTable)
		self.liveInfo.Bind(wx.EVT_CONTEXT_MENU, self.events.userInfoContextMenu)
		self.liveInfo.Bind(wx.EVT_RIGHT_DOWN,self.liveInfo.setCursorOnMouse)
		self.itemList, self.itemListStatic = creator.listbox(_("アイテム"), proportion=1, size=(100,100), sizerFlag=wx.EXPAND, textLayout=wx.VERTICAL)

		self.hPanel.Layout()
		self.commentList.SetFocus()

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニューの大項目を作る
		self.hFileMenu=wx.Menu()
		self.hPlayMenu=wx.Menu()
		self.hCommentMenu=wx.Menu()
		self.hLiveMenu=wx.Menu()
		self.hSettingsMenu=wx.Menu()
		self.hHelpMenu=wx.Menu()
		self.hCommentListContextMenu=wx.Menu()

		#メニューの中身
		#ファイルメニュー
		self.RegisterMenuCommand(self.hFileMenu,"connect",_("接続") + "(&C) ...")
		self.RegisterMenuCommand(self.hFileMenu,"viewHistory",_("接続履歴を開く") + "(&H) ...")
		self.RegisterMenuCommand(self.hFileMenu,"viewFavorites",_("お気に入り一覧を開く") + "(&F) ...")
		self.RegisterMenuCommand(self.hFileMenu,"disconnect",_("切断") + "(&D)")
		self.RegisterMenuCommand(self.hFileMenu,"exit",_("終了") + "(&Q)")
		#再生メニュー
		self.RegisterMenuCommand(self.hPlayMenu,"play",_("再生") + "(&P)")
		self.RegisterMenuCommand(self.hPlayMenu,"stop",_("停止") + "(&S)")
		self.RegisterMenuCommand(self.hPlayMenu,"volumeUp",_("音量を上げる") + "(&U)")
		self.RegisterMenuCommand(self.hPlayMenu,"volumeDown",_("音量を下げる") + "(&D)")
		self.RegisterMenuCommand(self.hPlayMenu,"resetVolume",_("音量を１００％に設定") + "(&R)")
		self.RegisterMenuCommand(self.hPlayMenu,"changeDevice",_("再生デバイスを変更") + "(&C)")
		#コメントメニュー
		self.RegisterMenuCommand(self.hCommentMenu, "copyComment", _("選択中のコメントをコピー") + "(&C)")
		self.RegisterMenuCommand(self.hCommentMenu,"viewComment",_("コメントの詳細を表示") + "(&V) ...")
		self.RegisterMenuCommand(self.hCommentMenu,"replyToSelectedComment",_("選択中のコメントに返信") + "(&R)")
		self.RegisterMenuCommand(self.hCommentMenu,"deleteSelectedComment",_("選択中のコメントを削除") + "(&D)")
		self.RegisterMenuCommand(self.hCommentMenu,"replyToBroadcaster",_("配信者に返信") + "(&B)")
		#ライブメニュー
		self.RegisterMenuCommand(self.hLiveMenu,"viewBroadcaster",_("配信者の情報を表示") + "(&B) ...")
		self.RegisterMenuCommand(self.hLiveMenu,"openLive",_("このライブをブラウザで開く") + "(&O)")
		self.RegisterMenuCommand(self.hLiveMenu,"addFavorites",_("お気に入りに追加") + "(&A) ...")
		#設定メニュー
		self.RegisterMenuCommand(self.hSettingsMenu,"settings",_("設定") + "(&S) ...")
		self.RegisterMenuCommand(self.hSettingsMenu, "indicatorSoundSettings", _("効果音設定") + "(&F)")
		self.RegisterMenuCommand(self.hSettingsMenu,"commentReplace",_("コメント文字列置換設定") + "(&R) ...")
		self.RegisterMenuCommand(self.hSettingsMenu,"userNameReplace",_("表示名置換設定") + "(&N) ...")
		self.RegisterMenuCommand(self.hSettingsMenu,"accountManager",_("アカウントマネージャ") + "(&M) ...")
		self.RegisterMenuCommand(self.hSettingsMenu, "sapiSetting", _("SAPI設定を開く") + "(&A) ...")
		#ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu,"versionInfo",_("バージョン情報") + "(&V) ...")
		self.RegisterMenuCommand(self.hHelpMenu, "checkforUpdate", _("更新を確認") + "(&C) ...")

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル") + "(&F)")
		self.hMenuBar.Append(self.hPlayMenu,_("再生") + "(&P)")
		self.hMenuBar.Append(self.hCommentMenu,_("コメント") + "(&C)")
		self.hMenuBar.Append(self.hLiveMenu,_("ライブ") + "(&L)")
		self.hMenuBar.Append(self.hSettingsMenu,_("設定") + "(&S)")
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ") + "(&H)")
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る

		#特殊なイベントと思われる
		if selected<10 and selected>0:
			event.Skip()
			return

		if not self.parent.menu.IsEnable(selected):
			event.Skip()
			return

		#終了
		if selected==menuItemsStore.getRef("exit"):
			self.parent.hFrame.Close()
		#バージョン情報
		elif selected==menuItemsStore.getRef("versionInfo"):
			simpleDialog.dialog(_("バージョン情報"), _("%s(%s) Version %s.\nCopyright (C) %s %s") %(constants.APP_NAME, constants.APP_FULL_NAME,constants.APP_VERSION, constants.APP_COPYRIGHT_YEAR, constants.APP_DEVELOPERS))
		#接続
		elif selected==menuItemsStore.getRef("connect"):
			self.connect()
		#切断
		elif selected==menuItemsStore.getRef("disconnect"):
			globalVars.app.Manager.disconnect()
		#履歴
		elif selected==menuItemsStore.getRef("viewHistory"):
			self.viewHistory()
		#お気に入り
		elif selected==menuItemsStore.getRef("viewFavorites"):
			self.viewFavorites()
		#コメントのコピー
		elif selected == menuItemsStore.getRef("copyComment"):
			globalVars.app.Manager.copyComment()
		#コメントの詳細を表示
		elif selected==menuItemsStore.getRef("viewComment"):
			viewCommentDialog = views.viewComment.Dialog(globalVars.app.Manager.connection.comments[self.parent.commentList.GetFocusedItem()])
			viewCommentDialog.Initialize()
			viewCommentDialog.Show()
		#選択中のコメントに返信
		elif selected==menuItemsStore.getRef("replyToSelectedComment"):
			self.parent.commentBodyEdit.SetValue("@" + globalVars.app.Manager.connection.comments[self.parent.commentList.GetFocusedItem()]["from_user"]["screen_id"] + " ")
			self.parent.commentBodyEdit.SetInsertionPointEnd()
			self.parent.commentBodyEdit.SetFocus()
		#配信者に返信
		elif selected==menuItemsStore.getRef("replyToBroadcaster"):
			self.parent.commentBodyEdit.SetValue("@" + globalVars.app.Manager.connection.movieInfo["broadcaster"]["screen_id"] + " ")
			self.parent.commentBodyEdit.SetInsertionPointEnd()
			self.parent.commentBodyEdit.SetFocus()
		#コメントの削除
		elif selected==menuItemsStore.getRef("deleteSelectedComment"):
			dlg=simpleDialog.yesNoDialog(_("確認"),_("選択中のコメントを削除しますか？"))
			if dlg==wx.ID_NO:
				return
			globalVars.app.Manager.deleteComment()
		#お気に入りに追加
		elif selected==menuItemsStore.getRef("addFavorites"):
			if globalVars.app.Manager.connection.userId in globalVars.app.Manager.favorites:
				simpleDialog.errorDialog(_("すでに登録されています。"))
				return
			dlg=simpleDialog.yesNoDialog(_("確認"),_("%sのライブをお気に入りに追加しますか？") %(globalVars.app.Manager.connection.userId))
			if dlg==wx.ID_NO:
				return
			globalVars.app.Manager.addFavorites()
		#配信者の情報
		elif selected==menuItemsStore.getRef("viewBroadcaster"):
			viewBroadcasterDialog = views.viewBroadcaster.Dialog(globalVars.app.Manager.connection.movieInfo["broadcaster"])
			viewBroadcasterDialog.Initialize()
			viewBroadcasterDialog.Show()
		#ブラウザで開く
		elif selected==menuItemsStore.getRef("openLive"):
			globalVars.app.Manager.openLiveWindow()
		#設定
		elif selected==menuItemsStore.getRef("settings"):
			self.settings()
		#効果音設定
		elif selected == menuItemsStore.getRef("indicatorSoundSettings"):
			self.indicatorSoundSettings()
		#コメント文字列置換設定
		elif selected==menuItemsStore.getRef("commentReplace"):
			self.commentReplace()
		#表示名置換設定
		elif selected==menuItemsStore.getRef("userNameReplace"):
			self.userNameReplace()
		#アカウントマネージャ
		elif selected==menuItemsStore.getRef("accountManager"):
			self.accountManager()
		#SAPI設定を開く
		elif selected == menuItemsStore.getRef("sapiSetting"):
			file = os.path.join(os.getenv("windir"), "SysWOW64", "Speech", "SpeechUX", "sapi.cpl")
			if os.path.exists(file) == False:
				file = file.replace("syswow64", "system32")
			os.system(file)
		#コメント送信（ホットキー）
		elif selected==menuItemsStore.getRef("postComment"):
			self.postComment(None)
		#再生
		elif selected==menuItemsStore.getRef("play"):
			globalVars.app.Manager.play()
		#停止
		elif selected==menuItemsStore.getRef("stop"):
			globalVars.app.Manager.stop()
		#音量を上げる
		elif selected==menuItemsStore.getRef("volumeUp"):
			globalVars.app.Manager.volumeUp()
		#音量を下げる
		elif selected==menuItemsStore.getRef("volumeDown"):
			globalVars.app.Manager.volumeDown()
		#音量のリセット
		elif selected==menuItemsStore.getRef("resetVolume"):
			globalVars.app.Manager.resetVolume()
		#再生デバイス変更
		elif selected==menuItemsStore.getRef("changeDevice"):
			changeDeviceDialog = views.changeDevice.Dialog()
			changeDeviceDialog.Initialize()
			ret = changeDeviceDialog.Show()
			if ret==wx.ID_CANCEL: return
			globalVars.app.Manager.changeDevice(changeDeviceDialog.GetData())
			return
		#音声停止
		elif selected==menuItemsStore.getRef("silence"):
			try:
				globalVars.app.speech.silence()
			except AttributeError:
				pass
		#エラーログを開く
		elif selected==menuItemsStore.getRef("viewErrorLog"):
			subprocess.Popen(["start", ".\\errorLog.txt"], shell=True)
		#更新を確認
		elif selected==menuItemsStore.getRef("checkforUpdate"):
			globalVars.update.update(False)
		#コメントリストのコンテキストメニューを開く
		elif selected==menuItemsStore.getRef("openCommentListContextMenu"):
				return self.commentContextMenu()
		#URLを開く
		elif selected >= constants.MENU_URL_FIRST:
			obj = event.GetEventObject()
			webbrowser.open(obj.GetLabel(selected))
		#ユーザー情報のコンテキストメニューを開く
		elif selected==menuItemsStore.getRef("openUserInfoContextMenu"):
			return self.userInfoContextMenu()


	def postComment(self, event):
		commentBody = self.parent.commentBodyEdit.GetValue()
		result = globalVars.app.Manager.postComment(commentBody, self.parent.selectAccount.GetSelection())
		if result == True:
			self.parent.commentBodyEdit.Clear()

	def Exit(self, event=None):
		if hasattr(self.parent,"commentList"):
			self.parent.commentList.saveColumnInfo()
		for i in globalVars.app.Manager.timers:
			if i.IsRunning() == True:
				i.Stop()
		if event and isinstance(event,wx.CloseEvent):
			super().Exit(event)
		else:
			self.parent.hFrame.Close()

	def connect(self, event=None):
		connectDialog = views.connect.Dialog()
		connectDialog.Initialize()
		ret = connectDialog.Show()
		if ret==wx.ID_CANCEL: return
		user = str(connectDialog.GetValue())
		globalVars.app.Manager.connect(user)
		return

	def viewHistory(self, event=None):
		if len(globalVars.app.Manager.history) == 0:
			simpleDialog.errorDialog(_("接続履歴がありません。"))
			return
		viewHistoryDialog = views.viewHistory.Dialog()
		viewHistoryDialog.Initialize()
		ret = viewHistoryDialog.Show()
		if ret==wx.ID_CANCEL: return
		globalVars.app.Manager.connect(globalVars.app.Manager.history[viewHistoryDialog.GetValue()])
		return

	def viewFavorites(self, event=None):
		if len(globalVars.app.Manager.favorites) == 0:
			simpleDialog.errorDialog(_("お気に入りライブが登録されていません。"))
			return
		viewFavoritesDialog = views.viewFavorites.Dialog()
		viewFavoritesDialog.Initialize()
		ret = viewFavoritesDialog.Show()
		if ret==wx.ID_CANCEL: return
		globalVars.app.Manager.connect(globalVars.app.Manager.favorites[viewFavoritesDialog.GetValue()])
		return

	def accountManager(self, event=None):
		accountManager = views.accountManager.Dialog()
		accountManager.Initialize()
		accountManager.Show()

	def settings(self, event=None):
		settings = views.settings.settingsDialog()
		settings.Initialize()
		settings.Show()

	def indicatorSoundSettings(self):
		d = views.indicatorSoundSettings.Dialog()
		d.Initialize()
		d.show()

	def commentReplace(self):
		commentReplace = views.commentReplace.Dialog()
		commentReplace.Initialize()
		result = commentReplace.Show()
		if result == wx.ID_CANCEL:
			return
		globalVars.app.config.remove_section("commentReplaceBasic")
		globalVars.app.config.remove_section("commentReplaceReg")
		for i in commentReplace.GetValue():
			if i[2] == _("標準"):
				globalVars.app.config["commentReplaceBasic"][i[0]] = i[1]
			elif i[2] == _("正規表現"):
				globalVars.app.config["commentReplaceReg"][i[0]] = i[1]
		globalVars.app.Manager.refreshReplaceSettings()

	def userNameReplace(self):
		userNameReplace = views.userNamereplace.Dialog()
		userNameReplace.Initialize()
		result = userNameReplace.Show()
		if result == wx.ID_CANCEL:
			return
		globalVars.app.config.remove_section("nameReplace")
		for i in userNameReplace.GetData():
			globalVars.app.config["nameReplace"][i[0]] = i[1]
		globalVars.app.Manager.refreshReplaceSettings()

	def commentSelected(self, event):
		if event == None:
			enable = False
		else:
			enable = True
		self.parent.menu.EnableMenu("copyComment", enable)
		self.parent.menu.EnableMenu("viewComment", enable)
		self.parent.menu.EnableMenu("replyToSelectedComment", enable)
		self.parent.menu.EnableMenu("deleteSelectedComment", enable)

	#コメント一覧でのコンテキストメニュー
	#Shift+F10の場合はメニューイベント経由の為event=Noneとなる
	def commentContextMenu(self, event=None):
		if self.parent.commentList.GetFocusedItem() < 0:
			return
		contextMenu = wx.Menu()
		self.parent.menu.RegisterMenuCommand(contextMenu,"replyToSelectedComment",_("選択中のコメントに返信") + "(&R)")
		self.parent.menu.RegisterMenuCommand(contextMenu,"deleteSelectedComment",_("選択中のコメントを削除") + "(&D)")
		self.parent.menu.RegisterMenuCommand(contextMenu,"viewComment",_("コメントの詳細を表示") + "(&V) ...")
		urls = list(globalVars.app.Manager.connection.comments[self.parent.commentList.GetFocusedItem()]["urls"])
		for i, j in zip(urls, range(len(urls))):
			contextMenu.Append(constants.MENU_URL_FIRST + j, i.group())
		pos=wx.DefaultPosition
		self.parent.commentList.PopupMenu(contextMenu,event)

	def userInfoContextMenu(self,event=None):
		focusedItem = self.parent.liveInfo.GetSelection()
		if focusedItem != self.parent.liveInfo.GetCount() - 1:
			return
		contextMenu = wx.Menu()
		self.parent.menu.RegisterMenuCommand(contextMenu,"replyToBroadcaster",_("配信者に返信") + "(&B)")
		self.parent.menu.RegisterMenuCommand(contextMenu,"viewBroadcaster",_("配信者の情報を表示") + "(&B) ...")
		self.parent.menu.RegisterMenuCommand(contextMenu,"addFavorites",_("お気に入りに追加") + "(&A) ...")
		self.parent.liveInfo.PopupMenu(contextMenu,event)
