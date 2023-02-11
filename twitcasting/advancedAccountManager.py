# advanced account manager

import globalVars
import twitterLogin
import twitcastingLogin
import simpleDialog
import requests
import bs4
from logging import getLogger
import constants
import re
import errorCodes
import pickle

class AdvancedAccountManager:
	def __init__(self):
		self.sessions = {}
		self.log = getLogger("%s.%s" % (constants.LOG_PREFIX, "twitcasting.advancedAccountManager"))
		self.loadSessionData()
		self.defaultAccountIndex = 0

	def login(self, account):
		if account in self.sessions.keys():
			return True
		id = globalVars.app.config["advanced_ids"][account]
		pw = globalVars.app.config["advanced_passwords"][account]
		if "c:" not in id:
			result = twitterLogin.login(id, pw)
		elif "c:" in id:
			result = twitcastingLogin.login(id.replace("c:", ""), pw)
		if type(result) == int:
			messages = {
				errorCodes.LOGIN_TWITCASTING_ERROR: _("ログイン中にエラーが発生しました。"),
				errorCodes.LOGIN_TWITCASTING_WRONG_ACCOUNT: _("設定されたユーザ名またはパスワードが不正です。設定を確認してください。"),
				errorCodes.LOGIN_TWITTER_WRONG_ACCOUNT: _("Twitterユーザ名またはパスワードが不正です。設定を確認してください。なお、TCV Version 3.4.0の更新に伴い、ツイキャスの「ログインパスワード」を使用してログインするようになりました。ツイキャスのサイトでログインパスワードを設定し、そのパスワードをTCVに設定する必要があります。"),
				errorCodes.LOGIN_RECAPTCHA_NEEDED: _("reCAPTCHAによる認証が必要です。ブラウザからTwitterにログインし、認証を行ってください。"),
				errorCodes.LOGIN_TWITTER_ERROR: _("ログイン中にエラーが発生しました。"),
				errorCodes.LOGIN_CONFIRM_NEEDED: _("認証が必要です。ブラウザで操作を完了してください。"),
			}
			simpleDialog.errorDialog(messages[result])
			return False
		self.sessions[account] = result
		self.saveSessionData()
		return True

	def getDefaultAccount(self):
		return list(globalVars.app.config["advanced_ids"].keys())[self.defaultAccountIndex]

	def setDefaultAccountIndex(self, idx):
		if idx >= len(globalVars.app.config["advanced_ids"].keys()):
			return
		self.defaultAccountIndex = idx

	def getDefaultAccountIndex(self):
		return self.defaultAccountIndex

	def getUserId(self, account):
		user = globalVars.app.config["advanced_ids"][account]
		if "@" not in user:
			return user
		session = self.sessions[account]
		req = session.get("https://twitcasting.tv/")
		if req.status_code != 200:
			return ""
		soup = bs4.BeautifulSoup(req.text, "lxml")
		tmp = soup.find("a", class_="tw-global-header-login-user")
		if tmp == None:
			return ""
		return str(tmp["href"]).replace("/", "")

	def loadSessionData(self):
		try:
			with open(constants.SESSION_FILE_NAME, "rb") as f:
				data = pickle.load(f)
		except Exception as e:
			self.log.error("Session data load error:" + str(e))
			return
		for i in data:
			if i in globalVars.app.config["advanced_ids"].values():
				key = [k for k, v in globalVars.app.config["advanced_ids"].items() if v == i][0]
				self.sessions[key] = data[i]

	def saveSessionData(self):
		data = {}
		for i in globalVars.app.config["advanced_ids"]:
			if i in self.sessions.keys():
				data[globalVars.app.config["advanced_ids"][i]] = self.sessions[i]
		try:
			with open(constants.SESSION_FILE_NAME, "wb") as f:
				pickle.dump(data, f)
		except Exception as e:
			self.log.error("Session data save error:" + str(e))

	def deleteSessions(self):
		target = []
		for i in self.sessions:
			if i not in globalVars.app.config["advanced_ids"].keys():
				target.append(i)
		target.reverse()
		for i in target:
			del self.sessions[i]
		self.saveSessionData()

	def relogin(self, account):
		del self.sessions[account]
		return self.login(account)

	def getSession(self, account):
		return self.sessions[account]

	def isActive(self, account):
		session = self.sessions[account]
		user = self.getUserId(account)
		url = "https://twitcasting.tv/%s/account" % user
		response = session.get(url)
		return response.url == url
