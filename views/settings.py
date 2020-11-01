# -*- coding: utf-8 -*-
# settings dialog

import wx
import globalVars
import views.ViewCreator
from logging import getLogger
from views.baseDialog import *
import globalVars
import simpleDialog

class settingsDialog(BaseDialog):
	def __init__(self):
		super().__init__("settingDialog")
		self.readerSelection = {
			"NOSPEECH": _("音声なし"),
			"AUTO": _("自動選択"),
			"SAPI5": "SAPI5",
			"CLIPBOARD": _("クリップボード出力"),
			"PCTK": "PC-Talker",
			"NVDA": "NVDA",
			"JAWS": "JAWS for Windows"
		}
		self.colorModeSelection = {
			"white": _("標準"),
			"dark": _("反転表示")
		}
		self.commenttosnsSelection = {
			0: _("投稿しない"),
			1: _("配信者へ返信する形式で投稿"),
			2: _("通常の投稿")
		}
		self.timertypeSelection = {
			0: _("コインの枚数を加味せず30分を計測"),
			1: _("コインの枚数を加味して最大まで延長したと仮定した残り時間を計測し各枠ごとの残り時間を詳細に通知する"),
			2: _("コインの枚数を加味して最大まで延長したと仮定した残り時間を計測し延長が予定される枠の残り時間は３分前のみを通知する")
		}
		self.readmentionsSelection = {
			0: _("読み上げない"),
			1: _("全て読み上げる"),
			2: _("自分宛の返信のみ読み上げる")
		}
		self.readitemposteduserSelection = {
			0: _("読み上げない"),
			1: _("ユーザ名を読み上げる"),
			2: _("表示名を読み上げる")
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定画面"))
		self.InstallControls()
		# self.loadSettings()
		# self.switch()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		# tab
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリ選択"))

		# general
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("一般"))
		self.colormode = creator.combobox(_("画面表示モード"), list(self.colorModeSelection.values()))
		self.initialcommentcount = creator.spinCtrl(_("ライブ接続時に読み込むコメント数(&N)"), 1, 50)
		self.commenttosns = creator.combobox(_("コメントをSNSに投稿する(&S)"), list(self.commenttosnsSelection.values()))
		self.timertype = creator.combobox(_("タイマーの種類(&T)"), list(self.timertypeSelection.values()))
		self.historymax = creator.spinCtrl(_("履歴保持件数(&H)"), -1, 50)
		self.defaultconnectaccount = creator.inputbox(_("規定の接続先(&D)"))

		# reading
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("読み上げ"))
		self.reader = creator.combobox(_("出力先(&O)"), list(self.readerSelection.values()))
		self.readreceivedcomments = creator.checkbox(_("受信したコメントを読み上げる(&C)"))
		self.receivedcommentsannouncement = creator.inputbox(_("コメント受信時の読み上げ内容(&C)"))
		self.readmycomment = creator.checkbox(_("自分が投稿したコメントを読み上げる(&S)"))
		self.readmentions_mylive = creator.combobox(_("自分のライブに接続した際の返信の読み方(&R)"), list(self.readmentionsSelection.values()))
		self.readmentions_otherlive = creator.combobox(_("自分以外のライブに接続した際の返信の読み方(&R)"), list(self.readmentionsSelection.values()))
		self.readviewers = creator.checkbox(_("閲覧者数が変化したら読み上げる(&V)"))
		self.viewersincreasedannouncement = creator.inputbox(_("閲覧者数が増加した際の読み上げ(&I)"))
		self.viewersdecreasedannouncement = creator.inputbox(_("閲覧者数が減少した際の読み上げ(&D)"))
		self.readtypinguser = creator.checkbox(_("入力中のユーザーを読み上げる(&T)"))
		self.readreceiveditems = creator.checkbox(_("受信したアイテムを読み上げる(&I)"))
		self.readitemposteduser = creator.combobox(_("アイテム投稿者の読み上げ(&U)"), list(self.readitemposteduserSelection.values()))

		# live play
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("ライブ再生"))
		self.autoplay = creator.checkbox(_("自動的に再生を開始する(&A)"))
		self.defaultvolume = creator.slider(_("規定の音量(&V)"), 0, 100)
		self.audiodelay = creator.spinCtrl(_("ライブ再生の遅延時間(&D)"), 1, 30)

		# FX
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("効果音"))
		self.fxvolume = creator.slider(_("効果音の音量(&V)"), 0, 100)
		self.syncaudiodevice = creator.checkbox(_("効果音の出力先をライブ音声の出力先と同期(&D)"))
		self.playcommentreceivedsound = creator.checkbox(_("コメント受信時にサウンドを再生(&C)"))
		self.commentreceivedsound = creator.inputbox(_("コメント受信時のサウンド(&C)"))
		self.playviewerschangedsound = creator.checkbox(_("閲覧者数が変化したらサウンドを再生(&V)"))
		self.viewerschangedsound = creator.inputbox(_("閲覧者数が変化した際のサウンド(&V)"))
		self.playitemreceivedsound = creator.checkbox(_("アイテム受信時にサウンドを再生(&I)"))
		self.itemreceivedsound = creator.inputbox(_("アイテム受信時のサウンド(&I)"))
		self.playcommentpostedsound = creator.checkbox(_("コメント投稿時にサウンドを再生(&S)"))
		self.commentpostedsound = creator.inputbox(_("コメント投稿時のサウンド(&S)"))
		self.playtypingsound = creator.checkbox(_("コメント入力中のユーザーがいたらサウンドを再生(&T)"))
		self.typingsound = creator.inputbox(_("コメント入力中のユーザがいた際のサウンド(&T)"))
		self.playstartupsound = creator.checkbox(_("TCVの起動時にサウンドを再生(&S)"))
		self.startupsound = creator.inputbox(_("TCV起動時のサウンド(&S)"))

		# buttons
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton(_("OK"), self.onOkBtn)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), self.onCancelBtn)

	def onOkBtn(self, event):
		reader = list(self.readerSelection.keys())[self.reader.GetSelection()]
		colormode = list(self.colorSelection.keys())[self.color.GetSelection()]
		update = self.autoUpdate.GetValue()
		try:
			timeout = int(self.timeout.GetValue())
		except ValueError:
			simpleDialog.errorDialog(_("タイムアウト秒数の設定値が不正です。"))
		tmpdir = self.tmpEdit.GetValue()
		saveSourceDir = self.saveSelect[0].GetValue()
		savedir = self.saveDir.GetValue()
		globalVars.app.config["speech"]["reader"] = reader
		globalVars.app.config["view"]["colormode"] = colormode
		globalVars.app.config["general"]["update"] = update
		globalVars.app.config["general"]["timeout"] = timeout
		globalVars.app.config["ocr"]["tmpdir"] = tmpdir
		globalVars.app.config["ocr"]["savesourcedir"] = saveSourceDir
		globalVars.app.config["ocr"]["savedir"] = savedir
		simpleDialog.dialog(_("設定を保存しました。一部の設定は再起動後から有効になります。"))
		self.Destroy()

	def onCancelBtn(self, event):
		print("cancel")
		self.Destroy()

	def switch(self, event = None):
		if self.saveSelect[0].GetValue():
			self.saveDir.Disable()
			self.changeBtn.Disable()
		else:
			self.saveDir.Enable()
			self.changeBtn.Enable()

	def browse(self, event):
		dialog = wx.DirDialog(None, _("保存先を選択"))
		if dialog.ShowModal() == wx.ID_OK:
			dir = dialog.GetPath()
			self.saveDir.SetValue(dir)
		return

	def loadSettings(self):
		reader = globalVars.app.config["speech"]["reader"]
		selectionStr = self.readerSelection[reader]
		self.reader.SetStringSelection(selectionStr)
		color = globalVars.app.config.getstring("view", "colormode")
		selectionStr = self.colorSelection[color]
		self.color.SetStringSelection(selectionStr)
		update = globalVars.app.config.getboolean("general", "update")
		if update:
			self.autoUpdate.SetValue(True)
		else:
			self.autoUpdate.SetValue(False)
		timeout = globalVars.app.config.getint("general", "timeout", 3)
		self.timeout.SetValue(str(timeout))
		tmpdir = globalVars.app.tmpdir
		self.tmpEdit.SetValue(tmpdir)
		savesourcedir = globalVars.app.config.getboolean("ocr", "saveSourceDir")
		if savesourcedir:
			self.saveSelect[0].SetValue(True)
		else:
			self.saveSelect[1].SetValue(False)
		savedir = globalVars.app.config.getstring("ocr", "savedir", "")
		self.saveDir.SetValue(savedir)
		return

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	#def GetData(self):
		return None
