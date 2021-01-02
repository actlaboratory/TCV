# -*- coding: utf-8 -*-
# アクセストークン取得モジュール（暫定版）

import implicitGrantManager
import pickle
import webbrowser
import time
import pathlib
import requests
import datetime
import constants
import simpleDialog
import wx
import base64
import copy
import views.accountManager
import sys
import globalVars
from logging import getLogger
import os
import traceback

class AccountManager:
	def __init__(self):
		self.log = getLogger("%s.%s" %(constants.LOG_PREFIX, "twitcasting.accountManager"))
		self.tokens = []
		f = pathlib.Path(constants.TOKEN_FILE_NAME)
		if f.exists() == False:
			f.touch()
		try:
			self.loadFromFile()
		except:
			pass
		rm = []
		cl = []
		for i in range(0, len(self.tokens)):
			while True:
				try:
					result = self.verifyCredentials(i)
					break
				except Exception as e:
					d = wx.MessageDialog(None, _("通信に失敗しました。インターネット接続を確認してください。\nプロキシサーバーを使用する場合には、設定からプロキシの設定を行う必要があります。\n今すぐプロキシ設定を開きますか？"), _("通信エラー"), style=wx.YES_NO|wx.NO_DEFAULT|wx.ICON_ERROR)
					result = d.ShowModal()
					if result == wx.ID_NO:
						globalVars.app.hMainView.events.Exit()
						return
					import views.settings
					d = views.settings.settingsDialog()
					d.Initialize()
					for j in range(d.tab.GetPageCount()):
						if d.tab.GetPageText(j) == _("ネットワーク"):
							d.tab.SetSelection(j)
					d.Show()
			if result == 1000:
				rm.append(i)
			elif result == 2000:
				cl.append(i)
			elif result == 2001:
				simpleDialog.errorDialog(_("現在TCVは使用できません。開発者に連絡してください。"))
				sys.exit(-1)
		if len(rm) > 0:
			simpleDialog.errorDialog(_("無効なトークンが見つかったため、アカウントを削除しました。設定メニューのアカウントマネージャから、再度アカウントの追加を行ってください。"))
			for i in rm:
				del self.tokens[i]
		if len(cl) > 0:
			simpleDialog.errorDialog(_("APIの実行回数が上限に達したため、一部のユーザ情報を取得できませんでした。この情報を再度取得するには、数分待ってからTCVを再起動してください。"))
		self.saveAsFile()

	def loadFromFile(self):
		with open(constants.TOKEN_FILE_NAME, "rb") as f:
			tmplst = pickle.load(f)
		self.tokens = []
		for i in tmplst:
			i["access_token"] = base64.b64decode(i["access_token"].encode()).decode()
			self.tokens.append(i)

	def saveAsFile(self):
		tmplst = copy.deepcopy(self.tokens)
		for i in tmplst:
			i["access_token"] = base64.b64encode(i["access_token"].encode()).decode()
		try:
			with open(constants.TOKEN_FILE_NAME, "wb") as f:
				pickle.dump(tmplst, f)
		except Exception as e:
			simpleDialog.errorDialog(_("アカウント情報の書き込みに失敗しました。以下のファイルへのアクセスが可能であることを確認してください。") + "\n" + os.path.abspath(constants.TOKEN_FILE_NAME))
			traceback.print_exc()
			self.log.warning("Failed to save account information. detail: %s" %traceback.format_exc())

	def add(self):
		manager = implicitGrantManager.ImplicitGrantManager(constants.TC_CID, constants.TC_URL, constants.TC_PORT)
		l="ja"
		try:
			l=globalVars.app.config["general"]["language"].split("_")[0].lower()
		except:
			pass#end うまく読めなかったら ja を採用
		#end except
		manager.setMessage(
			lang=l,
			success=_("認証に成功しました。このウィンドウを閉じて、アプリケーションに戻ってください。"),
			failed=_("認証に失敗しました。もう一度お試しください。"),
			transfer=_("しばらくしても画面が切り替わらない場合は、別のブラウザでお試しください。")
		)
		webbrowser.open(manager.getUrl())
		d = views.accountManager.waitingDialog()
		d.Initialize()
		d.Show(False)
		while True:
			time.sleep(0.01)
			wx.YieldIfNeeded()
			if manager.getToken():
				self.tokens.append(manager.getToken())
				break
			if d.canceled == 1 or manager.getToken() == "":
				simpleDialog.dialog(_("処理結果"), _("キャンセルされました。"))
				manager.shutdown()
				return
		self.tokens[-1]["created"] = datetime.datetime.now().timestamp()
		self.tokens[-1]["default"] = False
		self.verifyCredentials(-1)
		rm = []
		for i in range(len(self.tokens) - 1):
			if self.tokens[i]["user"]["id"] == self.tokens[-1]["user"]["id"]:
				rm.append(i)
		for i in rm:
			del self.tokens[i]
		self.saveAsFile()

	def verifyCredentials(self, idx):
		token = self.tokens[idx]["access_token"]
		result = requests.get("https://apiv2.twitcasting.tv/verify_credentials", headers = {
			"X-Api-Version": "2.0",
			"Authorization": "Bearer " + token
		}).json()
		if "error" in result:
			if result["error"]["code"] == 2000:
				self.tokens[idx]["user"] = {
					"id": "0",
					"screen_id": "unavailable",
					"name": _("不明"),
				}
			return result["error"]["code"]
		self.tokens[idx]["user"] = result["user"]

	def setDefaultAccount(self, idx):
		for i in range(0, len(self.tokens)):
			if i == idx:
				self.tokens[i]["default"] = True
			else:
				self.tokens[i]["default"] = False
		self.saveAsFile()

	def hasDefaultAccount(self):
		for i in self.tokens:
			if i["default"] == True:
				return True
		return False

	def isDefault(self, idx):
		return self.tokens[idx]["default"]

	def deleteAccount(self, idx):
		del self.tokens[idx]
		self.saveAsFile()

	def getDefaultToken(self):
		for i in range(len(self.tokens)):
			if self.tokens[i]["default"] == True:
				return self.getToken(i)

	def getToken(self, idx):
		return self.tokens[idx]["access_token"]

