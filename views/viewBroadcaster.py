# -*- coding: utf-8 -*-
# 配信者情報

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self, broadcaster):
		super().__init__("viewBroadcasterDialog")
		self.broadcaster = broadcaster

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("配信者の情報"))
		self.InstallControls()
		return True


	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)

		grid=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,20,2)
		name,dummy = grid.inputbox(_("名前"), None, self.broadcaster["name"], wx.TE_READONLY, 300)
		userName,dummy = grid.inputbox(_("ユーザ名"), None, self.broadcaster["screen_id"], wx.TE_READONLY, 300)
		level,dummy = grid.inputbox(_("レベル"), None, str(self.broadcaster["level"]), wx.TE_READONLY, 300)

		introduction,dummy = self.creator.inputbox(_("自己紹介"), None, self.broadcaster["profile"], wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.TE_PROCESS_ENTER, 500)
		introduction.hideScrollBar(wx.VERTICAL)
		introduction.Bind(wx.EVT_TEXT_ENTER,self.processEnter)
		self.closeButton=self.creator.okbutton(_("閉じる") + "(&C)", None)

	def processEnter(self,event):
		self.wnd.EndModal(wx.OK)

