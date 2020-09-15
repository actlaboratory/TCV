# -*- coding: utf-8 -*-
#アカウントマネージャ

import wx
import os
import re
import gettext
from logging import getLogger

from .baseDialog import *
import globalVars
import views.ViewCreator
import simpleDialog

class Dialog(BaseDialog):

	def __init__(self,config):
		super().__init__()
		self.config=config

	def Initialize(self):
		self.identifier="accountManagerDialog"#このビューを表す文字列
		self.log=getLogger(self.identifier)
		self.log.debug("created")
		self.app=globalVars.app
		super().Initialize(self.app.hMainView.hFrame,_("アカウントマネージャ"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		#情報の表示
		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.VERTICAL,20)
		self.hListCtrl=self.creator.ListCtrl(0,wx.ALL|wx.ALIGN_CENTER_HORIZONTAL,size=(600,300),style=wx.LC_REPORT,name=_("アカウント"))

		self.hListCtrl.InsertColumn(0,_("ユーザ名"),format=wx.LIST_FORMAT_LEFT,width=250)
		self.hListCtrl.InsertColumn(1,_("名前"),format=wx.LIST_FORMAT_LEFT,width=350)
		self.hListCtrl.InsertColumn(2,_("有効期限"),format=wx.LIST_FORMAT_LEFT,width=350)
		self.hListCtrl.InsertColumn(1,_("通信アカウント設定"),format=wx.LIST_FORMAT_LEFT,width=350)

		for i in self.config:
			self.hListCtrl.Append([i["userId"], i["name"], i["limit"], i["default"]])

		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED,self.ItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED,self.ItemSelected)

		#処理ボタン
		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.creator.GetSizer(),wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.addButton=self.creator.button(_("追加"),self.add)
		self.setDefaultButton=self.creator.button(_("通信用アカウントとして設定"),self.setDefault)
		self.setDefaultButton.Enable(False)
		self.deleteButton=self.creator.button(_("削除"),self.delete)
		self.deleteButton.Enable(False)

		#ボタンエリア
		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bClose=self.creator.cancelbutton(_("閉じる"),None)

	def ItemSelected(self,event):
		self.editButton.Enable(self.hListCtrl.GetFocusedItem()>=0)
		self.deleteButton.Enable(self.hListCtrl.GetFocusedItem()>=0)

	def GetValue(self):
		return self.config


	def add(self,event):
		globalVars.app.accountManager.add()

	def setDefault(self):
		pass

	def delete(self,event):
		pass
