# -*- coding: utf-8 -*-
#表示名置換設定

import wx
from logging import getLogger

from .baseDialog import *
import globalVars
import views.ViewCreator
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("userNameReplace")
		self.values = []
		for i in dict(globalVars.app.config["nameReplace"]).items():
			i = list(i)
			self.values.append(i)

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("表示名置換設定"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		#情報の表示
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.hListCtrl,self.hListStatic=self.creator.listCtrl("",None,wx.LC_REPORT,(600,300),wx.ALL|wx.ALIGN_CENTER_HORIZONTAL)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)
		self.hListCtrl.InsertColumn(0,_("ユーザ名"),width=290)
		self.hListCtrl.InsertColumn(1,_("表示名"),width=290)
		for i in self.values:
			self.hListCtrl.Append(i)

		#処理ボタン
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.addButton=self.creator.button(_("追加"),self.add)
		self.modifyButton=self.creator.button(_("修正"),self.modify)
		self.modifyButton.Enable(False)
		self.deleteButton=self.creator.button(_("削除"),self.delete)
		self.deleteButton.Enable(False)
		self.sizer.AddSpacer(20)

		#ボタンエリア
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.okButton = self.creator.okbutton("OK")
		self.cancelButton = self.creator.cancelbutton(_("キャンセル"))

	def ItemSelected(self,event):
		self.deleteButton.Enable(self.hListCtrl.GetFocusedItem()>=0)
		self.modifyButton.Enable(self.hListCtrl.GetFocusedItem()>=0)

	def add(self,event):
		d = Dialog_sub(0)
		d.Initialize()
		if d.Show() == wx.ID_CANCEL:
			return
		self.values.append(d.GetData())
		self.hListCtrl.Append(d.GetData())
		self.hListCtrl.SetFocus()

	def modify(self, event):
		idx = self.hListCtrl.GetFocusedItem()
		d = Dialog_sub(1, self.values[idx])
		d.Initialize()
		if d.Show() == wx.ID_CANCEL:
			return
		self.values[idx] = d.GetData()
		for i in range(2):
			self.hListCtrl.SetItem(idx, i, d.GetData()[i])
			self.hListCtrl.SetFocus()

	def delete(self,event):
		idx = self.hListCtrl.GetFocusedItem()
		self.hListCtrl.DeleteItem(idx)
		del self.values[idx]
		self.modifyButton.Enable(False)
		self.deleteButton.Enable(False)
		self.hListCtrl.SetFocus()

	def GetData(self):
		return self.values

class Dialog_sub(BaseDialog):
	def __init__(self, mode, value=0):
		super().__init__("commentReplace_sub")
		self.value = []
		self.mode = mode
		if self.mode == 1:
			self.value = value

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("置換内容設定"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.EXPAND|wx.ALL)
		self.userName, static = self.creator.inputbox(_("ユーザ名"),sizerFlag=wx.EXPAND)
		if self.mode == 1:
			self.userName.SetValue(self.value[0])
		self.displayName, static = self.creator.inputbox(_("表示名"),sizerFlag=wx.EXPAND)
		if self.mode == 1:
			self.displayName.SetValue(self.value[1])
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("ＯＫ"), self.onOkBtn)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def GetData(self):
		return self.value

	def onOkBtn(self, event):
		self.value = [
			self.userName.GetValue(),
			self.displayName.GetValue()
		]
		self.Destroy()
