# -*- coding: utf-8 -*-
#main view
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import logging
import os
import sys

from wx.core import EnableTopLevelWindows
import wx
import re
import ctypes
import pywintypes
import ConfigManager
import keymap
import hotkeyHandler
from views import globalKeyConfig

import constants
import errorCodes
import globalVars
import menuItemsStore

from logging import getLogger
import simpleDialog
from .base import *

import views.versionDialog
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
import views.changeSpeechOutput
import webbrowser
import constants

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
		self.applyHotKey()

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
		self.helpButton = self.creator.button(_("ヘルプを表示"), self.events.help, size=(540,-1), sizerFlag=wx.ALIGN_CENTER | wx.ALL)
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
		self.commentList, self.commentListStatic = creator.listCtrl(_("コメント一覧"), None, wx.LC_REPORT | wx.BORDER_RAISED, size=(-1,100), sizerFlag=wx.EXPAND, proportion=1)
		self.commentList.InsertColumn(0, _("名前"),width=200)
		self.commentList.InsertColumn(1, _("投稿"),width=370)
		self.commentList.InsertColumn(2, _("時刻"),width=150)
		self.commentList.InsertColumn(3, _("ユーザ名"),width=200	)
		self.commentList.loadColumnInfo(self.identifier,"commentList")

		self.commentList.SetAcceleratorTable(self.commentListAcceleratorTable)
		self.commentList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.events.commentSelected)
		self.commentList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.events.commentSelected)
		self.commentList.Bind(wx.EVT_CONTEXT_MENU, self.events.commentContextMenu)
		self.commentList.Bind(wx.EVT_SET_FOCUS, self.events.commentSelected)
		self.commentList.Bind(wx.EVT_KILL_FOCUS, self.events.commentSelected)

		self.events.commentSelected(None)

		self.selectAccount, self.selectAccountstatic = self.creator.combobox(_("コメント投稿アカウント"), [], textLayout=None, sizerFlag=wx.LEFT,margin=20)
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


	def applyHotKey(self):
		self.hotkey = hotkeyHandler.HotkeyHandler(None,hotkeyHandler.HotkeyFilter().SetDefault())
		if self.hotkey.addFile(constants.KEYMAP_FILE_NAME,["HOTKEY"])==errorCodes.OK:
			errors=self.hotkey.GetError("HOTKEY")
			if errors:
				tmp=_(constants.KEYMAP_FILE_NAME+"で設定されたホットキーが正しくありません。キーの重複、存在しないキー名の指定、使用できないキーパターンの指定などが考えられます。以下のキーの設定内容をご確認ください。\n\n")
				for v in errors:
					tmp+=v+"\n"
				dialog(_("エラー"),tmp)
			self.hotkey.Set("HOTKEY",self.hFrame)

	def Clear(self):
		if hasattr(self,"commentList") and self.commentList:
			self.commentList.saveColumnInfo()
			self.commentList = None
		super().Clear()

class Menu(BaseMenu):
	def Apply(self,target):
		"""指定されたウィンドウに、メニューを適用する。"""

		#メニュー内容をいったんクリア
		self.hMenuBar=wx.MenuBar()

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
		self.RegisterMenuCommand(self.hFileMenu,
			["CONNECT", "VIEW_HISTORY", "VIEW_FAVORITES", "DISCONNECT", "EXIT"])
		#再生メニュー
		self.RegisterMenuCommand(self.hPlayMenu,
			["PLAY", "STOP", "VOLUME_UP", "VOLUME_DOWN", "RESET_VOLUME", "CHANGE_DEVICE"])
		#コメントメニュー
		self.RegisterMenuCommand(self.hCommentMenu,
			["COPY_COMMENT", "VIEW_COMMENT", "REPLY2SELECTED_COMMENT", "DELETE_SELECTED_COMMENT", "SELECT_ALL_COMMENT", "REPLY2BROADCASTER"])
		#ライブメニュー
		self.RegisterMenuCommand(self.hLiveMenu, ["VIEW_BROADCASTER", "OPEN_LIVE", "ADD_FAVORITES"])
		#設定メニュー
		self.RegisterMenuCommand(self.hSettingsMenu,
			["SETTING", "SET_KEYMAP", "SET_HOTKEY", "INDICATOR_SOUND_SETTING", "COMMENT_REPLACE", "USER_NAME_REPLACE", "ACCOUNT_MANAGER", "SAPI_SETTING", "CHANGE_SPEECH_OUTPUT"])
		#ヘルプメニュー
		self.RegisterMenuCommand(self.hHelpMenu, ["HELP", "VERSION_INFO", "CHECK4UPDATE"])

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

		#特殊なイベントと思われる
		if selected<10 and selected>0:
			event.Skip()
			return

		if not self.parent.menu.IsEnable(selected):
			event.Skip()
			return

		#終了
		if selected==menuItemsStore.getRef("EXIT"):
			self.parent.hFrame.Close()
		#バージョン情報
		elif selected==menuItemsStore.getRef("SET_KEYMAP"):
			if self.setKeymap("MainView",_("ショートカットキーの設定"),filter=keymap.KeyFilter().SetDefault(False,False)):
				#ショートカットキーの変更適用とメニューバーの再描画
				self.parent.menu.InitShortcut()
				self.parent.menu.ApplyShortcut(self.parent.hFrame)
				self.parent.menu.Apply(self.parent.hFrame)
		elif selected==menuItemsStore.getRef("SET_HOTKEY"):
			if self.setKeymap("HOTKEY",_("グローバルホットキーの設定"), self.parent.hotkey,filter=self.parent.hotkey.filter):
				#変更適用
				self.parent.hotkey.UnSet("HOTKEY",self.parent.hFrame)
				self.parent.applyHotKey()
		elif selected==menuItemsStore.getRef("VERSION_INFO"):
			views.versionDialog.versionDialog()
		#接続
		elif selected==menuItemsStore.getRef("CONNECT"):
			self.connect()
		#切断
		elif selected==menuItemsStore.getRef("DISCONNECT"):
			globalVars.app.Manager.disconnect()
		#履歴
		elif selected==menuItemsStore.getRef("VIEW_HISTORY"):
			self.viewHistory()
		#お気に入り
		elif selected==menuItemsStore.getRef("VIEW_FAVORITES"):
			self.viewFavorites()
		#コメントのコピー
		elif selected == menuItemsStore.getRef("COPY_COMMENT"):
			globalVars.app.Manager.copyComment()
		#コメントの詳細を表示
		elif selected==menuItemsStore.getRef("VIEW_COMMENT"):
			viewCommentDialog = views.viewComment.Dialog(globalVars.app.Manager.connection.comments[self.parent.commentList.GetFocusedItem()])
			viewCommentDialog.Initialize()
			viewCommentDialog.Show()
		#選択中のコメントに返信
		elif selected==menuItemsStore.getRef("REPLY2SELECTED_COMMENT"):
			self.parent.commentBodyEdit.SetValue("@" + globalVars.app.Manager.connection.comments[self.parent.commentList.GetFocusedItem()]["from_user"]["screen_id"] + " ")
			self.parent.commentBodyEdit.SetInsertionPointEnd()
			self.parent.commentBodyEdit.SetFocus()
		#全てのコメントを選択
		elif selected == menuItemsStore.getRef("SELECT_ALL_COMMENT"):
			self.selectAllComment()
		#配信者に返信
		elif selected==menuItemsStore.getRef("REPLY2BROADCASTER"):
			self.parent.commentBodyEdit.SetValue("@" + globalVars.app.Manager.connection.movieInfo["broadcaster"]["screen_id"] + " ")
			self.parent.commentBodyEdit.SetInsertionPointEnd()
			self.parent.commentBodyEdit.SetFocus()
		#コメントの削除
		elif selected==menuItemsStore.getRef("DELETE_SELECTED_COMMENT"):
			dlg=simpleDialog.yesNoDialog(_("確認"),_("選択中のコメントを削除しますか？"))
			if dlg==wx.ID_NO:
				return
			globalVars.app.Manager.deleteComment()
		#お気に入りに追加
		elif selected==menuItemsStore.getRef("ADD_FAVORITES"):
			if globalVars.app.Manager.connection.userId in globalVars.app.Manager.favorites:
				simpleDialog.errorDialog(_("すでに登録されています。"))
				return
			dlg=simpleDialog.yesNoDialog(_("確認"),_("%sのライブをお気に入りに追加しますか？") %(globalVars.app.Manager.connection.userId))
			if dlg==wx.ID_NO:
				return
			globalVars.app.Manager.addFavorites()
		#配信者の情報
		elif selected==menuItemsStore.getRef("VIEW_BROADCASTER"):
			viewBroadcasterDialog = views.viewBroadcaster.Dialog(globalVars.app.Manager.connection.movieInfo["broadcaster"])
			viewBroadcasterDialog.Initialize()
			viewBroadcasterDialog.Show()
		#ブラウザで開く
		elif selected==menuItemsStore.getRef("OPEN_LIVE"):
			globalVars.app.Manager.openLiveWindow()
		#設定
		elif selected==menuItemsStore.getRef("SETTING"):
			self.settings()
		#効果音設定
		elif selected == menuItemsStore.getRef("INDICATOR_SOUND_SETTING"):
			self.indicatorSoundSettings()
		#コメント文字列置換設定
		elif selected==menuItemsStore.getRef("COMMENT_REPLACE"):
			self.commentReplace()
		#表示名置換設定
		elif selected==menuItemsStore.getRef("USER_NAME_REPLACE"):
			self.userNameReplace()
		#アカウントマネージャ
		elif selected==menuItemsStore.getRef("ACCOUNT_MANAGER"):
			self.accountManager()
		#SAPI設定を開く
		elif selected == menuItemsStore.getRef("SAPI_SETTING"):
			file = os.path.join(os.getenv("windir"), "SysWOW64", "Speech", "SpeechUX", "sapi.cpl")
			if os.path.exists(file) == False:
				file = file.replace("syswow64", "system32")
			os.system(file)
		#読み上げ出力先の変更
		elif selected == menuItemsStore.getRef("CHANGE_SPEECH_OUTPUT"):
			d = views.changeSpeechOutput.Dialog()
			d.Initialize()
			d.Show()
		#コメント送信（ホットキー）
		elif selected==menuItemsStore.getRef("POST_COMMENT"):
			self.postComment(None)
		#再生
		elif selected==menuItemsStore.getRef("PLAY"):
			globalVars.app.Manager.play()
		#停止
		elif selected==menuItemsStore.getRef("STOP"):
			globalVars.app.Manager.stop()
		#音量を上げる
		elif selected==menuItemsStore.getRef("VOLUME_UP"):
			globalVars.app.Manager.volumeUp()
		#音量を下げる
		elif selected==menuItemsStore.getRef("VOLUME_DOWN"):
			globalVars.app.Manager.volumeDown()
		#音量のリセット
		elif selected==menuItemsStore.getRef("RESET_VOLUME"):
			globalVars.app.Manager.resetVolume()
		#再生デバイス変更
		elif selected==menuItemsStore.getRef("CHANGE_DEVICE"):
			changeDeviceDialog = views.changeDevice.Dialog()
			changeDeviceDialog.Initialize()
			ret = changeDeviceDialog.Show()
			if ret==wx.ID_CANCEL: return
			globalVars.app.Manager.changeDevice(changeDeviceDialog.GetData())
			return
		#音声停止
		elif selected==menuItemsStore.getRef("SILENCE"):
			try:
				globalVars.app.speech.silence()
			except AttributeError:
				pass
		#ヘルプを開く
		elif selected == menuItemsStore.getRef("HELP"):
			self.help()
		#更新を確認
		elif selected==menuItemsStore.getRef("CHECK4UPDATE"):
			globalVars.update.update(False)
		#コメントリストのコンテキストメニューを開く
		elif selected==menuItemsStore.getRef("POPUP_OPEN_COMMENT"):
				return self.commentContextMenu()
		#URLを開く
		elif selected >= constants.MENU_URL_FIRST:
			obj = event.GetEventObject()
			webbrowser.open(obj.GetLabel(selected))
		#ユーザー情報のコンテキストメニューを開く
		elif selected==menuItemsStore.getRef("POPUP_OPEN_USER_INFO"):
			return self.userInfoContextMenu()


	def postComment(self, event):
		commentBody = self.parent.commentBodyEdit.GetValue()
		result = globalVars.app.Manager.postComment(commentBody, self.parent.selectAccount.GetSelection())
		if result == True:
			self.parent.commentBodyEdit.Clear()

	def Exit(self, event=None):
		if hasattr(self.parent,"commentList") and self.parent.commentList:
			self.parent.commentList.saveColumnInfo()
		try:
			for i in globalVars.app.Manager.timers:
				if i.IsRunning() == True:
					i.Stop()
			globalVars.app.Manager.connection.running = False
		except:
			pass
		if event and isinstance(event,wx.CloseEvent):
			super().Exit(event)
		else:
			self.parent.hFrame.Close()

	def connect(self, event=None):
		self.parent.Clear()
		connectDialog = views.connect.Dialog()
		connectDialog.Initialize()
		ret = connectDialog.Show()
		if ret==wx.ID_CANCEL:
			self.parent.createStartScreen()
			return
		user = str(connectDialog.GetValue())
		globalVars.app.Manager.connect(user)
		return

	def viewHistory(self, event=None):
		if len(globalVars.app.Manager.history) == 0:
			simpleDialog.errorDialog(_("接続履歴がありません。"))
			return
		self.parent.Clear()
		viewHistoryDialog = views.viewHistory.Dialog()
		viewHistoryDialog.Initialize()
		ret = viewHistoryDialog.Show()
		if ret==wx.ID_CANCEL:
			self.parent.createStartScreen()
			return
		globalVars.app.Manager.connect(globalVars.app.Manager.history[viewHistoryDialog.GetValue()])
		return

	def viewFavorites(self, event=None):
		if len(globalVars.app.Manager.favorites) == 0:
			simpleDialog.errorDialog(_("お気に入りライブが登録されていません。"))
			return
		self.parent.Clear()
		viewFavoritesDialog = views.viewFavorites.Dialog()
		viewFavoritesDialog.Initialize()
		ret = viewFavoritesDialog.Show()
		if ret==wx.ID_CANCEL:
			self.parent.createStartScreen()
			return
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
		d.Show()

	def setKeymap(self, identifier,ttl, keymap=None,filter=None):
		if keymap:
			try:
				keys=keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		else:
			try:
				keys=self.parent.menu.keymap.map[identifier.upper()]
			except KeyError:
				keys={}
		keyData={}
		menuData={}
		for refName in defaultKeymap.defaultKeymap[identifier.upper()].keys():
			title=menuItemsDic.getValueString(refName)
			if refName in keys:
				keyData[title]=keys[refName]
			else:
				keyData[title]=_("なし")
			menuData[title]=refName

		entries=[]
		for map in (self.parent.menu.keymap,self.parent.hotkey):
			for i in map.entries.keys():
				if identifier.upper()!=i:	#今回の変更対象以外のビューのものが対象
					entries.extend(map.entries[i])

		d=views.globalKeyConfig.Dialog(keyData,menuData,entries,filter)
		d.Initialize(ttl)
		if d.Show()==wx.ID_CANCEL: return False

		result={}
		keyData,menuData=d.GetValue()

		#キーマップの既存設定を置き換える
		newMap=ConfigManager.ConfigManager()
		newMap.read(constants.KEYMAP_FILE_NAME)
		for name,key in keyData.items():
			if key!=_("なし"):
				newMap[identifier.upper()][menuData[name]]=key
			else:
				newMap[identifier.upper()][menuData[name]]=""
		newMap.write()
		return True

	def commentReplace(self):
		commentReplace = views.commentReplace.Dialog()
		commentReplace.Initialize()
		result = commentReplace.Show()
		if result == wx.ID_CANCEL:
			return
		globalVars.app.config.remove_section("commentReplaceBasic")
		globalVars.app.config.remove_section("commentReplaceReg")
		for i in commentReplace.GetValue():
			if i[2] == False:
				globalVars.app.config["commentReplaceBasic"][i[0]] = i[1]
			elif i[2] == True:
				globalVars.app.config["commentReplaceReg"][i[0]] = i[1]
		globalVars.app.Manager.refreshReplaceSettings()

	def userNameReplace(self):
		userNameReplace = views.userNamereplace.Dialog()
		userNameReplace.Initialize()
		result = userNameReplace.Show()
		if result == wx.ID_CANCEL:
			return
		globalVars.app.config.remove_section("nameReplace")
		data = userNameReplace.GetData()[0]
		for i in data:
			globalVars.app.config["nameReplace"][i] = data[i]
		globalVars.app.Manager.refreshReplaceSettings()

	def help(self, event=None):
		if os.path.isfile(constants.README_FILE_NAME):
			os.startfile(constants.README_FILE_NAME)
		else:
			simpleDialog.errorDialog(_("readme.txtが見つかりません。"))

	def commentSelected(self, event):
		enable = self.parent.commentList.HasFocus() == True and self.parent.commentList.GetFirstSelected() >= 0
		self.parent.menu.EnableMenu("COPY_COMMENT", enable)
		self.parent.menu.EnableMenu("VIEW_COMMENT", enable)
		self.parent.menu.EnableMenu("REPLY2SELECTED_COMMENT", enable)
		self.parent.menu.EnableMenu("DELETE_SELECTED_COMMENT", enable)
		self.parent.menu.EnableMenu("SELECT_ALL_COMMENT", self.parent.commentList.HasFocus() == True)

	#コメント一覧でのコンテキストメニュー
	#Shift+F10の場合はメニューイベント経由の為event=Noneとなる
	def commentContextMenu(self, event=None):
		if self.parent.commentList.GetFocusedItem() < 0:
			return
		contextMenu = wx.Menu()
		self.parent.menu.RegisterMenuCommand(contextMenu,
				["REPLY2SELECTED_COMMENT", "DELETE_SELECTED_COMMENT", "VIEW_COMMENT"])
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
		self.parent.menu.RegisterMenuCommand(contextMenu,
			["REPLY2BROADCASTER", "VIEW_BROADCASTER", "ADD_FAVORITES"])
		self.parent.liveInfo.PopupMenu(contextMenu,event)

	def selectAllComment(self):
		for i in range(self.parent.commentList.GetItemCount()):
			self.parent.commentList.Select(i)

	def  focusChanged(self, event):
		import winsound
		winsound.Beep(440, 100)
		enable = self.parent.commentList.HasFocus()
		self.parent.menu.EnableMenu("COPY_COMMENT", enable)
		self.parent.menu.EnableMenu("VIEW_COMMENT", enable)
		self.parent.menu.EnableMenu("REPLY2SELECTED_COMMENT", enable)
		self.parent.menu.EnableMenu("DELETE_SELECTED_COMMENT", enable)
