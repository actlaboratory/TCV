# -*- coding: utf-8 -*-
#アカウントマネージャ

import wx
from logging import getLogger

from .baseDialog import *
import globalVars
import views.ViewCreator
import simpleDialog
import datetime

class Dialog(BaseDialog):

	def __init__(self):
		super().__init__("accountManagerDialog")

	def Initialize(self):
		self.log.debug("created")
		self.app=globalVars.app
		super().Initialize(self.app.hMainView.hFrame,_("アカウントマネージャ"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		#情報の表示
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.hListCtrl,self.hListStatic=self.creator.listCtrl(_("アカウント"),None,wx.LC_REPORT,(600,300),wx.ALL|wx.ALIGN_CENTER_HORIZONTAL)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)
		self.refreshList()

		#処理ボタン
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.addButton=self.creator.button(_("追加"),self.add)
		self.setDefaultButton=self.creator.button(_("通信用アカウントとして設定"),self.setDefault)
		self.setDefaultButton.Enable(False)
		self.deleteButton=self.creator.button(_("削除"),self.delete)
		self.deleteButton.Enable(False)

		#ボタンエリア
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bClose=self.creator.cancelbutton(_("閉じる"),self.close)

	def refreshList(self):
		cursor = self.hListCtrl.GetFocusedItem()
		self.hListCtrl.DeleteAllItems()
		self.hListCtrl.InsertColumn(0,_("ユーザ名"),format=wx.LIST_FORMAT_LEFT,width=250)
		self.hListCtrl.InsertColumn(1,_("名前"),format=wx.LIST_FORMAT_LEFT,width=350)
		self.hListCtrl.InsertColumn(2,_("有効期限"),format=wx.LIST_FORMAT_LEFT,width=350)
		self.hListCtrl.InsertColumn(3,_("通信アカウント設定"),format=wx.LIST_FORMAT_LEFT,width=350)
		for i in globalVars.app.accountManager.tokens:
			if i["default"] == True:
				state = _("通信用アカウントとして設定済み")
			else:
				state = ""
			self.hListCtrl.Append([
				i["user"]["screen_id"],
				i["user"]["name"],
				datetime.datetime.fromtimestamp(i["expires_at"]).strftime("%Y/%m/%d"),
				state
			])
		if cursor >= 0:
			try:
				self.hListCtrl.GetItem(cursor).SetFocus()
			except:
				pass

	def ItemSelected(self,event):
		self.deleteButton.Enable(self.hListCtrl.GetFocusedItem()>=0)
		self.setDefaultButton.Enable(self.hListCtrl.GetFocusedItem()>=0 and globalVars.app.accountManager.isDefault(self.hListCtrl.GetFocusedItem()) == False)

	def GetValue(self):
		return self.config


	def add(self,event):
		q = simpleDialog.yesNoDialog(_("アカウントの追加"), _("ブラウザを開いてアカウントの認証作業を行います。よろしいですか？"))
		if q == wx.ID_NO:
			return
		globalVars.app.accountManager.add()
		self.refreshList()

	def setDefault(self, event):
		idx = self.hListCtrl.GetFocusedItem()
		globalVars.app.accountManager.setDefaultAccount(idx)
		self.refreshList()
		self.hListCtrl.SetFocus()

	def delete(self,event):
		idx = self.hListCtrl.GetFocusedItem()
		self.hListCtrl.DeleteItem(idx)
		globalVars.app.accountManager.deleteAccount(idx)
		self.setDefaultButton.Enable(False)
		self.deleteButton.Enable(False)

	def close(self, event = None):
		result = globalVars.app.accountManager.hasDefaultAccount()
		if result == False and self.hListCtrl.GetItemCount() > 0:
			simpleDialog.errorDialog(_("通信用アカウントが設定されていません。"))
			return
		else:
			self.wnd.Destroy()

	def OnClose(self, event):
		self.close()

