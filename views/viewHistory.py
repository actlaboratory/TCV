# -*- coding: utf-8 -*-
# 履歴ダイアログ

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("viewHistory")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("履歴"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
		self.historyList, self.historyStatic = self.creator.listbox(_("接続履歴"))
		self.historyList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		self.historyList.Bind(wx.EVT_LISTBOX, self.itemSelected)
		for i in globalVars.app.Manager.history:
			self.historyList.Append(i)

		self.buttonArea=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.buttonArea.okbutton(_("接続"),None)
		self.bCancel=self.buttonArea.cancelbutton(_("閉じる"),None)
		self.itemSelected()

		self.clearButton = self.creator.button(_("履歴消去(&C)"), self.clearHistory,sizerFlag=wx.ALIGN_RIGHT)

	def GetData(self):
		return self.historyList.GetSelection()

	def closeDialog(self, event):
		self.wnd.EndModal(wx.ID_OK)

	def clearHistory(self, event):
		dlg = simpleDialog.yesNoDialog(_("確認"), _("接続履歴を全て消去します。よろしいですか？"))
		if dlg == wx.ID_NO:
			return
		globalVars.app.Manager.clearHistory()
		self.historyList.Clear()
		self.itemSelected()

	def itemSelected(self, event=None):
		self.bOk.Enable(self.historyList.GetSelection() != wx.NOT_FOUND)
		self.historyList.SetFocus()
