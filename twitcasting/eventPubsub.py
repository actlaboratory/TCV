import json
import logging
import threading
import time
import traceback

import bs4
import requests
import websocket
import wx

import constants
import globalVars
import simpleDialog
from views import poll


class EventPubsub(threading.Thread):
	def __init__(self, manager, movieId):
		super().__init__(daemon=True)
		self.log = logging.getLogger("%s.%s" % (constants.LOG_PREFIX, "twitcasting.eventPubsub"))
		websocket.enableTrace(True, globalVars.app.hLogHandler)
		self.manager = manager
		self.movieId = movieId
		self.shouldExit = False

	def getWebsocketUrl(self):
		url = "https://twitcasting.tv/eventpubsuburl.php"
		data = {
			"movie_id": self.movieId,
			"__n": int(time.time() * 1000),
		}
		self.log.debug("connecting to: %s, data: %s" % (url, data))
		try:
			r = requests.post(url, data)
			self.log.debug("status: %s" % r.status_code)
			if r.status_code != 200:
				return ""
			response = r.json()
			ret = response["url"]
			ret = ret + "&gift=1"
			return ret
		except Exception as e:
			self.log.error(traceback.format_exc())
			return ""

	def run(self):
		proxyUrl, proxyPort = globalVars.app.getProxyInfo()
		self.log.debug("proxyUrl: %s" % proxyUrl)
		if proxyUrl and proxyUrl.startswith("http://"):
			proxyUrl = proxyUrl.replace("http://", "")
			self.log.debug("removed 'http://'")
		self.log.debug("proxyUrl: %s" % proxyUrl)
		while not self.shouldExit:
			url = self.getWebsocketUrl()
			if not url:
				self.log.error("Failed to get websocket URL")
				return
			self.log.debug("Websocket URL: %s" % url)
			self.socket = websocket.WebSocketApp(url, on_message=self.onMessage, on_error=self.onError, on_open=self.onOpen, on_close=self.onClose)
			self.socket.run_forever(http_proxy_host=proxyUrl, http_proxy_port=proxyPort, proxy_type="http", ping_interval=3)
			time.sleep(3)

	def onMessage(self, ws, text):
		try:
			data = json.loads(text)
			items = {}
			for i in data:
				self.log.debug(json.dumps(i, ensure_ascii=False))
				type_ = i.get("type", "")
				if type_ == "gift":
					# アイテム名が空の場合、「不明なアイテム」に置換する
					if i["item"]["name"] == "":
						self.log.debug("unknown item")
						i["item"]["name"] = _("不明なアイテム")
						self.log.debug(json.dumps(i, ensure_ascii=False))
						# 「コインの種」対応
						if i["item"]["image"].endswith("icon_incentive_coin.png"):
							self.log.debug("incentive_coin")
							globalVars.app.say(_("コインの種を使いました。"))
							# 続きの処理は不要
							self.log.debug("skipped remaining process")
							continue
					self.manager.items.insert(0, {"item": i["item"]["name"], "user": i["sender"]["screenName"]})
					itemName = i["item"]["name"]
					lst = items.get(itemName, [])
					lst.append(i)
					items[itemName] = lst
				elif type_ == "poll_status_update":
					obj = i["poll"]
					if obj["status"] == "closed":
						self.log.debug("poll %s was closed" % obj["title"])
						continue
					accounts = list(globalVars.app.config["advanced_ids"].keys())
					if len(accounts) == 0:
						self.log.info("advanced accounts are not registered")
						self.log.info("skip poll %s" % obj["title"])
						continue
					question = obj["title"]
					answers = []
					options = obj["options"]
					assert [option["id"] for option in options] == list(range(len(options)))
					for option in obj["options"]:
						answers.append(option["text"])
					sec = obj["expire_after"]
					wx.CallAfter(self.showPollDialog, accounts, question, answers, sec)
				else:
					self.log.debug("skipped: %s" % type_)
					continue
			if items:
				self.processItems(items)
		except Exception as e:
			self.log.error("Failed to get information")
			self.log.error(traceback.format_exc())

	def onError(self, ws, error):
		self.log.error("".join(traceback.TracebackException.from_exception(error).format()))

	def onOpen(self, ws):
		self.log.debug("wss opened")

	def onClose(self, ws, code, msg):
		self.log.debug("wss closed. code:%s, msg:%s" % (code, msg))

	def processItems(self, items):
		if globalVars.app.config.getboolean("fx", "playItemReceivedSound", True):
			self.manager.playFx(globalVars.app.config["fx"]["itemReceivedSound"])
		if not globalVars.app.config.getboolean("autoReadingOptions", "readReceivedItems", True):
			return
		readItemPostedUser = globalVars.app.config.getint("autoReadingOptions", "readItemPostedUser", 0)
		for name, data in items.items():
			users = [i["sender"]["id"] for i in data]
			multiUser = len(set(users)) > 1
			count = len(data)
			if readItemPostedUser == 0:
				if count == 1:
					globalVars.app.say(_("%sをもらいました。") % name)
				else:
					globalVars.app.say(_("%(name)sを%(count)i個もらいました。") % {"name": name, "count": count})
			else:
				if readItemPostedUser == 1:
					user = data[0]["sender"]["screenName"]
				elif readItemPostedUser == 2:
					user = data[0]["sender"]["name"]
				if not multiUser:
					if count == 1:
						globalVars.app.say(_("%(user)sさんから%(item)sをもらいました。") % {"user": user, "item": name})
					else:
						globalVars.app.say(_("%(user)sさんから%(item)sを%(count)i個もらいました。") % {"user": user, "item": name, "count": count})
				else:
					if count == 1:
						globalVars.app.say(_("%(user)sさんなどから%(item)sをもらいました。") % {"user": user, "item": name})
					else:
						globalVars.app.say(_("%(user)sさんなどから%(item)sを%(count)i個もらいました。") % {"user": user, "item": name, "count": count})

	def showPollDialog(self, accounts, question, answers, sec):
		d = poll.Dialog(accounts, question, answers, sec)
		d.Initialize()
		if d.Show() == wx.ID_CANCEL:
			return
		self.answerPoll(d.GetValue())

	def answerPoll(self, option):
		account = globalVars.app.advancedAccountManager.getDefaultAccount()
		if globalVars.app.advancedAccountManager.getUserId(account) == self.manager.connection.userId:
			# 自分のライブ
			existFlag = False
			for i in list(globalVars.app.config["advanced_ids"].keys()):
				if i == account:
					continue
				account = i
				existFlag = True
				break
			if not existFlag:
				simpleDialog.errorDialog(_("自分のライブで行われているアンケートに答えることはできません。"))
				return
		if not globalVars.app.advancedAccountManager.login(account):
			return
		if not globalVars.app.advancedAccountManager.isActive(account):
			if not globalVars.app.advancedAccountManager.relogin(account):
				return
		session = globalVars.app.advancedAccountManager.getSession(account)
		try:
			# get csrf token
			self.log.debug("getting csrf token...")
			r = session.get("https://twitcasting.tv/%s" % (self.manager.connection.userId))
			self.log.debug("status: %s" % r.status_code)
			if r.status_code != 200:
				simpleDialog.errorDialog(_("アンケートへの回答に失敗しました。"))
				return
			soup = bs4.BeautifulSoup(r.text, "lxml")
			elem = soup.find(attrs={"data-csrf-token": True})
			if elem is None:
				simpleDialog.errorDialog(_("アンケートへの回答に失敗しました。"))
				return
			token = elem["data-csrf-token"]
			# 回答送信
			self.log.debug("posting data...")
			r = session.post("https://frontendapi.twitcasting.tv/users/%s/polls/current/options/%d?action=vote" % (self.manager.connection.userId, option), json={"cs_session_id": token})
			self.log.debug("status: %s" % r.status_code)
			if r.status_code != 200:
				simpleDialog.errorDialog(_("アンケートへの回答に失敗しました。"))
				return
		except Exception as e:
			self.log.error(traceback.format_exc())
			simpleDialog.errorDialog(_("アンケートへの回答に失敗しました。"))
			return

	def exit(self):
		self.log.debug("exitting...")
		self.shouldExit = True
		if hasattr(self, "socket"):
			self.socket.close()
