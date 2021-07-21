# -*- coding: utf-8 -*-
# post item dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import simpleDialog

class Dialog(BaseDialog):
	def __init__(self):
		super().__init__("postItemDialog")

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("アイテム投下"))
		self.InstallControls()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20,style=wx.ALL|wx.EXPAND,margin=20)
		self.account, self.accountStatic = self.creator.combobox(_("使用するアカウント(&A)"), list(globalVars.app.config["advanced_ids"].keys()), state=0)
		self.items, self.itemsStatic = self.creator.combobox(_("アイテム(&I)"), globalVars.app.postItem.getItemList(), self.itemSelected)
		self.count, self.countStatic = self.creator.spinCtrl(_("個数(&C)"), 1)
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,20,"",wx.ALIGN_RIGHT|wx.ALL,margin=20)
		self.bOk=self.creator.okbutton(_("アイテム投下"), self.post)
		self.bOk.Disable()
		self.bCancel=self.creator.cancelbutton(_("閉じる"))

	def post(self, event):
		account = self.account.GetValue()
		item = globalVars.app.postItem.getItem(self.items.GetValue())
		if not globalVars.app.postItem.login(account):
			return
		if self.count.GetValue() * item.point > globalVars.app.postItem.getPoint(account):
			simpleDialog.errorDialog(_("アカウント「%s」の所有ポイント数が不足しているため、アイテムを投下できません。") % account)
			return
		globalVars.app.postItem.postItem(account, item, self.count.GetValue())
		self.account.SetFocus()

	def itemSelected(self, event):
		self.bOk.Enable()
