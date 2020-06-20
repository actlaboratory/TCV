# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime
import wx
import globalVars
import simpleDialog
import pathlib
from twitcasting.accessToken import accessToken
import twitcasting.twitcasting
import re

evtComment = 0
evtLiveInfo = 1
evtCountDown = 2
evtTyping = 3

first = 0
update = 1

commentTimerInterval = 5000
liveInfoTimerInterval = 10000
countDownTimerInterval = 1000
typingTimerInterval = 5000

historyData = pathlib.Path("history.dat")
favoritesData = pathlib.Path("favorites.dat")

class manager:
	def __init__(self, MainView):
		self.MainView = MainView
		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.timer)
		if historyData.exists() == False:
			historyData.touch()
		self.history = historyData.read_text().split("\n")
		if len(self.history) == 1 and self.history[0] == "":
			del self.history[0]
		if favoritesData.exists() == False:
			favoritesData.touch()
		self.favorites = favoritesData.read_text().split("\n")
		if len(self.favorites) == 1 and self.favorites[0] == "":
			del self.favorites[0]
		self.myAccount = []
		self.myAccount.append(twitcasting.twitcasting.VerifyCredentials()["user"])
		self.nameReplaceList = globalVars.app.config.items("nameReplace")

	def connect(self, userId):
		self.connection = twitcasting.connection.connection(userId)
		if self.connection.connected == False:
			simpleDialog.errorDialog(_("指定されたユーザが見つかりません。"))
		else:
			globalVars.app.say(userId)
			if userId not in self.history:
				self.history.insert(0, userId.lower())
			elif userId in self.history:
				del self.history[self.history.index(userId)]
				self.history.insert(0, userId.lower())
			historyData.write_text("\n".join(self.history))
			self.countDownTimer = wx.Timer(self.evtHandler, evtCountDown)
			if self.connection.isLive == True:
				globalVars.app.say(_("接続。現在配信中。"))
				self.resetTimer()
				self.countDownTimer.Start(countDownTimerInterval)
				globalVars.app.say(_("タイマー開始。"))
			else:
				globalVars.app.say(_("接続。現在オフライン。"))
				self.resetTimer()
			initialCommentCount = globalVars.app.config.getint("general", "initialCommentCount", 50)
			self.initialComments = self.connection.getInitialComment(initialCommentCount)
			self.commentTimer = wx.Timer(self.evtHandler, evtComment)
			self.commentTimer.Start(commentTimerInterval)
			self.addComments(self.initialComments, first)
			self.liveInfoTimer = wx.Timer(self.evtHandler, evtLiveInfo)
			self.liveInfoTimer.Start(liveInfoTimerInterval)
			self.createLiveInfoList(first)
			self.oldCoins = self.connection.coins
			self.oldViewers = self.connection.viewers
			self.oldIsLive = self.connection.isLive
			self.oldMovieId = self.connection.movieId
			self.oldSubtitle = self.connection.subtitle
			self.oldItem = self.connection.item
			self.createItemList(first)
			self.typingTimer = wx.Timer(self.evtHandler, evtTyping)
			self.typingTimer.Start(typingTimerInterval)

	def addComments(self, commentList, mode):
		for i in commentList:
			result = {
				"dispname": i["from_user"]["name"],
				"message": i["message"],
				"time": datetime.datetime.fromtimestamp(i["created"]).strftime("%H:%M:%S"),
				"user": i["from_user"]["screen_id"]
			}
			for j in self.nameReplaceList:
				if j[0] == result["user"]:
					result["dispname"] = j[1]
			for j in globalVars.app.config.items("commentReplaceBasic"):
				result["message"] = result["message"].replace(j[0], j[1])
			for j in globalVars.app.config.items("commentReplaceReg"):
				result["message"] = re.sub(j[0], j[1], result["message"])
			urls = re.finditer("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", result["message"])
			domains = re.finditer("(https?://[^/]+/)", result["message"])
			for url in urls:
				for domain in domains:
					if len(globalVars.app.config["commentReplaceSpecial"]["url"]) != 0:
						result["message"] = re.sub(url.group(), globalVars.app.config["commentReplaceSpecial"]["url"], result["message"])
					if globalVars.app.config.getboolean("commentReplaceSpecial", "deleteProtcolName", False) == True:
						result["message"] = result["message"].replace("http://", "")
						result["message"] = result["message"].replace("https://", "")
					if globalVars.app.config.getboolean("commentReplaceSpecial", "onlyDomain", False) == True:
						result["message"] = result["message"].replace(url.group(), domain.group())
			self.MainView.commentList.InsertItem(0	, "")
			self.MainView.commentList.SetItem(0, 0, result["dispname"])
			self.MainView.commentList.SetItem(0, 1, result["message"])
			self.MainView.commentList.SetItem(0, 2, result["time"])
			self.MainView.commentList.SetItem(0, 3, result["user"])
			if mode == update:
				commentReadMode = globalVars.app.config.getint("autoReadingOptions", "announceReceivedComments", 1)
				if commentReadMode == 2:
					for j in self.myAccount:
						if i["from_user"]["id"] == j["id"]:
							return
				if commentReadMode != 0:
					announceText = globalVars.app.config["autoReadingOptions"]["receivedCommentsAnnouncement"]
					announceText = announceText.replace("$dispname", result["dispname"])
					announceText = announceText.replace("$message", result["message"])
					announceText = announceText.replace("$time", result["time"])
					announceText = announceText.replace("$user", result["user"])
					globalVars.app.say(announceText)

	def createLiveInfoList(self, mode):
		if self.connection.hasMovieId == False:
			return
		result = [
			_("経過時間：%(elapsedTime)s、残り時間：%(remainingTime)s") %{"elapsedTime": self.formatTime(self.elapsedTime).strftime("%H:%M:%S"), "remainingTime": self.formatTime(self.remainingTime).strftime("%H:%M:%S")},
			_("タイトル：%(title)s") %{"title": self.connection.movieInfo["movie"]["title"]},
			_("テロップ：%(subtitle)s") %{"subtitle": self.connection.movieInfo["movie"]["subtitle"]},
			_("閲覧：現在%(current)d人、合計%(total)d人") %{"current": self.connection.movieInfo["movie"]["current_view_count"], "total": self.connection.movieInfo["movie"]["total_view_count"]},
			_("カテゴリ：%(category)s") %{"category": self.connection.categoryName},
			_("コメント数：%(number)d") %{"number": self.connection.movieInfo["movie"]["comment_count"]},
			self.connection.movieInfo["broadcaster"]["screen_id"]
		]
		if self.connection.movieInfo["movie"]["is_live"] == True:
			result.insert(0, _("現在配信中"))
		else:
			result.insert(0, _("オフライン"))
		if self.connection.movieInfo["movie"]["is_collabo"] == True:
			result.insert(-1, _("コラボ可能"))
		else:
			result.insert(-1, _("コラボ不可"))
		for i in range(0, len(result)):
			result[i] = result[i].replace("None", _("なし"))
		if mode == first:
			for i in range(0, len(result)):
				self.MainView.liveInfo.InsertItem(i, result[i])
		elif mode == update:
			for i in range(0, len(result)):
				bool = result[i] == self.MainView.liveInfo.GetItemText(i)
				if bool == False:
					self.MainView.liveInfo.SetItemText(i, result[i])

	def createItemList(self, mode):
		result = []
		for i in self.connection.item:
			result.append(i["name"] + ":" + str(i["count"]))
		result.sort()
		if mode == update:
			self.MainView.itemList.ClearAll()
		for i in range(0, len(result)):
			self.MainView.itemList.InsertItem(i, result[i])

	def postComment(self, commentBody):
		if len(commentBody) == 0:
			simpleDialog.errorDialog(_("コメントが入力されていません。"))
			return False
		elif len(commentBody) > 140:
			simpleDialog.errorDialog(_("１４０字を超えるコメントは投稿できません。現在%s文字のコメントが入力されています。") %(str(len(commentBody))))
			return False
		result = self.connection.postComment(commentBody)
		if "error" in result:
			if result["error"]["code"] == 1001 and "comment" in result["error"]["details"] and "length" in result["error"]["details"]["comment"] :
				simpleDialog.errorDialog(_("コメント文字数が１４０字を超えているため、コメントを投稿できません。"))
				return False
			else:
				simpleDialog.errorDialog(_("エラーが発生しました。詳細：%(detail)s") %{"detail": str(result)})
				return False
		else:
			return True

	def formatTime(self, second):
		time = datetime.time(hour = int(second / 3600), minute = int(second % 3600 / 60), second = int(second % 3600 % 60))
		return time

	def deleteComment(self):
		selected = self.MainView.commentList.GetFocusedItem()
		result = self.connection.deleteComment(self.connection.comments[selected])
		if result == False:
			simpleDialog.errorDialog(_("コメントの削除に失敗しました。このコメントを削除する権限がありません。"))
		else:
			del self.connection.comments[selected]
			self.MainView.commentList.DeleteItem(selected)

	def resetTimer(self):
		globalVars.app.say(_("タイマーリセット。"))
		if self.connection.isLive == True:
			self.elapsedTime = self.connection.movieInfo["movie"]["duration"]
			self.remainingTime = 1800 - self.elapsedTime % 1800 + int(self.connection.coins / 5) * 1800
			if self.elapsedTime + self.remainingTime > 14400:
				self.remainingTime = 14400 - self.elapsedTime
			globalVars.app.say(_("残り時間：%(remainingTime)s。") %{"remainingTime": self.formatTime(self.remainingTime).strftime("%H:%M:%S")})
		elif self.connection.isLive == False:
			self.elapsedTime = 0
			self.remainingTime = 0

	def clearHistory(self):
		self.history.clear()
		historyData.write_text("\n".join(self.history))

	def addFavorites(self):
		self.favorites.insert(0, self.connection.userId.lower())
		self.favorites.sort()
		favoritesData.write_text("\n".join(self.favorites))

	def deleteFavorites(self, index):
		del self.favorites[index]
		self.favorites.sort()
		favoritesData.write_text("\n".join(self.favorites))

	def clearFavorites(self):
		self.favorites.clear()
		favoritesData.write_text("\n".join(self.favorites))

	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == evtComment:
			newComments = self.connection.getComment()
			self.addComments(newComments, update)
		elif id == evtLiveInfo:
			self.connection.update()
			self.newIsLive = self.connection.isLive
			if self.oldIsLive == True and self.newIsLive == False:
				globalVars.app.say(_("ライブ終了。"))
				self.countDownTimer.Stop()
				self.resetTimer()
				self.commentTimer.Stop()
			elif self.oldIsLive == False and self.newIsLive == True:
				globalVars.app.say(_("ライブ開始。"))
				self.countDownTimer.Start(countDownTimerInterval)
				self.commentTimer.Start(commentTimerInterval)
			self.oldIsLive = self.newIsLive
			self.newSubtitle = self.connection.subtitle
			if self.newSubtitle != self.oldSubtitle:
				if self.newSubtitle == None:
					globalVars.app.say(_("テロップ削除"))
				else:
					globalVars.app.say(_("テロップ変更。"))
					globalVars.app.say(self.newSubtitle)
			self.oldSubtitle = self.newSubtitle
			self.newCoins = self.connection.coins
			if self.newCoins != self.oldCoins:
				if self.newCoins < self.oldCoins:
					globalVars.app.say(_("コイン消費"))
				globalVars.app.say(_("コイン%(coins)d枚") %{"coins": self.newCoins})
				self.resetTimer()
			self.oldCoins = self.newCoins
			self.newMovieId = self.connection.movieId
			if self.newMovieId != self.oldMovieId:
				if self.connection.isLive == True:
					globalVars.app.say(_("次のライブが開始されました。"))
				self.resetTimer()
			self.oldMovieId = self.newMovieId
			self.newViewers = self.connection.viewers
			announceViewers = globalVars.app.config.getboolean("autoReadingOptions", "announceViewers", True)
			if announceViewers == True:
				if self.newViewers < self.oldViewers:
					viewersInfo = globalVars.app.config["autoReadingOptions"]["viewersDecreasedAnnouncement"]
					viewersInfo = viewersInfo.replace("$viewers", str(self.newViewers))
					globalVars.app.say(viewersInfo)
				elif self.newViewers > self.oldViewers:
					viewersInfo = globalVars.app.config["autoReadingOptions"]["viewersIncreasedAnnouncement"]
					viewersInfo = viewersInfo.replace("$viewers", str(self.newViewers))
					globalVars.app.say(viewersInfo)
			self.oldViewers = self.newViewers
			self.createLiveInfoList(update)
			self.newItem = self.connection.item
			receivedItem = []
			for new in self.newItem:
				#if new["name"] not in self.oldItem:
					#receivedItem.append({"id": new["id"], "name": new["name"], "count": new["count"]})
				for old in self.oldItem:
					if new["name"] == old["name"] and new["count"] > old["count"]:
						receivedItem.append({"id": new["id"], "name": new["name"], "count": new["count"] - old["count"]})
			for i in receivedItem:
				id = i["id"]
				name = i["name"]
				count = i["count"]
				users = self.connection.getItemPostedUser(id, count)
				sameUser = False
				for k in range(1, len(users) - 1):
					if users[0] == users[k]:
						sameUser = True
				announceReceivedItems = globalVars.app.config.getboolean("autoReadingOptions", "announceReceivedItems", True)
				if announceReceivedItems == True:
					if sameUser == True:
						globalVars.app.say(_("%sさんから%sをもらいました。") %(users[0], name))
					else:
						globalVars.app.say(_("%sさんなどから%sをもらいました。") %(users[0], name))
			self.oldItem = self.newItem
			self.createItemList(update)
		elif id == evtCountDown:
			self.elapsedTime += 1
			self.remainingTime -= 1
			if self.remainingTime % 1800 == 900:
				globalVars.app.say(_("残り１５分。"))
			if self.remainingTime % 1800 == 300:
				globalVars.app.say(_("残り５分。"))
			if self.remainingTime % 1800 == 180:
				globalVars.app.say(_("残り３分。"))
			if self.remainingTime % 1800 == 60:
				globalVars.app.say(_("残り１分"))
			if self.remainingTime % 1800 == 30:
				globalVars.app.say(_("残り３０秒。"))
			if self.remainingTime % 1800 == 10:
				globalVars.app.say(_("残り１０秒。"))
			if self.remainingTime % 1800 == 0:
				globalVars.app.say(_("３０分経過。"))
			self.MainView.liveInfo.SetItemText(1, _("経過時間：%(elapsedTime)s、残り時間：%(remainingTime)s") %{"elapsedTime": self.formatTime(self.elapsedTime).strftime("%H:%M:%S"), "remainingTime": self.formatTime(self.remainingTime).strftime("%H:%M:%S")})
		elif id == evtTyping:
			typingUser = self.connection.getTypingUser()
			announceTypingUser = globalVars.app.config.getboolean("autoReadingOptions", "announceTypingUser", False)
			if announceTypingUser == True:
				if typingUser != "":
					globalVars.app.say(_("%sさんが入力中") %(typingUser))
