# -*- coding: utf-8 -*-
# 接続ダイアログ

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("connectDialog")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("接続"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		displayOnConnectDialog = globalVars.app.config.getint("general", "displayonconnectdialog", 1, 0, 2)
		items = []
		if displayOnConnectDialog == 1:
			# history
			items = globalVars.app.Manager.history
		elif displayOnConnectDialog == 2:
			# favorites
			items = globalVars.app.Manager.favorites
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.iText,self.static=self.creator.comboEdit(_("接続先"), items)
		self.iText.SetValue(globalVars.app.config["general"]["defaultConnectAccount"])
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("ＯＫ"), self.onOkBtn)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def GetData(self):
		return self.iText.GetValue()

	def onOkBtn(self, event):
		if len(self.iText.GetValue().strip()) == 0:
			return
		event.Skip()
