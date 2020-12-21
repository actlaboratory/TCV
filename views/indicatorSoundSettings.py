# -*- coding: utf-8 -*-
#効果音設定
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>
#Note: All comments except these top lines will be written in Japanese. 

import views.KeyValueSettingDialogBase
import wx
import globalVars
import os
import simpleDialog

class Dialog(views.KeyValueSettingDialogBase.KeyValueSettingDialogBase):
	def __init__(self):
		info=[
			(_("種類"),wx.LIST_FORMAT_LEFT,350),
			(_("再生"),wx.LIST_FORMAT_LEFT,180),
			(_("ファイル"),wx.LIST_FORMAT_LEFT,400)
		]
		self.types = [
			_("コメント受信時"),
			_("閲覧者数増加時"),
			_("閲覧者数減少時"),
			_("アイテム受信時"),
			_("コメント投稿時"),
			_("コメント入力中検知時"),
			_("残り時間通知時"),
			_("プログラムの起動時")
		]
		play = {
			self.types[0]: globalVars.app.config.getboolean("fx", "playcommentreceivedsound"),
			self.types[1]: globalVars.app.config.getboolean("fx", "playviewersincreasedsound"),
			self.types[2]: globalVars.app.config.getboolean("fx", "playviewersincreasedsound"),
			self.types[3]: globalVars.app.config.getboolean("fx", "playitemreceivedsound"),
			self.types[4]: globalVars.app.config.getboolean("fx", "playcommentpostedsound"),
			self.types[5]: globalVars.app.config.getboolean("fx", "playtypingsound"),
			self.types[6]: globalVars.app.config.getboolean("fx", "playtimersound"),
			self.types[7]: globalVars.app.config.getboolean("fx", "playstartupsound")
		}
		files = {
			self.types[0]: globalVars.app.config["fx"]["commentreceivedsound"],
			self.types[1]: globalVars.app.config["fx"]["viewersincreasedsound"],
			self.types[2]: globalVars.app.config["fx"]["viewersdecreasedsound"],
			self.types[3]: globalVars.app.config["fx"]["itemreceivedsound"],
			self.types[4]: globalVars.app.config["fx"]["commentpostedsound"],
			self.types[5]: globalVars.app.config["fx"]["typingsound"],
			self.types[6]: globalVars.app.config["fx"]["timersound"],
			self.types[7]: globalVars.app.config["fx"]["startupsound"]
		}
		super().__init__("indicatorSoundSettingsDialog",SettingDialog,info,play,files)
		self.SetCheckResultValueString(1, _("再生する"), _("再生しない"))
		self.AddSpecialButton(_("プレビュー"),self.preview)

	def Initialize(self):
		super().Initialize(self.app.hMainView.hFrame,_("効果音設定"))
		self.addButton.Hide()
		self.deleteButton.Hide()
		return

	def save(self):
		data = self.GetData()
		globalVars.app.config["fx"]["playcommentreceivedsound"] = data[0][self.types[0]]
		globalVars.app.config["fx"]["commentreceivedsound"] = data[1][self.types[0]]
		globalVars.app.config["fx"]["playviewersincreasedsound"] = data[0][self.types[1]]
		globalVars.app.config["fx"]["viewersincreasedsound"] = data[1][self.types[1]]
		globalVars.app.config["fx"]["playviewersdecreasedsound"] = data[0][self.types[2]]
		globalVars.app.config["fx"]["viewersdecreasedsound"] = data[1][self.types[2]]
		globalVars.app.config["fx"]["playitemreceivedsound"] = data[0][self.types[3]]
		globalVars.app.config["fx"]["itemreceivedsound"] = data[1][self.types[3]]
		globalVars.app.config["fx"]["playcommentpostedsound"] = data[0][self.types[4]]
		globalVars.app.config["fx"]["commentpostedsound"] = data[1][self.types[4]]
		globalVars.app.config["fx"]["playtypingsound"] = data[0][self.types[5]]
		globalVars.app.config["fx"]["typingsound"] = data[1][self.types[5]]
		globalVars.app.config["fx"]["playtimersound"] = data[0][self.types[6]]
		globalVars.app.config["fx"]["timersound"] = data[1][self.types[6]]
		globalVars.app.config["fx"]["playstartupsound"] = data[0][self.types[7]]
		globalVars.app.config["fx"]["startupsound"] = data[1][self.types[7]]

	def OkButtonEvent(self, event):
		self.save()
		event.Skip()

	def preview(self,event):
		globalVars.app.Manager.playFx(self.hListCtrl.GetItemText(self.hListCtrl.GetFocusedItem(), 2))

class SettingDialog(views.KeyValueSettingDialogBase.SettingDialogBase):
	"""設定内容を入力するダイアログ"""

	def __init__(self,parent,type,play,files):
		super().__init__(
				parent,
				((_("種類"),None),("",_("再生する")),(_("ファイルパス"),True)),
				(None,None,(_("参照"),self.browse)),
				type,play,files
				)
		self.type = type

	def Initialize(self):
		return super().Initialize(_("効果音設定") + " - " + self.type)

	def browse(self, event):
		dialog = wx.FileDialog(self.wnd, _("効果音ファイルを選択"), wildcard="WAVE files (*.wav)|*.wav", style=wx.FD_OPEN)
		result = dialog.ShowModal()
		if result == wx.ID_CANCEL:
			return
		self.edits[2].SetValue(dialog.GetPath())

	def OkButtonEvent(self, event):
		if os.path.isfile(self.edits[2].GetValue()) == False:
			simpleDialog.errorDialog(_("効果音ファイルが見つかりません。設定内容を確認してください。"))
			return
		super().OkButtonEvent(event)
