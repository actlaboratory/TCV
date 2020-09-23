# -*- coding: utf-8 -*-
# 再生デバイス変更ダイアログ

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
from soundPlayer.player import getDeviceList

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("deviceDialog")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("再生デバイス変更"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.deviceList, self.static = self.creator.listCtrl(_("再生デバイス"), None, wx.LC_LIST)
		self.deviceList.ClearAll()
		self.deviceList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		self.deviceList.InsertItem(0, _("規定のデバイス"))
		deviceList = list(getDeviceList())
		del deviceList[deviceList.index("No sound")]
		for i in deviceList:
			self.deviceList.Append([i])
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("ＯＫ"),None)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def GetData(self):
		selected = self.deviceList.GetFocusedItem()
		if selected == 0:
			return ""
		else:
			return self.deviceList.GetItemText(selected)

	def closeDialog(self, event):
		self.wnd.EndModal(wx.ID_OK)
