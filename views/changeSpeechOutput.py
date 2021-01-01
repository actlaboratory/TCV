# -*- coding: utf-8 -*-
# 再生デバイス変更ダイアログ

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("speechOutputDialog")
		self.readerSelection = {
			"NOSPEECH": _("音声なし"),
			"AUTO": _("自動選択"),
			"SAPI5": "SAPI5",
			"CLIPBOARD": _("クリップボード出力"),
			"PCTK": "PC-Talker",
			"NVDA": "NVDA",
			"JAWS": "JAWS for Windows"
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("読み上げ出力先の変更"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.EXPAND|wx.ALL,margin=20)
		self.reader, self.static = self.creator.listCtrl(_("出力先"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,sizerFlag=wx.EXPAND)
		self.reader.InsertColumn(0, _("出力先"),width=450)
		self.reader.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onOkBtn)
		reader = list(self.readerSelection.values())
		for i in reader:
			self.reader.Append([i])
		idx = self.reader.FindItem(-1, self.readerSelection[globalVars.app.config["speech"]["reader"]])
		self.reader.Focus(idx)
		self.reader.Select(idx)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("ＯＫ"), self.onOkBtn)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def save(self):
		globalVars.app.config["speech"]["reader"] = list(self.readerSelection.keys())[self.reader.GetFocusedItem()]
		globalVars.app.InitSpeech()

	def  onOkBtn(self, event):
		self.save()
		self.Destroy()
