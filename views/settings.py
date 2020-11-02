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
			"0": _("コインの枚数を加味せず30分を計測"),
			"1": _("コインの枚数を加味して最大まで延長したと仮定した残り時間を計測し各枠ごとの残り時間を詳細に通知する"),
			"2": _("コインの枚数を加味して最大まで延長したと仮定した残り時間を計測し延長が予定される枠の残り時間は３分前のみを通知する")
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
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("一般"))
		self.colormode, static = creator.combobox(_("画面表示モード"), list(self.colorModeSelection.values()))
		self.initialcommentcount, static = creator.spinCtrl(_("ライブ接続時に読み込むコメント数(&N)"), 1, 50)
		self.commenttosns, static = creator.combobox(_("コメントをSNSに投稿する(&S)"), list(self.commenttosnsSelection.values()))
		self.timertype, static = creator.combobox(_("タイマーの種類(&T)"), list(self.timertypeSelection.values()))
		self.historymax, static = creator.spinCtrl(_("履歴保持件数(&H)"), -1, 50)
		self.defaultconnectaccount, static = creator.inputbox(_("規定の接続先(&D)"))

		# reading
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("読み上げ"))
		self.reader, static = creator.combobox(_("出力先(&O)"), list(self.readerSelection.values()))
		self.readreceivedcomments = creator.checkbox(_("受信したコメントを読み上げる(&C)"))
		self.receivedcommentsannouncement, static = creator.inputbox(_("コメント受信時の読み上げ内容(&C)"))
		self.readmycomment = creator.checkbox(_("自分が投稿したコメントを読み上げる(&S)"))
		self.readmentions_mylive, static = creator.combobox(_("自分のライブに接続した際の返信の読み方(&R)"), list(self.readmentionsSelection.values()))
		self.readmentions_otherlive, static = creator.combobox(_("自分以外のライブに接続した際の返信の読み方(&R)"), list(self.readmentionsSelection.values()))
		self.readviewers = creator.checkbox(_("閲覧者数が変化したら読み上げる(&V)"))
		self.viewersincreasedannouncement, static = creator.inputbox(_("閲覧者数が増加した際の読み上げ(&I)"))
		self.viewersdecreasedannouncement, static = creator.inputbox(_("閲覧者数が減少した際の読み上げ(&D)"))
		self.readtypinguser = creator.checkbox(_("入力中のユーザーを読み上げる(&T)"))
		self.readreceiveditems = creator.checkbox(_("受信したアイテムを読み上げる(&I)"))
		self.readitemposteduser, static = creator.combobox(_("アイテム投稿者の読み上げ(&U)"), list(self.readitemposteduserSelection.values()))

		# live play
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("ライブ再生"))
		self.autoplay = creator.checkbox(_("自動的に再生を開始する(&A)"))
		self.defaultvolume, static = creator.slider(_("規定の音量(&V)"), 0, 100)
		self.audiodelay, static = creator.spinCtrl(_("ライブ再生の遅延時間(&D)"), 1, 30)

		# FX
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.tab,None,wx.VERTICAL,space=20,label=_("効果音"))
		self.fxvolume, static = creator.slider(_("効果音の音量(&V)"), 0, 100)
		self.syncaudiodevice = creator.checkbox(_("効果音の出力先をライブ音声の出力先と同期(&D)"))
		self.playcommentreceivedsound = creator.checkbox(_("コメント受信時にサウンドを再生(&C)"))
		self.commentreceivedsound, static = creator.inputbox(_("コメント受信時のサウンド(&C)"))
		self.playviewerschangedsound = creator.checkbox(_("閲覧者数が変化したらサウンドを再生(&V)"))
		self.viewerschangedsound, static = creator.inputbox(_("閲覧者数が変化した際のサウンド(&V)"))
		self.playitemreceivedsound = creator.checkbox(_("アイテム受信時にサウンドを再生(&I)"))
		self.itemreceivedsound, static = creator.inputbox(_("アイテム受信時のサウンド(&I)"))
		self.playcommentpostedsound = creator.checkbox(_("コメント投稿時にサウンドを再生(&S)"))
		self.commentpostedsound, static = creator.inputbox(_("コメント投稿時のサウンド(&S)"))
		self.playtypingsound = creator.checkbox(_("コメント入力中のユーザーがいたらサウンドを再生(&T)"))
		self.typingsound, static = creator.inputbox(_("コメント入力中のユーザがいた際のサウンド(&T)"))
		self.playstartupsound = creator.checkbox(_("TCVの起動時にサウンドを再生(&S)"))
		self.startupsound, static = creator.inputbox(_("TCV起動時のサウンド(&S)"))

		# buttons
		creator=views.ViewCreator.ViewCreator(self.viewMode,self.panel,self.sizer,wx.HORIZONTAL,style=wx.ALIGN_RIGHT)
		self.okbtn = creator.okbutton("OK", self.ok)
		self.cancelBtn = creator.cancelbutton(_("キャンセル"), self.cancel)

	def load(self):
		# general
		self.colormode.SetValue(self.colorModeSelection[globalVars.app.config["view"]["colormode"]])
		self.initialcommentcount.SetValue(globalVars.app.config["general"]["initialcommentcount"])
		self.commenttosns.SetValue(self.commenttosnsSelection[globalVars.app.config["general"]["commenttosns"]])
		self.timertype.SetValue(self.timertypeSelection[globalVars.app.config["general"]["timertype"]])
		self.historymax.SetValue(globalVars.app.config["general"]["historymax"])
		self.defaultconnectaccount.SetValue(globalVars.app.config["general"]["defaultconnectaccount"])

		# read
		self.reader.SetValue(self.readerSelection[globalVars.app.config["speech"]["reader"]])
		self.readreceivedcomments.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readreceivedcomments"))
		self.receivedcommentsannouncement.SetValue(globalVars.app.config["autoReadingOptions"]["receivedcommentsannouncement"])
		self.readmycomment.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readmycomment"))
		self.readmentions_mylive.SetValue(self.readmentionsSelection[globalVars.app.config["autoReadingOptions"]["readmentions_mylive"]])
		self.readmentions_otherlive.SetValue(self.readmentionsSelection[globalVars.app.config["autoReadingOptions"]["readmentions_otherlive"]])
		self.readviewers.SetValue(globalVars.app.config.getboolean("autoReadingOptions", "readviewers"))
		self.viewersincreasedannouncement.SetValue(globalVars.app.config["autoReadingOptions"]["viewersincreasedannouncement"])
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
		self.playcommentreceivedsound.SetValue(globalVars.app.config.getboolean("fx", "playcommentreceivedsound"))
		self.commentreceivedsound.SetValue(globalVars.app.config["fx"]["commentreceivedsound"])
		self.playviewerschangedsound.SetValue(globalVars.app.config.getboolean("fx", "playviewerschangedsound"))
		self.viewerschangedsound.SetValue(globalVars.app.config["fx"]["viewerschangedsound"])
		self.playitemreceivedsound.SetValue(globalVars.app.config.getboolean("fx", "playitemreceivedsound"))
		self.itemreceivedsound.SetValue(globalVars.app.config["fx"]["itemreceivedsound"])
		self.playcommentpostedsound.SetValue(globalVars.app.config.getboolean("fx", "playcommentpostedsound"))
		self.commentpostedsound.SetValue(globalVars.app.config["fx"]["commentpostedsound"])
		self.playtypingsound.SetValue(globalVars.app.config.getboolean("fx", "playtypingsound"))
		self.typingsound.SetValue(globalVars.app.config["fx"]["typingsound"])
		self.playstartupsound.SetValue(globalVars.app.config.getboolean("fx", "playstartupsound"))
		self.startupsound.SetValue(globalVars.app.config["fx"]["startupsound"])

	def save(self):
		pass

	def ok(self, event):
		result = self.save()
		if result == False:
			return
		simpleDialog.dialog(_("設定完了"), _("設定を保存しました。一部の設定は再起動後から有効になります。"))
		self.Destroy()

	def cancel(self, event):
		self.Destroy()

	def Destroy(self, events = None):
		self.log.debug("destroy")
		self.wnd.Destroy()
