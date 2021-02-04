# -*- coding: utf-8 -*-
# コメントリスト表示設定

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import json

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("commentListConfigurationDialog")
		self.values = {
			0: _("名前"),
			1: _("投稿"),
			2: _("時刻"),
			3: _("ユーザ名")
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("コメントリスト表示設定"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.EXPAND|wx.ALL,margin=20)
		self.hListCtrl, self.hStatic = self.creator.listCtrl(_("カラム"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,sizerFlag=wx.EXPAND)
		self.hListCtrl.InsertColumn(0, _("カラム"),width=450)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOkBtn)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onItemSelected)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onItemSelected)
		try:
			data = globalVars.app.hMainView.commentList.GetColumnsOrder()
		except AttributeError:
			data = json.loads(globalVars.app.config["mainView"]["commentlist_columns_order"])
		for i in data:
			self.hListCtrl.Append([self.values[i]])

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.moveLeftButton = self.creator.button(_("左へ(&L)"), self.move)
		self.moveRightButton = self.creator.button(_("右へ(&R)"), self.move)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("ＯＫ"), self.onOkBtn)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

		self.onItemSelected()

	def save(self):
		ret = []
		for i in range(self.hListCtrl.GetItemCount()):
			text = self.hListCtrl.GetItemText(i)
			key = [k for k, v in self.values.items() if v == text][0]
			ret.append(key)
		try:
			globalVars.app.hMainView.commentList.SetColumnsOrder(ret)
		except AttributeError:
			globalVars.app.config["mainView"]["commentlist_columns_order"] = json.dumps(ret)

	def  onOkBtn(self, event):
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
		self.moveLeftButton.Enable(self.hListCtrl.GetFocusedItem() >= 1)
		self.moveRightButton.Enable(self.hListCtrl.GetFocusedItem() >= 0 and self.hListCtrl.GetFocusedItem() < self.hListCtrl.GetItemCount() - 1)
