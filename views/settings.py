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
			"0": _("投稿しない"),
			"1": _("配信者へ返信する形式で投稿"),
			"2": _("通常の投稿")
		}
		self.timertypeSelection = {
			"0": _("常に30分を計測"),
			"1": _("各枠ごとの残り時間を詳細に通知"),
			"2": _("延長可能な枠では３分前のみ通知")
		}
		self.readmentionsSelection = {
			"0": _("読み上げない"),
			"1": _("全て読み上げる"),
			"2": _("自分宛の返信のみ読み上げる")
		}
		self.readitemposteduserSelection = {
			"0": _("読み上げない"),
			"1": _("ユーザ名を読み上げる"),
			"2": _("表示名を読み上げる")
		}
		self.displayonconnectdialogSelection = {
			"0": _("なし"),
			"1": _("接続履歴"),
			"2": _("お気に入り")
		}

	def Initialize(self):
		self.log.debug("created")
		super().Initialize(self.app.hMainView.hFrame,_("設定"))
		self.InstallControls()
		self.load()
		return True

	def InstallControls(self):
		"""いろんなwidgetを設置する。"""

		# tab
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.VERTICAL,20)
		self.tab = self.creator.tabCtrl(_("カテゴリ選択"))

		# general
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,views.ViewCreator.GridBagSizer,label=_("一般"),style=wx.ALL,margin=20)
		self.displayonconnectdialog, static = creator.combobox(_("接続ダイアログに表示する項目(&O)"), list(self.displayonconnectdialogSelection.values()))
		self.update = creator.checkbox(_("起動時に更新を確認(&U)"))
		self.colormode, static = creator.combobox(_("画面表示モード(&D)"), list(self.colorModeSelection.values()))
		self.initialcommentcount, static = creator.spinCtrl(_("ライブ接続時に読み込む\nコメント数(&C)"), 1, 50)
		self.commenttosns, static = creator.combobox(_("コメントのSNS投稿(&S)"), list(self.commenttosnsSelection.values()))
		self.timertype, static = creator.combobox(_("タイマーの種類(&T)"), list(self.timertypeSelection.values()))
		self.historymax, static = creator.spinCtrl(_("接続履歴の保持件数(&H)"), -1, 50)
		self.defaultconnectaccount, static = creator.inputbox(_("規定の接続先(&A)"),sizerFlag=wx.EXPAND)
		self.openlivewindow = creator.checkbox(_("接続時にブラウザでライブを開く(&O)"))
		creator.GetSizer().SetItemSpan(self.openlivewindow.GetParent(),2)

		# reading-1
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("読み上げ-1"),style=wx.TOP|wx.LEFT|wx.RIGHT,margin=20)
		self.reader, static = creator.combobox(_("出力先(&O)"), list(self.readerSelection.values()), textLayout=wx.HORIZONTAL)
		self.readreceivedcomments = creator.checkbox(_("受信したコメントを読み上げる(&C)"), self.checkBoxStatusChanged)
		self.receivedcommentsannouncement, static = creator.inputbox(_("コメント受信時の読み上げ内容"))

		group=views.ViewCreator.ViewCreator(self.viewMode,creator.GetPanel(),creator.GetSizer(),wx.VERTICAL,space=20,label=_("コメントの読み上げスキップ"))
		group.AddSpace(20)
		self.readmycomment = group.checkbox(_("自分が投稿したコメントを読み上げる"))
		grid=views.ViewCreator.ViewCreator(self.viewMode,group.GetPanel(),group.GetSizer(),views.ViewCreator.FlexGridSizer,space=20,label=2)
		self.readmentions_mylive, static = grid.combobox(_("自分のライブ"), list(self.readmentionsSelection.values()))
		self.readmentions_otherlive, static = grid.combobox(_("自分以外のライブ"), list(self.readmentionsSelection.values()))
		creator.AddSpace()

		# reading-2
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("読み上げ-2"),style=wx.TOP|wx.LEFT|wx.RIGHT,margin=20)
		self.readviewersincreased = creator.checkbox(_("閲覧者数が増加したら読み上げる(&I)"), self.checkBoxStatusChanged)
		self.viewersincreasedannouncement, static = creator.inputbox(_("閲覧者数が増加した際の読み上げ"))
		self.readviewersdecreased = creator.checkbox(_("閲覧者数が減少したら読み上げる(&D)"), self.checkBoxStatusChanged)
		self.viewersdecreasedannouncement, static = creator.inputbox(_("閲覧者数が減少した際の読み上げ"))
		self.readtypinguser = creator.checkbox(_("入力中のユーザーを読み上げる(&T)"))
		self.readreceiveditems = creator.checkbox(_("受信したアイテムを読み上げる(&E)"), self.checkBoxStatusChanged)
		self.readitemposteduser, static = creator.combobox(_("アイテム投稿者の読み方"), list(self.readitemposteduserSelection.values()),textLayout=wx.HORIZONTAL)

		# live play
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("ライブ再生"),style=wx.ALL,margin=20)
		self.autoplay = creator.checkbox(_("自動的に再生を開始する(&A)"))
		self.defaultvolume, static = creator.slider(_("規定の音量(&V)"), 0, 100)
		self.audiodelay, static = creator.spinCtrl(_("ライブ再生の遅延時間(&D)"), 1, 30)

		# FX
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,views.ViewCreator.GridBagSizer,space=0,label=_("効果音"),style=wx.LEFT|wx.RIGHT|wx.TOP|wx.EXPAND,margin=20)
		creator.GetSizer().SetCols(3)
		self.syncaudiodevice = creator.checkbox(_("効果音の出力先をライブ音声の出力先と同期(&S)"))
		creator.GetSizer().SetItemSpan(self.syncaudiodevice.GetParent(),3)
		self.fxvolume, static = creator.slider(_("効果音の音量(&V)"), 0, 100,sizerFlag=wx.EXPAND,proportion=1)
		creator.GetSizer().SetItemSpan(self.fxvolume,2)
		self.playcommentreceivedsoundifskipped = creator.checkbox(_("読み上げを省略したコメントも通知音を再生する(&C)"))
		creator.GetSizer().SetItemSpan(self.playcommentreceivedsoundifskipped.GetParent(),3)
		creator.GetSizer().AddGrowableCol(1)

		# url
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("URL設定"),style=wx.ALL,margin=20)
		self.deleteprotcolname = creator.checkbox(_("プロトコル名を削除(&P)"))
		self.onlydomain = creator.checkbox(_("ドメインのみ(&D)"))
		self.url, static = creator.inputbox(_("URLを次の文字列に置き換える(&R)"))

		# proxy
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("プロキシ設定"),style=wx.ALL,margin=20)
		self.usemanualsetting = creator.checkbox(_("プロキシサーバーの情報を手動で設定する(&M)"), self.checkBoxStatusChanged)
		self.server, static = creator.inputbox(_("サーバーURL"))
		self.port, static = creator.spinCtrl(_("ポート番号"), 0, 65535, defaultValue=8080)

		# buttons
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton("OK", self.ok)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), self.cancel)

	def load(self):
		# general
		self.displayonconnectdialog.SetValue(self.displayonconnectdialogSelection[globalVars.app.config["general"]["displayonconnectdialog"]])
		self.update.SetValue(globalVars.app.config.getboolean("general", "update"))
		self.colormode.SetValue(self.colorModeSelection[globalVars.app.config["view"]["colormode"]])
		self.initialcommentcount.SetValue(globalVars.app.config["general"]["initialcommentcount"])
		self.commenttosns.SetValue(self.commenttosnsSelection[globalVars.app.config["general"]["commenttosns"]])
		self.timertype.SetValue(self.timertypeSelection[globalVars.app.config["general"]["timertype"]])
		self.historymax.SetValue(globalVars.app.config["general"]["historymax"])
		self.defaultconnectaccount.SetValue(globalVars.app.config["general"]["defaultconnectaccount"])
		self.openlivewindow.SetValue(globalVars.app.config.getboolean("general", "openlivewindow"))

		# read
		self.reader.SetValue(self.readerSelection[globalVars.app.config["speech"]["reader"]])
		self.readreceivedcomments.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readreceivedcomments"))
		self.receivedcommentsannouncement.SetValue(globalVars.app.config["autoReadingOptions"]["receivedcommentsannouncement"])
		self.readmycomment.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readmycomment"))
		self.readmentions_mylive.SetValue(self.readmentionsSelection[globalVars.app.config["autoReadingOptions"]["readmentions_mylive"]])
		self.readmentions_otherlive.SetValue(self.readmentionsSelection[globalVars.app.config["autoReadingOptions"]["readmentions_otherlive"]])
		self.readviewersincreased.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readviewersincreased"))
		self.viewersincreasedannouncement.SetValue(globalVars.app.config["autoReadingOptions"]["viewersincreasedannouncement"])
		self.readviewersdecreased.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readviewersdecreased"))
		self.viewersdecreasedannouncement.SetValue(globalVars.app.config["autoReadingOptions"]["viewersdecreasedannouncement"])
		self.readtypinguser.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readtypinguser"))
		self.readreceiveditems.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readreceiveditems"))
		self.readitemposteduser.SetValue(self.readitemposteduserSelection[globalVars.app.config["autoReadingOptions"]["readitemposteduser"]])

		# live play
		self.autoplay.SetValue(globalVars.app.config.getboolean("livePlay", "autoplay"))
		self.defaultvolume.SetValue(globalVars.app.config.getint("livePlay", "defaultvolume"))
		self.audiodelay.SetValue(globalVars.app.config["livePlay"]["audiodelay"])

		# fx
		self.fxvolume.SetValue(globalVars.app.config.getint("fx", "fxvolume"))
		self.syncaudiodevice.SetValue(globalVars.app.config.getboolean("fx", "syncaudiodevice"))
		self.playcommentreceivedsoundifskipped.SetValue(globalVars.app.config.getboolean("fx", "playcommentreceivedsoundifskipped"))

		# url
		self.deleteprotcolname.SetValue(globalVars.app.config.getboolean("commentReplaceSpecial", "deleteprotcolname"))
		self.onlydomain.SetValue(globalVars.app.config.getboolean("commentReplaceSpecial", "onlydomain"))
		self.url.SetValue(globalVars.app.config["commentReplaceSpecial"]["url"])

		# proxy
		self.usemanualsetting.SetValue(globalVars.app.config.getboolean("proxy", "usemanualsetting"))
		self.server.SetValue(globalVars.app.config["proxy"]["server"])
		self.port.SetValue(globalVars.app.config["proxy"]["port"])

		self.checkBoxStatusChanged()

	def save(self):
		# general
		globalVars.app.config["general"]["displayonconnectdialog"] = list(self.displayonconnectdialogSelection.keys())[self.displayonconnectdialog.GetSelection()]
		globalVars.app.config["general"]["update"] = self.update.GetValue()
		globalVars.app.config["view"]["colormode"] = list(self.colorModeSelection.keys())[self.colormode.GetSelection()]
		globalVars.app.config["general"]["initialcommentcount"] = self.initialcommentcount.GetValue()
		globalVars.app.config["general"]["commenttosns"] = list(self.commenttosnsSelection.keys())[self.commenttosns.GetSelection()]
		globalVars.app.config["general"]["timertype"] = list(self.timertypeSelection.keys())[self.timertype.GetSelection()]
		globalVars.app.config["general"]["historymax"] = self.historymax.GetValue()
		globalVars.app.config["general"]["defaultconnectaccount"] = self.defaultconnectaccount.GetValue()
		globalVars.app.config["general"]["openlivewindow"] = self.openlivewindow.GetValue()

		# read
		globalVars.app.config["speech"]["reader"] = list(self.readerSelection.keys())[self.reader.GetSelection()]
		globalVars.app.InitSpeech()
		globalVars.app.config["autoReadingOptions"]["readreceivedcomments"] = self.readreceivedcomments.GetValue()
		globalVars.app.config["autoReadingOptions"]["receivedcommentsannouncement"] = self.receivedcommentsannouncement.GetValue()
		globalVars.app.config["autoReadingOptions"]["readmycomment"] = self.readmycomment.GetValue()
		globalVars.app.config["autoReadingOptions"]["readmentions_mylive"] = list(self.readmentionsSelection.keys())[self.readmentions_mylive.GetSelection()]
		globalVars.app.config["autoReadingOptions"]["readmentions_otherlive"] = list(self.readmentionsSelection.keys())[self.readmentions_otherlive.GetSelection()]
		globalVars.app.config["autoReadingOptions"]["readviewersincreased"] = self.readviewersincreased.GetValue()
		globalVars.app.config["autoReadingOptions"]["viewersincreasedannouncement"] = self.viewersincreasedannouncement.GetValue()
		globalVars.app.config["autoReadingOptions"]["readviewersdecreased"] = self.readviewersdecreased.GetValue()
		globalVars.app.config["autoReadingOptions"]["viewersdecreasedannouncement"] = self.viewersdecreasedannouncement.GetValue()
		globalVars.app.config["autoReadingOptions"]["readtypinguser"] = self.readtypinguser.GetValue()
		globalVars.app.config["autoReadingOptions"]["readreceiveditems"] = self.readreceiveditems.GetValue()
		globalVars.app.config["autoReadingOptions"]["readitemposteduser"] = list(self.readitemposteduserSelection.keys())[self.readitemposteduser.GetSelection()]

		# live play
		globalVars.app.config["livePlay"]["autoplay"] = self.autoplay.GetValue()
		globalVars.app.config["livePlay"]["defaultvolume"] = self.defaultvolume.GetValue()
		globalVars.app.config["livePlay"]["audiodelay"] = self.audiodelay.GetValue()

		# fx
		globalVars.app.config["fx"]["fxvolume"] = self.fxvolume.GetValue()
		globalVars.app.config["fx"]["syncaudiodevice"] = self.syncaudiodevice.GetValue()
		globalVars.app.config["fx"]["playCommentReceivedSoundIfSkipped"] = self.playcommentreceivedsoundifskipped.GetValue()

		# url
		globalVars.app.config["commentReplaceSpecial"]["deleteprotcolname"] = self.deleteprotcolname.GetValue()
		globalVars.app.config["commentReplaceSpecial"]["onlydomain"] = self.onlydomain.GetValue()
		globalVars.app.config["commentReplaceSpecial"]["url"] = self.url.GetValue()
		globalVars.app.Manager.refreshReplaceSettings()

		# proxy
		globalVars.app.config["proxy"]["usemanualsetting"] = self.usemanualsetting.GetValue()
		globalVars.app.config["proxy"]["server"] = self.server.GetValue()
		globalVars.app.config["proxy"]["port"] = self.port.GetValue()

	def browse(self, event):
		obj = event.GetEventObject()
		if obj == self.commentreceivedsoundBrowse:
			target = self.commentreceivedsound
		elif obj == self.viewerschangedsoundBrowse:
			target = self.viewerschangedsound
		elif obj == self.itemreceivedsoundBrowse:
			target = self.itemreceivedsound
		elif obj == self.commentpostedsoundBrowse:
			target = self.commentpostedsound
		elif obj == self.typingsoundBrowse:
			target = self.typingsound
		elif obj == self.timersoundBrowse:
			target = self.timersound
		elif obj == self.startupsoundBrowse:
			target = self.startupsound
		dialog = wx.FileDialog(self.wnd, _("効果音ファイルを選択"), wildcard="WAVE files (*.wav)|*.wav", style=wx.FD_OPEN)
		result = dialog.ShowModal()
		if result == wx.ID_CANCEL:
			return
		target.SetValue(dialog.GetPath())

	def ok(self, event):
		result = self.save()
		if result == False:
			return
		self.Destroy()

	def cancel(self, event):
		self.Destroy()

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()

	def checkBoxStatusChanged(self, event=None):
		result = self.readreceivedcomments.GetValue()
		self.receivedcommentsannouncement.Enable(result)
		self.readmycomment.GetParent().Enable(result)
		self.readmentions_mylive.Enable(result)
		self.readmentions_otherlive.Enable(result)
		result = self.readviewersincreased.GetValue()
		self.viewersincreasedannouncement.Enable(result)
		result = self.readviewersdecreased.GetValue()
		self.viewersdecreasedannouncement.Enable(result)
		result = self.readreceiveditems.GetValue()
		self.readitemposteduser.GetParent().Enable(result)
		result = self.usemanualsetting.GetValue()
		self.server.Enable(result)
		self.port.Enable(result)
