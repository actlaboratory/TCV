# -*- coding: utf-8 -*-
# お気に入りリストダイアログ

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("viewFavorites")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("お気に入り"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.favoritesList, self.favoritesStatic = self.creator.listCtrl(_("お気に入り"), None, wx.LC_LIST)
		self.favoritesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		for i in globalVars.app.Manager.favorites:
			self.favoritesList.Append([i])
		self.deleteButton = self.creator.button(_("削除"), self.delete)
		self.clearButton = self.creator.button(_("全て削除"), self.clear)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("ＯＫ"),None)
		self.bCancel=self.creator.cancelbutton(_("キャンセル"),None)

	def GetData(self):
		return self.favoritesList.GetFocusedItem()

	def closeDialog(self, event):
		self.wnd.EndModal(wx.ID_OK)

	def delete(self, event):
		dlg = simpleDialog.yesNoDialog(_("確認"), _("%sのライブをお気に入りから削除してもよろしいですか？") %(globalVars.app.Manager.favorites[self.favoritesList.GetFocusedItem()]))
		if dlg == wx.ID_NO:
			return
		globalVars.app.Manager.deleteFavorites(self.favoritesList.GetFocusedItem())
		self.favoritesList.DeleteItem(self.favoritesList.GetFocusedItem())

	def clear(self, event):
		dlg = simpleDialog.yesNoDialog(_("確認"), _("お気に入りの内容を全て消去します。よろしいですか？"))
		if dlg == wx.ID_NO:
			return
		globalVars.app.Manager.clearFavorites()
		self.favoritesList.ClearAll()
