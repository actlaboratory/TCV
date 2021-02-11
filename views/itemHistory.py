# -*- coding: utf-8 -*-
# アイテム履歴

import simpleDialog
import wx
import globalVars
import views.ViewCreator
from views.baseDialog import *
import views.viewBroadcaster
import twitcasting.twitcasting

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("itemHistoryDialog")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("アイテム履歴"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,10,style=wx.EXPAND|wx.ALL,margin=20)
		self.historyList, self.static = self.creator.listCtrl(_("アイテム履歴"), None, wx.LC_REPORT | wx.LC_SINGLE_SEL | wx.BORDER_RAISED,sizerFlag=wx.EXPAND,size=(700,400))
		self.historyList.Bind(wx.EVT_LIST_ITEM_SELECTED, self.itemSelected)
		self.historyList.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.itemSelected)
		self.historyList.AppendColumn(_("ユーザ"),width=300)
		self.historyList.AppendColumn(_("アイテム"),width=380)
		for i in globalVars.app.Manager.items:
			self.historyList.Append([i["user"], i["item"]])
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.RIGHT|wx.BOTTOM,margin=10)
		self.viewProfileButton = self.creator.button(_("プロフィールを表示"), self.viewProfile)
		self.creator.AddSpace(-1)
		self.bOk=self.creator.okbutton(_("閉じる"),None)

		self.itemSelected()

	def viewProfile(self, event):
		id = self.historyList.GetItemText(self.historyList.GetFocusedItem(), 0)
		user = globalVars.app.Manager.connection.getUserObject(id)
		if len(user) == 0:
			simpleDialog.errorDialog(_("プロフィールの取得に失敗しました。"))
			return
		d = views.viewBroadcaster.Dialog(user)
		d.Initialize(_("プロフィール"))
		d.Show()
		self.wnd.SetFocus()

	def itemSelected(self, event=None):
		self.viewProfileButton.Enable(self.historyList.GetFocusedItem() >= 0)
