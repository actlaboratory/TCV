# -*- coding: utf-8 -*-
# コメントの詳細

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import webbrowser

class Dialog(BaseDialog):
	def __init__(self, comment):
		super().__init__("viewCommentDialog")
		self.comment = comment

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("コメントの詳細"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL,margin=20)
		body,dummy = self.creator.inputbox(_("コメント本文"), None, self.comment["message"], wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.TE_PROCESS_ENTER|wx.BORDER_RAISED, 500)
		body.hideScrollBar(wx.VERTICAL)
		body.Bind(wx.EVT_TEXT_ENTER,self.processEnter)

		grid=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.creator.GetSizer(),views.ViewCreator.FlexGridSizer,20,2)
		name,dummy = grid.inputbox(_("名前"), None, self.comment["from_user"]["name"], wx.TE_READONLY, 300)
		userName,dummy = grid.inputbox(_("ユーザ名"), None, self.comment["from_user"]["screen_id"], wx.TE_READONLY, 300)
		level,dummy = grid.inputbox(_("レベル"), None, str(self.comment["from_user"]["level"]), wx.TE_READONLY, 300)

		introduction,dummy = self.creator.inputbox(_("自己紹介"), None, self.comment["from_user"]["profile"], wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.TE_PROCESS_ENTER, 500)
		introduction.hideScrollBar(wx.VERTICAL)
		introduction.Bind(wx.EVT_TEXT_ENTER,self.processEnter)
		twitter = self.creator.button(_("投稿者のTwitterを開く"), self.twitter)
		twitter.Enable(self.comment["from_user"]["screen_id"][1] != ":")
		self.closeButton=self.creator.okbutton(_("閉じる"), None)

	def processEnter(self,event):
		self.wnd.EndModal(wx.OK)

	def twitter(self, event):
		webbrowser.open("https://twitter.com/%s" %self.comment["from_user"]["screen_id"])
