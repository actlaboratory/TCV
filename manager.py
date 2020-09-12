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
import constants
import soundPlayer.player
from soundPlayer.constants import *
import soundPlayer.fxPlayer

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
		self.timers = []
		self.livePlayer = None
		self.fxPlayer = None
		self.played = False
		self.MainView.menu.EnableMenu("play", False)
		self.MainView.menu.EnableMenu("stop", False)
		self.MainView.menu.EnableMenu("volumeUp", False)
		self.MainView.menu.EnableMenu("volumeDown", False)
		self.MainView.menu.EnableMenu("resetVolume", False)
		if globalVars.app.config.getboolean("fx", "playStartupSound", False) == True:
			self.playFx(globalVars.app.config["fx"]["startupSound"])

	def connect(self, userId):
		self.connection = twitcasting.connection.connection(userId)
		if self.connection.connected == False:
			simpleDialog.errorDialog(_("指定されたユーザが見つかりません。"))
			return
		self.MainView.Clear()
		self.MainView.createMainView()
		self.MainView.menu.EnableMenu("connect", False)
		self.MainView.menu.EnableMenu("viewHistory", False)
		self.MainView.menu.EnableMenu("viewFavorites", False)
		self.MainView.menu.EnableMenu("disconnect", True)
		globalVars.app.say(userId)
		if userId not in self.history:
			self.history.insert(0, userId.lower())
		elif userId in self.history:
			del self.history[self.history.index(userId)]
			self.history.insert(0, userId.lower())
		historyMax = globalVars.app.config.getint("general", "historyMax", 10)
		if len(self.history) > historyMax:
			del self.history[historyMax:]
		historyData.write_text("\n".join(self.history))
		self.elapsedTime = self.connection.movieInfo["movie"]["duration"]
		self.countDownTimer = wx.Timer(self.evtHandler, evtCountDown)
		self.timers.append(self.countDownTimer)
		if self.connection.isLive == True:
			globalVars.app.say(_("接続。現在配信中。"))
			self.resetTimer()
			self.countDownTimer.Start(countDownTimerInterval)
			globalVars.app.say(_("タイマー開始。"))
			globalVars.app.say(_("残り時間：%s") %self.formatTime(self.remainingTime).strftime("%H:%M:%S"))
		else:
			self.resetTimer()
			globalVars.app.say(_("接続。現在オフライン。"))
		initialCommentCount = globalVars.app.config.getint("general", "initialCommentCount", 50)
		self.initialComments = self.connection.getInitialComment(initialCommentCount)
		self.commentTimer = wx.Timer(self.evtHandler, evtComment)
		self.timers.append(self.commentTimer)
		self.commentTimer.Start(commentTimerInterval)
		self.addComments(self.initialComments, first)
		self.liveInfoTimer = wx.Timer(self.evtHandler, evtLiveInfo)
		self.timers.append(self.liveInfoTimer)
		self.liveInfoTimer.Start(liveInfoTimerInterval)
		self.createLiveInfoList(first)
		self.oldCoins = self.connection.coins
		self.oldCategory = self.connection.categoryName
		self.oldViewers = self.connection.viewers
		self.oldIsLive = self.connection.isLive
		self.oldMovieId = self.connection.movieId
		self.oldSubtitle = self.connection.subtitle
		self.oldItem = self.connection.item
		self.createItemList(first)
		self.typingTimer = wx.Timer(self.evtHandler, evtTyping)
		self.timers.append(self.typingTimer)
		self.typingTimer.Start(typingTimerInterval)
		self.MainView.hFrame.SetTitle("%s - %s" %(self.connection.userId, constants.APP_NAME))
		self.MainView.menu.EnableMenu("play", True)
		if globalVars.app.config.getboolean("livePlay", "autoPlay", False) == True and self.connection.movieInfo["movie"]["hls_url"] != None:
			self.play()

	def disconnect(self):
		if self.livePlayer != None:
			self.stop()
		self.MainView.menu.EnableMenu("play", False)
		self.livePlayer = None
		for i in self.timers:
			i.Stop()
		self.MainView.Clear()
		self.MainView.hFrame.SetTitle(constants.APP_NAME)

		self.MainView.createStartScreen()
		self.MainView.menu.EnableMenu("connect", True)
		self.MainView.menu.EnableMenu("viewHistory", True)
		self.MainView.menu.EnableMenu("viewFavorites", True)
		self.MainView.menu.EnableMenu("disconnect", False)

	def addComments(self, commentList, mode):
		for commentObject in commentList:
			commentData = {
				"dispname": commentObject["from_user"]["name"],
				"message": commentObject["message"],
				"time": datetime.datetime.fromtimestamp(commentObject["created"]).strftime("%H:%M:%S"),
				"user": commentObject["from_user"]["screen_id"]
			}
			for i in self.nameReplaceList:
				if i[0] == commentData["user"]:
					commentData["dispname"] = i[1]
			for i in globalVars.app.config.items("commentReplaceBasic"):
				commentData["message"] = commentData["message"].replace(i[0], i[1])
			for i in globalVars.app.config.items("commentReplaceReg"):
				commentData["message"] = re.sub(i[0], i[1], commentData["message"])
			urls = list(commentObject["urls"])
			domains = re.finditer("(https?://[^/]+/)", commentData["message"])
			for url in urls:
				for domain in domains:
					if len(globalVars.app.config["commentReplaceSpecial"]["url"]) != 0:
						commentData["message"] = re.sub(url.group(), globalVars.app.config["commentReplaceSpecial"]["url"], commentData["message"])
					if globalVars.app.config.getboolean("commentReplaceSpecial", "deleteProtcolName", False) == True:
						commentData["message"] = commentData["message"].replace("http://", "")
						commentData["message"] = commentData["message"].replace("https://", "")
					if globalVars.app.config.getboolean("commentReplaceSpecial", "onlyDomain", False) == True:
						commentData["message"] = commentData["message"].replace(url.group(), domain.group())
			self.MainView.commentList.InsertItem(0	, "")
			self.MainView.commentList.SetItem(0, 0, commentData["dispname"])
			self.MainView.commentList.SetItem(0, 1, commentData["message"])
			self.MainView.commentList.SetItem(0, 2, commentData["time"])
			self.MainView.commentList.SetItem(0, 3, commentData["user"])
			if mode == update:
				if globalVars.app.config.getboolean("autoReadingOptions", "readReceivedComments", True) == True:
					if globalVars.app.config.getboolean("autoReadingOptions", "readMyComment", True) == False:
						for i in self.myAccount:
							if commentObject["from_user"]["id"] == i["id"]:
								return
					if self.connection.userId in self.myAccount:
						readMentions = globalVars.app.config.getint("autoReadingOptions", "readMentions_myLive", 1)
					else:
						readMentions = globalVars.app.config.getint("autoReadingOptions", "readMentions_otherLive", 1)
					if readMentions == 2:
						mentionMe = False
						for i in self.myAccount:
							if "@%s " %(i["screen_id"]) in commentData["message"]:
								mentionMe = True
						if mentionMe == False and "@" in commentObject["message"]:
							return
					elif readMentions == 0:
						if "@" in commentObject["message"]:
							return
					self.readComment(commentData)
		if globalVars.app.config.getboolean("fx", "playCommentReceivedSound", True) == True and mode == update and len(commentList) != 0:
			self.playFx(globalVars.app.config["fx"]["commentReceivedSound"])

	def readComment(self, commentData):
		announceText = globalVars.app.config["autoReadingOptions"]["receivedCommentsAnnouncement"]
		announceText = announceText.replace("$dispname", commentData["dispname"])
		announceText = announceText.replace("$message", commentData["message"])
		announceText = announceText.replace("$time", commentData["time"])
		announceText = announceText.replace("$user", commentData["user"])
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
			if globalVars.app.config.getboolean("fx", "playCommentPostedSound", True) == True:
				self.playFx(globalVars.app.config["fx"]["commentPostedSound"])
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

	def resetTimer(self, speech = False):
		if speech == True:
			globalVars.app.say(_("タイマーリセット。"))
		timerType = globalVars.app.config.getint("general", "timerType", 0)
		if self.connection.isLive == False:
			self.elapsedTime = 0
			self.remainingTime = 0
			return
		tmp = 1800 - (self.elapsedTime % 1800)
		if timerType == 0:
			totalTime = self.elapsedTime + tmp
		else:
			totalTime = self.elapsedTime + tmp + (int(self.connection.coins / 5) * 1800)
		if totalTime > 14400:
			totalTime = 14400
		self.elapsedTime = self.elapsedTime + 1
		self.remainingTime = totalTime - self.elapsedTime
		if timerType == 2:
			if self.remainingTime > 1800 and int(self.remainingTime % 1800) == 180:
				self.sayRemainingTime()
				if self.remainingTime >= 1800:
					globalVars.app.say(_("コインが%d枚あるので延長可能です。") %(self.connection.coins))
			return
		announceTime = [900, 600, 300, 180, 60, 30, 10]
		for i in announceTime:
			if self.remainingTime % 1800 == i:
				self.sayRemainingTime()
				if self.remainingTime >= 1800 and timerType != 0:
					globalVars.app.say(_("コインが%d枚あるので延長可能です。") %(self.connection.coins))
		if self.remainingTime % 1800 == 0:
			globalVars.app.say(_("30分が経過しました。"))

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

	def sayRemainingTime(self):
		remainingTime = self.formatTime(self.remainingTime % 1800)
		if remainingTime.minute == 0:
			string = _("残り%s秒です。") %(str(remainingTime.second))
		elif remainingTime.second == 0:
			string = _("残り%s分です。") %(str(remainingTime.minute))
		else:
			string = _("残り%s分%s秒です。") %(str(remainingTime.minute), str(remainingTime.second))
		globalVars.app.say(string)

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
				if self.livePlayer.getStatus() == PLAYER_STATUS_PLAYING:
					self.played = True
					self.stop()
			elif self.oldIsLive == False and self.newIsLive == True:
				globalVars.app.say(_("ライブ開始。"))
				if self.played == True:
					self.play()
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
			self.newCategory = self.connection.categoryName
			if self.newCategory != self.oldCategory:
				globalVars.app.say(_("カテゴリ変更：%s") %self.newCategory)
			self.oldCategory = self.newCategory
			self.newCoins = self.connection.coins
			if self.newCoins != self.oldCoins:
				if self.newCoins < self.oldCoins:
					globalVars.app.say(_("コイン消費"))
				if self.newCoins % 5 == 0:
					globalVars.app.say(_("コイン%(coins)d枚") %{"coins": self.newCoins})
			self.oldCoins = self.newCoins
			self.newMovieId = self.connection.movieId
			if self.newMovieId != self.oldMovieId:
				if self.connection.isLive == True:
					globalVars.app.say(_("次のライブが開始されました。"))
					if self.livePlayer.getStatus() == PLAYER_STATUS_PLAYING:
						self.stop()
						self.play()
			self.oldMovieId = self.newMovieId
			self.newViewers = self.connection.viewers
			readViewers = globalVars.app.config.getboolean("autoReadingOptions", "readViewers", True)
			if readViewers == True:
				if self.newViewers < self.oldViewers:
					viewersInfo = globalVars.app.config["autoReadingOptions"]["viewersDecreasedAnnouncement"]
					viewersInfo = viewersInfo.replace("$viewers", str(self.newViewers))
					globalVars.app.say(viewersInfo)
				elif self.newViewers > self.oldViewers:
					viewersInfo = globalVars.app.config["autoReadingOptions"]["viewersIncreasedAnnouncement"]
					viewersInfo = viewersInfo.replace("$viewers", str(self.newViewers))
					globalVars.app.say(viewersInfo)
			if globalVars.app.config.getboolean("fx", "playViewersChangedSound", True) == True and self.newViewers != self.oldViewers:
				self.playFx(globalVars.app.config["fx"]["viewersChangedSound"])
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
				readItemPostedUser = globalVars.app.config.getint("autoReadingOptions", "readItemPostedUser", 0)
				sameUser = False
				for k in range(1, len(users) - 1):
					if users[0] == users[k]:
						sameUser = True
				readReceivedItems = globalVars.app.config.getboolean("autoReadingOptions", "readReceivedItems", True)
				if readReceivedItems == True:
					if readItemPostedUser == 0:
						globalVars.app.say(_("%sをもらいました。") %name)
					else:
						users[0] = twitcasting.twitcasting.GetUserInfo(users[0])["user"]["screen_id"]
						if sameUser == True:
							globalVars.app.say(_("%sさんから%sをもらいました。") %(users[0], name))
						else:
							globalVars.app.say(_("%sさんなどから%sをもらいました。") %(users[0], name))
			if globalVars.app.config.getboolean("fx", "playItemReceivedSound", True) == True and len(receivedItem) != 0:
				self.playFx(globalVars.app.config["fx"]["itemReceivedSound"])
			self.oldItem = self.newItem
			self.createItemList(update)
		elif id == evtCountDown:
			self.resetTimer()
			self.MainView.liveInfo.SetItemText(1, _("経過時間：%(elapsedTime)s、残り時間：%(remainingTime)s") %{"elapsedTime": self.formatTime(self.elapsedTime).strftime("%H:%M:%S"), "remainingTime": self.formatTime(self.remainingTime).strftime("%H:%M:%S")})
		elif id == evtTyping:
			typingUser = self.connection.getTypingUser()
			if typingUser != "":
				if globalVars.app.config.getboolean("autoReadingOptions", "readTypingUser", False) == True:
					globalVars.app.say(_("%sさんが入力中") %(typingUser))
				if globalVars.app.config.getboolean("fx", "playTypingSound", True) == True:
					self.playFx(globalVars.app.config["fx"]["typingSound"])

	def play(self):
		if self.livePlayer == None:
			self.livePlayer = soundPlayer.player.player()
			self.livePlayer.setAmp(globalVars.app.config.getint("livePlay", "defaultVolume", 100))
			self.livePlayer.setHlsTimeout(globalVars.app.config.getint("livePlay", "audioDelay", 7))
		if self.livePlayer.getStatus() != PLAYER_STATUS_PLAYING:
			if self.connection.movieInfo["movie"]["hls_url"] == None:
				simpleDialog.errorDialog(_("再生URLを取得できません。"))
				return
			setSource = self.livePlayer.setSource(self.connection.movieInfo["movie"]["hls_url"])
			if setSource == False:
				simpleDialog.errorDialog(_("再生に失敗しました。"))
				return
			self.livePlayer.play()
		self.MainView.menu.EnableMenu("play", False)
		self.MainView.menu.EnableMenu("stop", True)
		self.MainView.menu.EnableMenu("volumeUp", True)
		self.MainView.menu.EnableMenu("volumeDown", True)
		self.MainView.menu.EnableMenu("resetVolume", True)

	def stop(self):
		if self.livePlayer.getStatus() != PLAYER_STATUS_STOPPED:
			self.livePlayer.stop()
		self.MainView.menu.EnableMenu("stop", False)
		self.MainView.menu.EnableMenu("play", True)
		self.MainView.menu.EnableMenu("volumeUp", False)
		self.MainView.menu.EnableMenu("volumeDown", False)
		self.MainView.menu.EnableMenu("resetVolume", False)

	def volumeUp(self):
		self.livePlayer.setAmp(self.livePlayer.getConfig(PLAYER_CONFIG_AMP) + 10)

	def volumeDown(self):
		self.livePlayer.setAmp(self.livePlayer.getConfig(PLAYER_CONFIG_AMP) - 10)

	def resetVolume(self):
		self.livePlayer.setAmp(100)

	def playFx(self, filePath):
		soundPlayer.fxPlayer.playFx(filePath)
