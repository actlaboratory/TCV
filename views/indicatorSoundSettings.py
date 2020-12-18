﻿# -*- coding: utf-8 -*-
#効果音設定
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import views.KeyValueSettingDialogBase
import wx

class Dialog(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def __init__(self):
		info=[
			(_("種類"),wx.LIST_FORMAT_LEFT,200),
			(_("再生する"),wx.LIST_FORMAT_LEFT,350),
			(_("ファイル"),wx.LIST_FORMAT_LEFT,200)
		]
		types = (
			_("コメント受信時"),
			_("閲覧者数増加時"),
			_("閲覧者数減少時"),
			_("アイテム受信時"),
			_("コメント投稿時"),
			_("コメント入力中検知時"),
			_("残り時間通知時"),
			_("プログラムの起動時")
		)
		
		super().__init__("indicatorSoundSettingsDialog",SettingDialog,info,keyConfig,menuIds)

	def Initialize(self):
		super().Initialize(self.app.hMainView.hFrame,_("ショートカットキーの設定"))
		self.addButton.Hide()
		self.deleteButton.Hide()
		return

	def SettingDialogHook(self,dialog):
		dialog.SetFilter(self.filter)

	def OkButtonEvent(self,event):
		"""
			設定されたキーが重複している場合はエラーとする
		"""
		#他のビューとの重複調査
		if not views.KeyValueSettingDialogBase.KeySettingValidation(self.oldKeyConfig,self.values[0],self.log,self.checkEntries,True):
			return

		#このビュー内での重複調査
		newKeys={}
		for name,keys in self.values[0].items():
			for key in keys.split("/"):
				newKeys.setdefault(key, set()).add(name)
		for key,names in newKeys.items():
			if key==_("なし"):
				continue
			if len(names)>=2:
				entries=[]
				for name in names:
					entries.append(keymap.makeEntry(self.values[1][name],key,None,self.log))
				if not keymap.permitConfrict(entries,self.log):
					dialog(_("エラー"),_("以下の項目において、重複するキー %s が設定されています。\n\n%s") % (key,names))
					return
		event.Skip()

class SettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""設定内容を入力するダイアログ"""

	def __init__(self,parent,name,key,id):
		keys=key.split("/")
		for i in range(len(keys),5):
			keys.append(_("なし"))
		super().__init__(
				parent,
				((_("名前"),False),(_("ショートカット1"),False),(_("ショートカット2"),False),(_("ショートカット3"),False),(_("ショートカット4"),False),(_("ショートカット5"),False),(_("識別子"),None)),
				(None,(_("設定"),self.SetKey1),(_("設定"),self.SetKey2),(_("設定"),self.SetKey3),(_("設定"),self.SetKey4),(_("設定"),self.SetKey5),None),
				name,keys[0],keys[1],keys[2],keys[3],keys[4],id
				)

	def Initialize(self):
		return super().Initialize(_("登録内容の入力"))

	def SetKey1(self,event):
		self.keyDialog(1)

	def SetKey2(self,event):
		self.keyDialog(2)

	def SetKey3(self,event):
		self.keyDialog(3)

	def SetKey4(self,event):
		self.keyDialog(4)

	def SetKey5(self,event):
		self.keyDialog(5)

	def GetData(self):
		ret=[None]*3
		ret[0]=self.edits[0].GetLineText(0)
		ret[1]=""
		for i in range(1,6):
			if self.edits[i].GetLineText(0)!=_("なし"):
				if ret[1]!="":
					ret[1]+="/"
				ret[1]+=self.edits[i].GetLineText(0)
		ret[2]=self.edits[6].GetLineText(0)
		return ret

	def SetFilter(self,filter):
		"""
			SettingDialogHookから呼び出され、フィルタを登録する
		"""
		self.filter=filter

	def keyDialog(self,no):
		#フィルタに引っかかるものが既に設定されている場合、その変更は許さない
		before=self.edits[no].GetLineText(0)
		if before!=_("なし"):
			if not self.filter.Check(before):
				dialog(_("エラー"),_("このショートカットは変更できません。"))
				return
		d=views.keyConfig.Dialog(self.wnd,self.filter)
		d.Initialize()
		if d.Show()==wx.ID_CANCEL:
			globalVars.app.say(_("解除しました。"))
			self.edits[no].SetValue(_("なし"))
		else:
			globalVars.app.say(_("%s に設定しました。") % (d.GetValue()))
			self.edits[no].SetValue(d.GetValue())
		return
