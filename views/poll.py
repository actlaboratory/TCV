# -*- coding: utf-8 -*-
# poll dialog

import time
import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self, accounts, question, answers, sec):
		super().__init__("pollDialog")
		self.accounts = accounts
		self.question = question
		self.answers = answers
		self.sec = sec

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("アンケート"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.text = self.creator.staticText(self.question)
		self.comboBox, self.comboBoxLabel = self.creator.combobox(_("回答"), self.answers, state=0)
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton("OK", self.onOkButton)
		self.bCancel=self.creator.cancelbutton(_("閉じる"))
		# timer
		self.timer = wx.Timer(self.wnd)
		self.wnd.Bind(wx.EVT_TIMER, self.onTimerEvent)
		# 秒→ミリ秒変換、回答送信時の遅延を考慮して3秒前にはダイアログを閉じる
		timerInterval = (self.sec - 3) * 1000
		self.timer.Start(timerInterval, True)

	def onOkButton(self, event):
		self.timer.Stop()
		event.Skip()

	def onTimerEvent(self, event):
		self.wnd.EndModal(wx.ID_CANCEL)

	def GetValue(self):
		return self.comboBox.GetSelection()