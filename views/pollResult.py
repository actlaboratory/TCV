# -*- coding: utf-8 -*-
# poll result dialog

import time
import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self, poll: dict):
		super().__init__("pollResultDialog")
		self.poll = poll

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("アンケート結果"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.question = self.creator.staticText(self.poll["title"])
		self.answers, self.answersLabel = self.creator.listCtrl(_("回答"), style=wx.LC_REPORT)
		self.answers.AppendColumn(_("内容"))
		self.answers.AppendColumn(_("回答数"))
		for option in self.poll["options"]:
			self.answers.Append((option["text"], str(option["vote_count"])))
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bClose=self.creator.cancelbutton(_("閉じる"))
