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
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.EXPAND|wx.ALL)
		self.hListCtrl,self.hListStatic=self.creator.listCtrl(_("アカウント"),None,wx.LC_REPORT,(800,300),wx.ALL|wx.ALIGN_CENTER_HORIZONTAL)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)
		self.hListCtrl.InsertColumn(0,_("ユーザ名"),format=wx.LIST_FORMAT_LEFT,width=250)
		self.hListCtrl.InsertColumn(1,_("名前"),format=wx.LIST_FORMAT_LEFT,width=250)
		self.hListCtrl.InsertColumn(2,_("有効期限"),format=wx.LIST_FORMAT_LEFT,width=180)
		self.hListCtrl.InsertColumn(3,_("通信用"),format=wx.LIST_FORMAT_LEFT,width=110)
		self.refreshList()

		#処理ボタン
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		g1=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.VERTICAL,20,"")
		g1r1=views.ViewCreator.ViewCreator(self.viewMode,self.panel,g1.GetSizer(),wx.HORIZONTAL,20,"",wx.EXPAND)
		g1r2=views.ViewCreator.ViewCreator(self.viewMode,self.panel,g1.GetSizer(),wx.HORIZONTAL,20,"",wx.EXPAND)
		self.addButton=g1r1.button(_("追加"),self.add,proportion=1)
		self.deleteButton=g1r1.button(_("削除"),self.delete,proportion=1)
		self.deleteButton.Enable(False)
		self.setDefaultButton=g1r2.button(_("通信用アカウントに設定"),self.setDefault)
		self.setDefaultButton.Enable(False)

		g2=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.VERTICAL,0)
		self.moveUpButton = g2.button(_("上へ") + "(&U)", self.move)
		self.moveUpButton.Enable(False)
		self.moveDownButton = g2.button(_("下へ") + "(&D)", self.move)
		self.moveDownButton.Enable(False)
		self.bClose=self.creator.okbutton(_("閉じる"),self.close)

	def refreshList(self):
		cursor = self.hListCtrl.GetFocusedItem()
		self.hListCtrl.DeleteAllItems()
		for i in globalVars.app.accountManager.tokens:
			if i["default"] == True:
				state = _("設定中")
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
		self.moveUpButton.Enable(self.hListCtrl.GetFocusedItem() >= 1)
		self.moveDownButton.Enable(self.hListCtrl.GetFocusedItem() >= 0 and self.hListCtrl.GetFocusedItem() < self.hListCtrl.GetItemCount() - 1)

	def GetValue(self):
		return self.config


	def add(self,event):
		q = simpleDialog.yesNoDialog(_("アカウントの追加"), _("ブラウザを開いてアカウントの認証作業を行います。よろしいですか？"))
		if q == wx.ID_NO:
			return
		self.wnd.Enable(False)
		globalVars.app.accountManager.add()
		self.wnd.Enable(True)
		self.refreshList()
		self.hListCtrl.SetFocus()

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

	def move(self, event):
		button = event.GetEventObject()
		focus = self.hListCtrl.GetFocusedItem()
		if button == self.moveDownButton:
			target = focus + 1
		elif button == self.moveUpButton:
			target = focus - 1
		globalVars.app.accountManager.tokens[focus], globalVars.app.accountManager.tokens[target] = globalVars.app.accountManager.tokens[target], globalVars.app.accountManager.tokens[focus]
		self.refreshList()
		self.hListCtrl.Focus(target)
		self.hListCtrl.Select(target)
		globalVars.app.accountManager.saveAsFile()

	def close(self, event = None):
		result = globalVars.app.accountManager.hasDefaultAccount()
		if result == False and self.hListCtrl.GetItemCount() > 0:
			simpleDialog.errorDialog(_("通信用アカウントが設定されていません。"))
			return
		else:
			self.wnd.Destroy()

	def OnClose(self, event):
		self.close()

class waitingDialog(BaseDialog):
	def __init__(self):
		self.canceled = 0
		super().__init__("waitingDialog")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("アカウントの追加"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.staticText = self.creator.staticText(_("ブラウザでの操作をを待っています..."))
		self.bCancel=self.creator.cancelbutton(_("キャンセル"), self.onCancelBtn)

	def onCancelBtn(self, event):
		self.canceled = 1
		event.Skip()
