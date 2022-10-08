# -*- coding: utf-8 -*-
# おすすめライブダイアログ

import wx
import globalVars
import views.ViewCreator
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("viewPopular")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("おすすめライブ"))
		self.InstallControls()
		if not self.refreshData():
			return False
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.hListCtrl, dummy = self.creator.virtualListCtrl(_("おすすめライブ"), size=(600,300), sizerFlag=wx.EXPAND, proportion=1)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED, self.onItemFocused)
		self.hListCtrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onItemActivated)
		self.hListCtrl.AppendColumn(_("タイトル"), width=200)
		self.hListCtrl.AppendColumn(_("名前"), width=200)
		self.hListCtrl.AppendColumn(_("ユーザ名"), width=200)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("接続"),None)
		self.bOk.Disable()
		self.bCancel=self.creator.cancelbutton(_("閉じる"),None)

	def GetData(self):
		return self.hListCtrl.GetItemText(self.hListCtrl.GetFocusedItem(), 2)

	def refreshData(self):
		data = globalVars.app.Manager.getPopular()
		if "error" in data:
			simpleDialog.errorDialog(_("おすすめライブの取得に失敗しました。詳細:%s" % str(data)))
			return False
		self.hListCtrl.DeleteAllItems()
		for i in data["movies"]:
			columns = [
				i["movie"]["title"],
				i["broadcaster"]["name"],
				i["broadcaster"]["screen_id"],
			]
			self.hListCtrl.Append(columns)
		return True

	def onItemFocused(self, event):
		self.bOk.Enable()

	def onItemActivated(self, event):
		self.wnd.EndModal(wx.ID_OK)
