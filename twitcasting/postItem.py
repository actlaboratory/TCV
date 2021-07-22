# post item

from wx.core import App
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

class PostItem:
	def __init__(self):
		self.sessions = {}
		self.items = []
		self.log = getLogger("%s.%s" % (constants.LOG_PREFIX, "twitcasting.postItem"))

	def login(self, account):
		id = globalVars.app.config["advanced_ids"][account]
		pw = globalVars.app.config["advanced_passwords"][account]
		if id[1] != ":":
			result = twitterLogin.login(id, pw)
		elif id[0:2].lower() == "c:":
			result = twitcastingLogin.login(id[2:], pw)
		if type(result) == int:
			messages = {
				errorCodes.LOGIN_TWITCASTING_ERROR: _("ログイン中にエラーが発生しました。"),
				errorCodes.LOGIN_TWITCASTING_WRONG_ACCOUNT: _("設定されたユーザ名またはパスワードが不正です。設定を確認してください。"),
				errorCodes.LOGIN_TWITTER_WRONG_ACCOUNT: _("Twitterユーザ名またはパスワードが不正です。設定を確認してください。"),
				errorCodes.LOGIN_RECAPTCHA_NEEDED: _("reCAPTCHAによる認証が必要です。ブラウザからTwitterにログインし、認証を行ってください。"),
				errorCodes.LOGIN_TWITTER_ERROR: _("ログイン中にエラーが発生しました。"),
				errorCodes.LOGIN_CONFIRM_NEEDED: _("認証が必要です。ブラウザで操作を完了してください。"),
			}
			simpleDialog.errorDialog(messages[result])
			return False
		self.sessions[account] = result
		return True

	def getItemList(self):
		session = self.sessions[self.getDefaultAccount()]
		if globalVars.app.config["general"]["language"] == "ja-JP":
			lang = "ja"
		else:
			lang = "en"
		req = session.get("https://twitcasting.tv/gearajax.php", params={"c": "sendgift", "tuser": globalVars.app.Manager.connection.userId, "hl": lang})
		if req.status_code != 200:
			self.log.error("Item list page not found.")
			return []
		soup = bs4.BeautifulSoup(req.text, "lxml")
		itemList = soup.find("div", class_="tw-item-list")
		if itemList == None:
			self.log.error("Failed to get item list.")
			return []
		itemIds = []
		itemNames = []
		itemPoints = []
		for i in itemList.find_all("a"):
			match = re.match(r"javascript:giftItem\('.+?', '(.+?)', .+?\);", i["href"])
			if match:
				itemIds.append(match.group(1))
		for i in itemList.find_all("span", class_="tw-item-list-item-name"):
			itemNames.append(str(i.get_text()))
		for i in itemList.find_all("span", class_="tw-item-list-item-amount"):
			itemPoints.append(int(i.get_text()))
		if not len(itemIds) == len(itemNames) == len(itemPoints):
			self.log.error("GetItemList failed.\nids=%s\nnames=%s\npoints=%s" % (",".join(itemIds), ",".join(itemNames), ",".join(itemPoints)))
			return []
		for i in range(len(itemIds)):
			self.items.append(Item(itemIds[i], itemNames[i], itemPoints[i]))
		return itemNames

	def getDefaultAccount(self):
		return list(globalVars.app.config["advanced_ids"].keys())[0]

	def getPoint(self, account):
		session = self.sessions[account]
		req = session.get("https://twitcasting.tv/gearajax.php", params={"c": "sendgift", "tuser": globalVars.app.Manager.connection.userId})
		if req.status_code != 200:
			self.log.error("Item list page not found.")
			return 0
		soup = bs4.BeautifulSoup(req.text, "lxml")
		tmp = soup.find("span", class_="tw-point-bar-amount")
		if tmp == None:
			self.log.error("Get MP failed.")
			return 0
		result = tmp.get_text()
		try:
			result = int(result)
		except ValueError:
			self.log.error("Point data is invalid: " + result)
			return 0
		return result

	def getItem(self, name):
		for i in self.items:
			if i.name == name:
				return i

	def _postItem(self, account, item):
		session = self.sessions[account]
		req = session.get("https://twitcasting.tv/gearajax.php", params={"c": "sendgift", "tuser": globalVars.app.Manager.connection.userId, "itemid": item.id})
		if req.status_code != 200:
			return False
		soup = bs4.BeautifulSoup(req.text, "lxml")
		tmp = soup.find("input", {"name": "cs_session_id"})
		if tmp == None:
			return False
		csSessionId = tmp["value"]
		data = {
			"cs_session_id": csSessionId,
			"c": "sendgift",
			"tuser": globalVars.app.Manager.connection.userId,
			"itemid": item.id,
			"itemobj": "",
			"dlg": "1",
		}
		headers = {
			"Host": "twitcasting.tv",
			"Connection": "keep-alive",
			"Content-Length": "659",
			"sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
			"sec-ch-ua-mobile": "?0",
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
			"Content-Type": "multipart/form-data; boundary=----WebKitFormBoundarykFcAG1NbBBLNV4PE",
			"Accept": "*/*",
			"Origin": "https://twitcasting.tv",
			"Sec-Fetch-Site": "same-origin",
			"Sec-Fetch-Mode": "cors",
			"Sec-Fetch-Dest": "empty",
			"Referer": "https://twitcasting.tv/%s" % globalVars.app.Manager.connection.userId,
			"Accept-Encoding": "gzip, deflate, br",
			"Accept-Language": "ja,en-US;q=0.9,en;q=0.8,pl;q=0.7",
		}
		req = session.post("https://twitcasting.tv/gearajax.php", data)
		if req.status_code != 200:
			return False
		return True

	def postItem(self, account, item, count):
		counter = 0
		for i in range(count):
			if self._postItem(account, item):
				counter += 1
		simpleDialog.dialog(_("完了"), _("%(name)sを%(count)d個投下しました。") % {"name": item.name, "count": counter})

class Item:
	def __init__(self, id, name, point):
		self.id = id
		self.name = name
		self.point = point
