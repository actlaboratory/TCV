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
		self.favoritesList, self.favoritesStatic = self.creator.listbox(_("お気に入り"))
		self.favoritesList.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.closeDialog)
		self.favoritesList.Bind(wx.EVT_LISTBOX, self.itemSelected)
		for i in globalVars.app.Manager.favorites:
			self.favoritesList.Append(i)
		self.deleteButton = self.creator.button(_("削除"), self.delete)
		self.clearButton = self.creator.button(_("全て削除"), self.clear)

		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT)
		self.bOk=self.creator.okbutton(_("接続"),None)
		self.bCancel=self.creator.cancelbutton(_("閉じる"),None)
		self.itemSelected()

	def GetData(self):
		return self.favoritesList.GetSelection()

	def closeDialog(self, event):
		self.wnd.EndModal(wx.ID_OK)

	def delete(self, event):
		dlg = simpleDialog.yesNoDialog(_("確認"), _("%sのライブをお気に入りから削除してもよろしいですか？") %(globalVars.app.Manager.favorites[self.favoritesList.GetSelection()]))
		if dlg == wx.ID_NO:
			return
		globalVars.app.Manager.deleteFavorites(self.favoritesList.GetSelection())
		self.favoritesList.Delete(self.favoritesList.GetSelection())
		self.itemSelected()

	def clear(self, event):
		dlg = simpleDialog.yesNoDialog(_("確認"), _("お気に入りの内容を全て消去します。よろしいですか？"))
		if dlg == wx.ID_NO:
			return
		globalVars.app.Manager.clearFavorites()
		self.favoritesList.Clear()
		self.itemSelected()

	def itemSelected(self, event=None):
		status = self.favoritesList.GetSelection() != wx.NOT_FOUND
		self.deleteButton.Enable(status)
		self.bOk.Enable(status)
		self.favoritesList.SetFocus()
