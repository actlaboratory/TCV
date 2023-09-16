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
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.EXPAND|wx.ALL,margin=20)
		self.deviceList, self.static = self.creator.listCtrl(_("再生デバイス"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,sizerFlag=wx.EXPAND)
		self.deviceList.AppendColumn(_("再生デバイス"),width=450)
		self.deviceList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		self.deviceList.InsertItem(0, _("既定のデバイス"))
		deviceList = list(getDeviceList())
		del deviceList[deviceList.index("No sound")]
		for i in deviceList:
			self.deviceList.Append([i])
		current = globalVars.app.config["livePlay"]["device"]
		if len(current) > 0:
			try:
				idx = deviceList.index(current) + 1
			except ValueError:
				idx = 0
		else:
			idx = 0
		self.deviceList.Focus(idx)
		self.deviceList.Select(idx)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
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
