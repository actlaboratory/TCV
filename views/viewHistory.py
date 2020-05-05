# -*- coding: utf-8 -*-
# 履歴ダイアログ

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def Initialize(self):
		self.identifier="viewHistory"#このビューを表す文字列
		self.log=getLogger(self.identifier)
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("履歴"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(0,self.panel,self.sizer,wx.VERTICAL,20)
		self.historyList = self.creator.ListCtrl(0, 0, style = wx.LC_LIST, name = _("接続履歴"))
		self.historyList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		for i in globalVars.app.Manager.history:
			self.historyList.Append([i])

		self.creator=views.ViewCreator.ViewCreator(1,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT)
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
