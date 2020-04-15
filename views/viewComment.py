# -*- coding: utf-8 -*-
# コメントの詳細

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self, comment):
		super().__init__()
		self.comment = {
			_("コメント本文"): comment["message"],
			_("名前"): comment["from_user"]["name"],
			_("ユーザ名"): comment["from_user"]["screen_id"],
			_("自己紹介"): comment["from_user"]["profile"]
		}

	def Initialize(self):
		self.identifier="viewCommentDialog"#このビューを表す文字列
		self.log=getLogger(self.identifier)
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("コメントの詳細"))
		self.InstallControls()
		return True


	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(0,self.panel,self.sizer,wx.VERTICAL,20)
		for key, value in self.comment.items():
			self.creator.inputbox(key, 500, value, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
		self.closeButton=self.creator.cancelbutton(_("閉じる(&C)"), None)

	def GetData(self):
		return self.iText.GetLineText(0)
