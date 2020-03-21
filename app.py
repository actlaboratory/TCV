# -*- coding: utf-8 -*-
#Application Main

import accessible_output2.outputs.auto
import sys
import ConfigManager
import gettext
import logging
import os
import wx
import locale
import win32api
import datetime
from logging import getLogger, FileHandler, Formatter
from simpleDialog import *

import constants
import DefaultSettings
import errorCodes
from views import main

class Main(wx.App):
	def initialize(self):
		"""アプリを初期化する。"""
		#実行環境の取得(exeファイルorインタプリタ)
		self.frozen=hasattr(sys,"frozen")
		self.InitLogger()
		self.LoadSettings()
		locale.setlocale(locale.LC_TIME,self.config["general"]["locale"])
		self.SetTimeZone()
		self.InitTranslation()

		# 音声読み上げの準備
		reader=self.config["speech"]["reader"]
		if(reader=="PCTK"):
			self.log.info("use reader 'PCTalker'")
			self.speech=accessible_output2.outputs.pc_talker.PCTalker()
		elif(reader=="NVDA"):
			self.log.info("use reader 'NVDA'")
			self.speech=accessible_output2.outputs.nvda.NVDA()
		#SAPI4はバグってるっぽいので無効にしておく
		#		elif(reader=="SAPI4"):
			#			self.log.info("use reader 'SAPI4'")
			#			self.speech=accessible_output2.outputs.sapi4.Sapi4()
		elif(reader=="SAPI5"):
			self.log.info("use reader 'SAPI5'")
			self.speech=accessible_output2.outputs.sapi5.SAPI5()
		elif(reader=="AUTO"):
			self.log.info("use reader 'AUTO'")
			self.speech=accessible_output2.outputs.auto.Auto()
		elif(reader=="JAWS"):
			self.log.info("use reader 'JAWS'")
			self.speech=accessible_output2.outputs.jaws.Jaws()
		else:
			self.config.set("speech","reader","AUTO")
			self.log.warning("Setting missed! speech.reader reset to 'AUTO'")
			self.speech=accessible_output2.outputs.auto.Auto()

		# メインビューを表示
		self.hMainView=main.MainView()
		self.hMainView.Show()
		return True

	def InitLogger(self):
		"""ログ機能を初期化して準備する。"""
		self.hLogHandler=FileHandler(constants.APP_NAME+".log", mode="w", encoding="UTF-8")
		self.hLogHandler.setLevel(logging.DEBUG)
		self.hLogFormatter=Formatter("%(name)s - %(levelname)s - %(message)s (%(asctime)s)")
		self.hLogHandler.setFormatter(self.hLogFormatter)
		self.log=getLogger("ApplicationMain")
		self.log.setLevel(logging.DEBUG)
		self.log.addHandler(self.hLogHandler)
		r="executable" if self.frozen else "interpreter"
		self.log.info("Starting"+constants.APP_NAME+" as %s!" % r)

	def LoadSettings(self):
		"""設定ファイルを読み込む。なければデフォルト設定を適用し、設定ファイルを書く。"""
		self.config = DefaultSettings.DefaultSettings.get()
		self.config.read(constants.SETTING_FILE_NAME)
		self.config.write()

	def InitTranslation(self):
		"""翻訳を初期化する。"""
		self.translator=gettext.translation("messages","locale", languages=[self.config["general"]["language"]], fallback=True)
		self.translator.install()

	def GetFrozenStatus(self):
		"""コンパイル済みのexeで実行されている場合はTrue、インタプリタで実行されている場合はFalseを帰す。"""
		return self.frozen

	def say(self,s):
		"""スクリーンリーダーでしゃべらせる。"""
		self.speech.speak(s)

	def OnExit(self):
		return wx.App.OnExit(self)

	def SetTimeZone(self):
		bias=win32api.GetTimeZoneInformation(True)[1][0]*-1
		hours=bias//60
		minutes=bias%60
		self.timezone=datetime.timezone(datetime.timedelta(hours=hours,minutes=minutes))
