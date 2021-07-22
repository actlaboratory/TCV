# -*- coding: utf-8 -*-
#拡張機能用アカウントの設定
#Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import views.KeyValueSettingDialogBase
import wx
import globalVars

class Dialog(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def __init__(self):
		info=[
			(_("識別名"),wx.LIST_FORMAT_LEFT,200),
			(_("アカウントIDまたはEmail"),wx.LIST_FORMAT_LEFT,350),
			(_("パスワード"),wx.LIST_FORMAT_LEFT,200)
		]
		v1 = {}
		v2 = {}
		for i in globalVars.app.config.items("advanced_ids"):
			v1[i[0]] = i[1]
		for i in globalVars.app.config.items("advanced_passwords"):
			v2[i[0]] = i[1]
		super().__init__("advancedAccountManager",SettingDialog,info,v1,v2)

	def Initialize(self):
		super().Initialize(self.app.hMainView.hFrame,_("拡張機能用アカウントの設定"))
		return

class SettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""設定内容を入力するダイアログ"""

	def __init__(self,parent,name="",account="",pw=""):
		if "c:" in account or len(account) == 0:
			accountType = _("ツイキャスアカウント")
		else:
			accountType = _("Twitterアカウント")
		account = account.replace("c:", "")
		super().__init__(
				parent,
				((_("識別名"),True),(_("アカウント種別"),(_("ツイキャスアカウント"),_("Twitterアカウント"))),(_("アカウントIDまたはEmail"),True),(_("パスワード"), True)),
				(None,None,None, None),
				name,accountType,account,pw
				)

	def Initialize(self):
		return super().Initialize(_("拡張機能用アカウント設定"))

	def GetData(self):
		ret = super().GetData()
		accountType = ret.pop(1)
		if accountType == _("ツイキャスアカウント") and "c:" not in ret[1]:
			ret[1] = "c:" + ret[1]
		return ret