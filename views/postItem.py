# -*- coding: utf-8 -*-
# post item dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self, accounts, items):
		super().__init__("postItemDialog")
		self.accounts = accounts
		self.items = items

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("アイテム投下"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.account, self.accountStatic = self.creator.combobox(_("使用するアカウント(&A)"), self.accounts, state=0)
		self.item, self.itemStatic = self.creator.combobox(_("アイテム(&I)"), self.items, self.itemSelected)
		self.count, self.countStatic = self.creator.spinCtrl(_("個数(&C)"), 1)
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("アイテム投下"), self.post)
		self.bOk.Disable()
		self.bCancel=self.creator.cancelbutton(_("閉じる"))

	def post(self, event):
		account = self.account.GetValue()
		item = globalVars.app.postItem.getItem(self.item.GetValue())
		if not globalVars.app.postItem.login(account):
			return
		if self.count.GetValue() * item.point > globalVars.app.postItem.getPoint(account):
			simpleDialog.errorDialog(_("アカウント「%s」の所有ポイント数が不足しているため、アイテムを投下できません。") % account)
			return
		globalVars.app.postItem.postItem(account, item, self.count.GetValue())
		self.account.SetFocus()

	def itemSelected(self, event):
		self.bOk.Enable()
