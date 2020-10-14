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
import webbrowser
import constants

class MainView(BaseView):
	def __init__(self):
		super().__init__("mainView")
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
		self.createStartScreen()

	def createStartScreen(self):
		status = "現在、ライブに接続されていません。\nライブに接続するにはctrl+Nを押します。\n接続履歴から選択して接続するにはCtrl+Hを押します。\nお気に入りライブを表示するにはctrl+Iを押します。\n"
		self.statusEdit, self.statusStatic = self.creator.inputbox(_("状況"), None, status, wx.TE_READONLY | wx.TE_DONTWRAP | wx.TE_MULTILINE, 400)
		self.helpButton = self.creator.button(_("ヘルプを表示"), None)
		self.exitButton = self.creator.button(_("プログラムの終了"), self.events.Exit)

	def createMainView(self):
		self.keymap=keymap.KeymapHandler(defaultKeymap.defaultKeymap)
		self.commentListAcceleratorTable=self.keymap.GetTable("commentList")
		self.commentBodyAcceleratorTable=self.keymap.GetTable("commentBody")
		self.userInfoAcceleratorTable=self.keymap.GetTable("userInfo")

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.VERTICAL, style=wx.EXPAND | wx.ALL, proportion=1)
		self.commentList, self.commentListStatic = creator.listCtrl(_("コメント一覧"), None, wx.LC_REPORT,proportion=1, sizerFlag=wx.EXPAND)
		self.commentList.InsertColumn(0, _("名前"))
		self.commentList.InsertColumn(1, _("投稿"))
		self.commentList.InsertColumn(2, _("時刻"))
		self.commentList.InsertColumn(3, _("ユーザ名"))
		self.commentList.SetAcceleratorTable(self.commentListAcceleratorTable)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.HORIZONTAL, style=wx.EXPAND | wx.LEFT | wx.RIGHT)
		self.selectAccount, self.selectAccountstatic = creator.combobox(_("コメント投稿アカウント"), [], proportion=1, textLayout=None)
		for i in globalVars.app.accountManager.tokens:
			self.selectAccount.Append("%s(%s)" %(i["user"]["screen_id"], i["user"]["name"]))
		self.selectAccount.SetSelection(0)
		self.commentBodyEdit, self.commentBodyStatic = creator.inputbox(_("コメント内容"), None, "", wx.TE_MULTILINE|wx.TE_DONTWRAP, proportion=4, textLayout=None)
		self.commentBodyEdit.SetAcceleratorTable(self.commentBodyAcceleratorTable)
		self.commentSend = creator.button(_("送信"), self.events.postComment)

		creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,self.creator.GetSizer(), wx.HORIZONTAL, style=wx.EXPAND | wx.ALL)
		self.liveInfo, self.liveInfoStatic = creator.listbox(_("ライブ情報"), proportion=1, sizerFlag=wx.EXPAND | wx.RIGHT, textLayout=wx.VERTICAL, margin=20)
		self.liveInfo.SetAcceleratorTable(self.userInfoAcceleratorTable)
		self.itemList, self.itemListStatic = creator.listbox(_("アイテム"), proportion=1, sizerFlag=wx.EXPAND, textLayout=wx.VERTICAL)
		self.hPanel.Layout()

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
		self.RegisterMenuCommand(self.hFileMenu,"connect",_("接続(&C) ..."))
		self.RegisterMenuCommand(self.hFileMenu,"viewHistory",_("最近接続したライブに接続(&H) ..."))
		self.RegisterMenuCommand(self.hFileMenu,"viewFavorites",_("お気に入りライブに接続(&F) ..."))
		self.RegisterMenuCommand(self.hFileMenu,"disconnect",_("切断(&D)"))
		self.RegisterMenuCommand(self.hFileMenu,"exit",_("終了(&Q)"))
		#再生メニュー
		self.RegisterMenuCommand(self.hPlayMenu,"play",_("再生(&P)"))
		self.RegisterMenuCommand(self.hPlayMenu,"stop",_("停止(&S)"))
		self.RegisterMenuCommand(self.hPlayMenu,"volumeUp",_("音量を上げる(&U)"))
		self.RegisterMenuCommand(self.hPlayMenu,"volumeDown",_("音量を下げる(&D)"))
		self.RegisterMenuCommand(self.hPlayMenu,"resetVolume",_("音量を１００％に設定(&R)"))
		self.RegisterMenuCommand(self.hPlayMenu,"changeDevice",_("再生デバイスを変更(&C)"))
		#コメントメニュー
		self.RegisterMenuCommand(self.hCommentMenu,"viewComment",_("コメントの詳細を表示(&V) ..."))
		self.RegisterMenuCommand(self.hCommentMenu,"replyToSelectedComment",_("選択中のコメントに返信(&R)"))
		self.RegisterMenuCommand(self.hCommentMenu,"deleteSelectedComment",_("選択中のコメントを削除(&D)"))
		self.RegisterMenuCommand(self.hCommentMenu,"replyToBroadcaster",_("配信者に返信(&B)"))
		#ライブメニュー
		self.RegisterMenuCommand(self.hLiveMenu,"viewBroadcaster",_("配信者の情報を表示(&B) ..."))
		self.RegisterMenuCommand(self.hLiveMenu,"openLive",_("このライブをブラウザで開く(&O)"))
		self.RegisterMenuCommand(self.hLiveMenu,"addFavorites",_("お気に入りに追加(&A) ..."))
		#設定メニュー
		self.RegisterMenuCommand(self.hSettingsMenu,"basicSettings",_("基本設定(&G) ..."))
		self.RegisterMenuCommand(self.hSettingsMenu,"autoReadingSettings",_("自動読み上げの設定(&R) ..."))
		self.RegisterMenuCommand(self.hSettingsMenu,"accountManager",_("アカウントマネージャ(&M) ..."))
		#ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu,"versionInfo",_("バージョン情報(&V) ..."))
		self.RegisterMenuCommand(self.hHelpMenu,"viewErrorLog",_("エラーログを開く（開発用）"))

		#メニューバーの生成
		self.hMenuBar.Append(self.hFileMenu,_("ファイル(&F)"))
		self.hMenuBar.Append(self.hPlayMenu,_("再生(&P)"))
		self.hMenuBar.Append(self.hCommentMenu,_("コメント(&C)"))
		self.hMenuBar.Append(self.hLiveMenu,_("ライブ(&L)"))
		self.hMenuBar.Append(self.hSettingsMenu,_("設定(&S)"))
		self.hMenuBar.Append(self.hHelpMenu,_("ヘルプ(&H)"))
		target.SetMenuBar(self.hMenuBar)

class Events(BaseEvents):
	def OnMenuSelect(self,event):
		"""メニュー項目が選択されたときのイベントハンドら。"""
		#ショートカットキーが無効状態のときは何もしない
		if not self.parent.shortcutEnable:
			event.Skip()
			return

		selected=event.GetId()#メニュー識別しの数値が出る


		#終了
		if selected==menuItemsStore.getRef("exit"):
			self.Exit()
		#バージョン情報
		elif selected==menuItemsStore.getRef("versionInfo"):
			simpleDialog.dialog(_("バージョン情報"), _("%(appName)s Version %(versionNumber)s.\nCopyright (C) %(year)s %(developerName)s") %{"appName": constants.APP_NAME, "versionNumber": constants.APP_VERSION, "year":constants.APP_COPYRIGHT_YEAR, "developerName": constants.APP_DEVELOPERS})
		#接続
		elif selected==menuItemsStore.getRef("connect"):
			connectDialog = views.connect.Dialog()
			connectDialog.Initialize()
			ret = connectDialog.Show()
			if ret==wx.ID_CANCEL: return
			user = str(connectDialog.GetValue())
			user = user.replace("http://twitcasting.tv/", "")
			user = user.replace("https://twitcasting.tv/", "")
			if "/" in user:
				user = user[0:user.find("/")]
			globalVars.app.Manager.connect(user)
			return
		#切断
		elif selected==menuItemsStore.getRef("disconnect"):
			globalVars.app.Manager.disconnect()
		#履歴
		elif selected==menuItemsStore.getRef("viewHistory"):
			if len(globalVars.app.Manager.history) == 0:
				simpleDialog.errorDialog(_("接続履歴がありません。"))
				return
			viewHistoryDialog = views.viewHistory.Dialog()
			viewHistoryDialog.Initialize()
			ret = viewHistoryDialog.Show()
			if ret==wx.ID_CANCEL: return
			globalVars.app.Manager.connect(globalVars.app.Manager.history[viewHistoryDialog.GetValue()])
			return
		#お気に入り
		elif selected==menuItemsStore.getRef("viewFavorites"):
			if len(globalVars.app.Manager.favorites) == 0:
				simpleDialog.errorDialog(_("お気に入りライブが登録されていません。"))
				return
			viewFavoritesDialog = views.viewFavorites.Dialog()
			viewFavoritesDialog.Initialize()
			ret = viewFavoritesDialog.Show()
			if ret==wx.ID_CANCEL: return
			globalVars.app.Manager.connect(globalVars.app.Manager.favorites[viewFavoritesDialog.GetValue()])
			return
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
			webbrowser.open("http://twitcasting.tv/" + globalVars.app.Manager.connection.movieInfo["broadcaster"]["screen_id"])
		#アカウントマネージャ
		elif selected==menuItemsStore.getRef("accountManager"):
			accountManager = views.accountManager.Dialog([])
			accountManager.Initialize()
			accountManager.Show()
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
			import subprocess
			subprocess.Popen(["start", ".\\errorLog.txt"], shell=True)
		#コメントリストのコンテキストメニューを開く
		elif selected==menuItemsStore.getRef("openCommentListContextMenu"):
			contextMenu = wx.Menu()
			self.parent.menu.RegisterMenuCommand(contextMenu,"replyToSelectedComment",_("選択中のコメントに返信(&R)"))
			self.parent.menu.RegisterMenuCommand(contextMenu,"deleteSelectedComment",_("選択中のコメントを削除(&D)"))
			self.parent.menu.RegisterMenuCommand(contextMenu,"viewComment",_("コメントの詳細を表示(&V) ..."))
			urls = list(globalVars.app.Manager.connection.comments[self.parent.commentList.GetFocusedItem()]["urls"])
			for i, j in zip(urls, range(len(urls))):
				contextMenu.Append(constants.MENU_URL_FIRST + j, i.group())
			self.parent.hFrame.PopupMenu(contextMenu)
		#URLを開く
		elif selected >= constants.MENU_URL_FIRST:
			obj = event.GetEventObject()
			webbrowser.open(obj.GetLabel(selected))
		#ユーザー情報のコンテキストメニューを開く
		elif selected==menuItemsStore.getRef("openUserInfoContextMenu"):
			focusedItem = self.parent.liveInfo.GetSelection()
			if focusedItem != self.parent.liveInfo.GetCount() - 1:
				return
			contextMenu = wx.Menu()
			self.parent.menu.RegisterMenuCommand(contextMenu,"replyToBroadcaster",_("配信者に返信(&B)"))
			self.parent.menu.RegisterMenuCommand(contextMenu,"viewBroadcaster",_("配信者の情報を表示(&B) ..."))
			self.parent.menu.RegisterMenuCommand(contextMenu,"addFavorites",_("お気に入りに追加(&A) ..."))
			self.parent.hFrame.PopupMenu(contextMenu)


	def postComment(self, event):
		commentBody = self.parent.commentBodyEdit.GetValue()
		result = globalVars.app.Manager.postComment(commentBody, self.parent.selectAccount.GetSelection())
		if result == True:
			self.parent.commentBodyEdit.Clear()

	def Exit(self, event = None):
		for i in globalVars.app.Manager.timers:
			if i.IsRunning() == True:
				i.Stop()
		super().Exit()
