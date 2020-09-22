# -*- coding: utf-8 -*-
# コメントの詳細

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self, comment):
		super().__init__("viewCommentDialog")
		self.comment = {
			_("コメント本文"): comment["message"],
			_("名前"): comment["from_user"]["name"],
			_("ユーザ名"): comment["from_user"]["screen_id"],
			_("レベル"): str(comment["from_user"]["level"]),
			_("自己紹介"): comment["from_user"]["profile"]
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("コメントの詳細"))
		self.InstallControls()
		return True


	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		for key, value in self.comment.items():
			self.creator.inputbox(key, None, value, wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, 500)
		self.closeButton=self.creator.cancelbutton(_("閉じる(&C)"), None)

	def GetData(self):
		return self.iText.GetLineText(0)
