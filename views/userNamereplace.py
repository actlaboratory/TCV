# -*- coding: utf-8 -*-
#コメント文字列置換設定
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import views.KeyValueSettingDialogBase
import wx
import globalVars

class Dialog(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def __init__(self):
		info=[
			(_("ユーザ名"),wx.LIST_FORMAT_LEFT,200),
			(_("表示名"),wx.LIST_FORMAT_LEFT,350),
		]
		values = dict(globalVars.app.config.items("nameReplace"))
		super().__init__("userNameReplace",SettingDialog,info,values)

	def Initialize(self):
		super().Initialize(self.app.hMainView.hFrame,_("表示名置換設定"))
		return

class SettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""設定内容を入力するダイアログ"""

	def __init__(self,parent,userName="",displayName=""):
		super().__init__(
				parent,
				((_("ユーザ名"),True),(_("表示名"),True)),
				(None,None,None),
				userName,displayName
				)

	def Initialize(self):
		return super().Initialize(_("置換内容設定"))
