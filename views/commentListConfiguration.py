﻿# -*- coding: utf-8 -*-
# コメントリスト表示設定

import wx
import globalVars
import views.ViewCreator
from views.baseDialog import *
import json
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("commentListConfigurationDialog")
		self.values = {
			0: _("名前"),
			1: _("投稿"),
			2: _("時刻"),
			3: _("ユーザ名")
		}
		self.displayStatus = {}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("コメントリスト表示設定"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,0,style=wx.EXPAND|wx.ALL,margin=20)
		self.hListCtrl, self.hStatic = self.creator.listCtrl(_("カラム"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,sizerFlag=wx.EXPAND)
		self.hListCtrl.AppendColumn(_("カラム"),width=450)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOkBtn)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)
		tmp = list(range(4))
		try:
			data = globalVars.app.hMainView.commentList.GetColumnsOrder()
			isPrintColumn = globalVars.app.hMainView.commentList.isPrintColumn()
		except AttributeError:
			data = json.loads(globalVars.app.config["mainView"]["commentlist_columns_order"])
			isPrintColumn = globalVars.app.config.getboolean("mainView","commentlist"+"_print_column_name",True)
		for i in data:
			self.hListCtrl.Append([self.values[i]])
			tmp.remove(i)
		for i in tmp:
			self.hListCtrl.Append([self.values[i]])

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.EXPAND|wx.LEFT|wx.RIGHT,margin=20)
		self.hCheckBox = self.creator.checkbox(_("表示(&D)"), self.onCheckBoxStatusChanged)
		self.moveLeftButton = self.creator.button(_("左へ(&L)"), self.move)
		self.creator.AddSpace(-1)
		self.moveRightButton = self.creator.button(_("右へ(&R)"), self.move)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.EXPAND|wx.LEFT|wx.RIGHT,margin=20)
		self.hideHeaderSetting = self.creator.checkbox(_("ヘッダを画面上で非表示にする(&H)"), None, not isPrintColumn)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("ＯＫ"), self.onOkBtn)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

		self.loadDisplayStatus(data)
		self.onItemSelected()

	def loadDisplayStatus(self, data):
		for i in range(self.hListCtrl.GetItemCount()):
			index = self.getIndexFromText(self.hListCtrl.GetItemText(i))
			self.displayStatus[index] = (index in data)

	def getIndexFromText(self, text):
		return [k for k, v in self.values.items() if v == text][0]

	def save(self):
		ret = []
		for i in range(len(self.values)):
			text = self.hListCtrl.GetItemText(i)
			key = self.getIndexFromText(text)
			if self.displayStatus[key]:
				ret.append(key)
		try:
			globalVars.app.hMainView.commentList.setPrintColumn(not self.hideHeaderSetting.GetValue())
			globalVars.app.hMainView.commentList.SetColumnsOrder(ret)
		except AttributeError:
			globalVars.app.config["mainView"]["commentlist_columns_order"] = json.dumps(ret)
			globalVars.app.config["mainView"]["commentlist_print_column_name"] = not self.hideHeaderSetting.GetValue()

	def  onOkBtn(self, event):
		if len([i for i in self.displayStatus.values() if i == True]) == 0:
			simpleDialog.errorDialog(_("全ての列を非表示にすることはできません。"))
			return
		self.save()
		self.Destroy()

	def move(self, event):
		button = event.GetEventObject()
		focus = self.hListCtrl.GetFocusedItem()
		if button == self.moveRightButton:
			target = focus + 1
		elif button == self.moveLeftButton:
			target = focus - 1
		tmp = self.hListCtrl.GetItemText(focus)
		self.hListCtrl.SetItemText(focus, self.hListCtrl.GetItemText(target))
		self.hListCtrl.SetItemText(target, tmp)
		self.hListCtrl.Focus(target)
		self.hListCtrl.Select(target)

	def onItemSelected(self, event=None):
		selected = self.hListCtrl.GetFocusedItem()
		self.hCheckBox.GetParent().Enable(selected >= 0)
		if selected >= 0:
			self.hCheckBox.SetValue(self.displayStatus[self.getIndexFromText(self.hListCtrl.GetItemText(selected))])
		self.moveLeftButton.Enable(selected >= 1)
		self.moveRightButton.Enable(selected >= 0 and selected < self.hListCtrl.GetItemCount() - 1)

	def onCheckBoxStatusChanged(self, event):
		selected = self.hListCtrl.GetFocusedItem()
		self.displayStatus[self.getIndexFromText(self.hListCtrl.GetItemText(selected))] = self.hCheckBox.GetValue()
