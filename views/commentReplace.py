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
			(_("置換元文字列"),wx.LIST_FORMAT_LEFT,200),
			(_("置換文字列"),wx.LIST_FORMAT_LEFT,350),
			(_("種別"),wx.LIST_FORMAT_LEFT,200)
		]
		v1 = {}
		v2 = {}
		for i in globalVars.app.config.items("commentReplaceBasic"):
			v1[i[0]] = i[1]
			v2[i[0]] = False
		for i in globalVars.app.config.items("commentReplaceReg"):
			v1[i[0]] = i[1]
			v2[i[0]] = True
		super().__init__("commentReplace",SettingDialog,info,v1,v2)
		self.SetCheckResultValueString(2, _("正規表現"), _("標準"))

	def Initialize(self):
		super().Initialize(self.app.hMainView.hFrame,_("コメント文字列置換設定"))
		return

	def GetValue(self):
		data = super().GetValue()
		result = []
		for i in data[0]:
			result.append([i, data[0][i], data[1][i]])
		import simpleDialog
		simpleDialog.debugDialog(result)
		return result

class SettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""設定内容を入力するダイアログ"""

	def __init__(self,parent,old="",new="",reg=False):
		super().__init__(
				parent,
				((_("置換元文字列"),True),(_("置換先文字列"),True),("",_("正規表現を使用"))),
				(None,None,None),
				old,new,reg
				)

	def Initialize(self):
		return super().Initialize(_("置換内容設定"))
