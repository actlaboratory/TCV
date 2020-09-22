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
		super().__init("viewHistory")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("履歴"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.historyList, self.historyStatic = self.creator.listCtrl(_("接続履歴"), None, wx.LC_LIST)
		self.historyList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		for i in globalVars.app.Manager.history:
			self.historyList.Append([i])

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("ＯＫ"),None)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)
		self.clearButton = self.creator.button(_("履歴消去"), self.clearHistory)

	def GetData(self):
		return self.historyList.GetFocusedItem()

	def closeDialog(self, event):
		self.wnd.EndModal(wx.ID_OK)

	def clearHistory(self, event):
		dlg = simpleDialog.yesNoDialog(_("確認"), _("接続履歴を全て消去します。よろしいですか？"))
		if dlg == wx.ID_NO:
			return
		globalVars.app.Manager.clearHistory()
		self.historyList.ClearAll()
