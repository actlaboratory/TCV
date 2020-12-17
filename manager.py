# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime
import wx
import globalVars
import simpleDialog
import pathlib
import twitcasting.twitcasting
import re
import constants
import soundPlayer.player
from soundPlayer.constants import *
import soundPlayer.fxPlayer
import pyperclip
import webbrowser

evtComment = 0
evtLiveInfo = 1
evtCountDown = 2
evtTyping = 3
evtPlaystatus = 4

first = 0
update = 1

commentTimerInterval = 5000
liveInfoTimerInterval = 10000
countDownTimerInterval = 1000
typingTimerInterval = 5000
playstatusTimerInterval = 500

historyData = pathlib.Path(constants.HISTORY_FILE_NAME)
favoritesData = pathlib.Path(constants.FAVORITES_FILE_NAME)

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
		for i in globalVars.app.accountManager.tokens:
			self.myAccount.append(i["user"])
		self.timers = []
		self.livePlayer = None
		self.fxPlayer = None
		self.played = False
		self.changeMenuState(False)
		if globalVars.app.config.getboolean("fx", "playStartupSound", False) == True:
			self.playFx(globalVars.app.config["fx"]["startupSound"])
		self.playStatusTimer = wx.Timer(self.evtHandler, evtPlaystatus)
		self.timers.append(self.playStatusTimer)

	def connect(self, userId):
		userId = userId.replace("http://twitcasting.tv/", "")
		userId = userId.replace("https://twitcasting.tv/", "")
		if "/" in userId:
			userId = userId[0:userId.find("/")]
		if globalVars.app.accountManager.hasDefaultAccount() == False:
			simpleDialog.errorDialog(_("アカウントが登録されていません。ライブに接続する前に、設定メニューのアカウントマネージャからアカウントの登録を行ってください。"))
			return
		self.connection = twitcasting.connection.connection(userId)
		if self.connection.connected == False:
			simpleDialog.errorDialog(_("指定されたユーザが見つかりません。"))
			return
		self.MainView.Clear()
		self.MainView.createMainView()
		self.changeMenuState(True)
		globalVars.app.say(userId)
		if userId not in self.history:
			self.history.insert(0, userId.lower())
		elif userId in self.history:
			del self.history[self.history.index(userId)]
			self.history.insert(0, userId.lower())
		historyMax = globalVars.app.config.getint("general", "historyMax", 10)
		if historyMax >= 0 and len(self.history) > historyMax:
			del self.history[historyMax:]
		historyData.write_text("\n".join(self.history))
		try:
			self.elapsedTime = self.connection.movieInfo["movie"]["duration"]
		except:
			self.elapsedTime = 0
		self.countDownTimer = wx.Timer(self.evtHandler, evtCountDown)
		self.timers.append(self.countDownTimer)
		if self.connection.isLive == True:
			globalVars.app.say(_("接続。現在配信中。"))
			self.resetTimer()
			self.countDownTimer.Start(countDownTimerInterval)
			globalVars.app.say(_("タイマー開始。"))
			try:
				globalVars.app.say(_("残り時間：%s") %self.formatTime(self.remainingTime).strftime("%H:%M:%S"))
			except:
				globalVars.app.say(_("配信時間が４時間を超えているため、タイマーを使用できません。"))
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
		if self.hasEnoughCoins(self.connection.coins) == True:
			globalVars.app.say(_("完走に必用なコインが集まっています。"))
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
		if globalVars.app.config.getboolean("livePlay", "autoPlay", False) == True and self.connection.movieInfo["movie"]["hls_url"] != None:
			self.play()
		if globalVars.app.config.getboolean("general", "openlivewindow", False) == True:
			self.openLiveWindow()

	def disconnect(self):
		if self.livePlayer != None:
			self.stop()
		self.livePlayer = None
		for i in self.timers:
			i.Stop()
		self.MainView.Clear()
		self.MainView.hFrame.SetTitle(constants.APP_NAME)
		self.MainView.createStartScreen()
		self.changeMenuState(False)

	def addComments(self, commentList, mode):
		for commentObject in commentList:
			commentData = self.getCommentdata(commentObject)
			self.MainView.commentList.InsertItem(0	, "")
			self.MainView.commentList.SetItem(0, 0, commentData["dispname"])
			self.MainView.commentList.SetItem(0, 1, commentData["message"])
			self.MainView.commentList.SetItem(0, 2, commentData["time"])
			self.MainView.commentList.SetItem(0, 3, commentData["user"])
			itemLimit = 100000
			if self.MainView.commentList.GetItemCount() > itemLimit:
				self.MainView.commentList.DeleteItem(itemLimit)
			if mode == update:
				if globalVars.app.config.getboolean("autoReadingOptions", "readReceivedComments", True) == True:
					if globalVars.app.config.getboolean("autoReadingOptions", "readMyComment", True) == False:
						for i in self.myAccount:
							if commentObject["from_user"]["id"] == i["id"]:
								self.playCommentReceivedSoundIfSkipped()
								return
					for i in self.myAccount:
						if commentObject["from_user"]["id"] == i["id"]:
							readMentions = globalVars.app.config.getint("autoReadingOptions", "readMentions_myLive", 1)
					else:
						readMentions = globalVars.app.config.getint("autoReadingOptions", "readMentions_otherLive", 1)
					if readMentions == 2:
						mentionMe = False
						for i in self.myAccount:
							if "@%s " %(i["screen_id"]) in commentData["message"]:
								mentionMe = True
						if mentionMe == False and "@" in commentObject["message"]:
							self.playCommentReceivedSoundIfSkipped()
							return
					elif readMentions == 0:
						if "@" in commentObject["message"]:
							self.play()
							return
					self.readComment(commentData)
		if globalVars.app.config.getboolean("fx", "playCommentReceivedSound", True) == True and mode == update and len(commentList) != 0:
			self.playFx(globalVars.app.config["fx"]["commentReceivedSound"])

	def getCommentdata(self, commentObject):
		commentData = {
			"dispname": commentObject["from_user"]["name"],
			"message": commentObject["message"],
			"time": datetime.datetime.fromtimestamp(commentObject["created"]).strftime("%H:%M:%S"),
			"user": commentObject["from_user"]["screen_id"]
		}
		for i in globalVars.app.config.items("nameReplace"):
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
		return commentData

	def readComment(self, commentData, speech = True):
		announceText = globalVars.app.config["autoReadingOptions"]["receivedCommentsAnnouncement"]
		announceText = announceText.replace("$dispname", commentData["dispname"])
		announceText = announceText.replace("$message", commentData["message"])
		announceText = announceText.replace("$time", commentData["time"])
		announceText = announceText.replace("$user", commentData["user"])
		if speech == False:
			return announceText
		globalVars.app.say(announceText)

	def createLiveInfoList(self, mode):
		if self.connection.hasMovieId == False:
			return
		result = [
			_("タイトル：%s") %(self.connection.movieInfo["movie"]["title"]),
			_("テロップ：%s") %(self.connection.movieInfo["movie"]["subtitle"]),
			_("閲覧：現在%d人、合計%d人") %(self.connection.movieInfo["movie"]["current_view_count"], self.connection.movieInfo["movie"]["total_view_count"]),
			_("カテゴリ：%s") %(self.connection.categoryName),
			_("コメント数：%d") %(self.connection.movieInfo["movie"]["comment_count"]),
			self.connection.movieInfo["broadcaster"]["screen_id"]
		]
		if self.connection.movieInfo["movie"]["is_live"] == True:
			result.insert(0, _("現在配信中"))
		else:
			result.insert(0, _("オフライン"))
		try:
			result.insert(1, _("経過時間：%s") %(self.formatTime(self.elapsedTime).strftime("%H:%M:%S")))
			result.insert(2, _("残り時間：%s") %(self.formatTime(self.remainingTime).strftime("%H:%M:%S")))
		except:
			result.insert(1, _("配信時間が４時間を超えているため、タイマーを使用できません。"))
			result.insert(2, _("配信時間が４時間を超えているため、タイマーを使用できません。"))
		if self.connection.movieInfo["movie"]["is_collabo"] == True:
			result.insert(-1, _("コラボ可能"))
		else:
			result.insert(-1, _("コラボ不可"))
		for i in range(0, len(result)):
			result[i] = result[i].replace("None", _("なし"))
		if mode == first:
			for i in range(0, len(result)):
				self.MainView.liveInfo.Insert(result[i], i)
		elif mode == update:
			for i in range(0, len(result)):
				bool = result[i] == self.MainView.liveInfo.GetString(i)
				if bool == False:
					self.MainView.liveInfo.SetString(i, result[i])

	def createItemList(self, mode):
		result = []
		for i in self.connection.item:
			result.append(i["name"] + ":" + str(i["count"]))
		result.sort()
		for i in range(len(result)):
			if result[i][0:2] == "MP":
				mp = i
				break
		result[mp], result[-1] = result[-1], result[mp]
		if mode == update:
			cursor = self.MainView.itemList.GetSelection()
			self.MainView.itemList.Clear()
		for i in range(0, len(result)):
			self.MainView.itemList.Insert(result[i], i)
		if mode == update and cursor != wx.NOT_FOUND and self.MainView.itemList.GetCount() - 1 >= cursor:
			self.MainView.itemList.SetSelection(cursor)

	def postComment(self, commentBody, idx):
		commentBody = commentBody.strip()
		if len(commentBody) == 0:
			simpleDialog.errorDialog(_("コメントが入力されていません。"))
			return False
		elif len(commentBody) > 140:
			simpleDialog.errorDialog(_("１４０字を超えるコメントは投稿できません。現在%s文字のコメントが入力されています。") %(str(len(commentBody))))
			return False
		result = self.connection.postComment(commentBody, idx)
		if "error" in result:
			if result["error"]["code"] == 1001 and "comment" in result["error"]["details"] and "length" in result["error"]["details"]["comment"] :
				simpleDialog.errorDialog(_("コメント文字数が１４０字を超えているため、コメントを投稿できません。"))
				return False
			else:
				simpleDialog.errorDialog(_("エラーが発生しました。詳細：%s") %(str(result)))
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

	def copyComment(self):
		selected = self.MainView.commentList.GetFocusedItem()
		pyperclip.copy(self.readComment(self.getCommentdata(self.connection.comments[selected]), False))

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
		if globalVars.app.config.getboolean("fx", "playTimersound") == True:
			self.playFx(globalVars.app.config["fx"]["timerSound"])
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
				if self.livePlayer != None and self.livePlayer.getStatus() == PLAYER_STATUS_PLAYING:
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
			self.newMovieId = self.connection.movieId
			if self.newMovieId != self.oldMovieId:
				if self.connection.isLive == True:
					globalVars.app.say(_("次のライブが開始されました。"))
					self.elapsedTime = self.connection.movieInfo["movie"]["duration"]
					if self.livePlayer != None and self.livePlayer.getStatus() == PLAYER_STATUS_PLAYING:
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
				if i["name"] == "MP":
					continue
				id = i["id"]
				name = i["name"]
				count = i["count"]
				users = self.connection.getItemPostedUser(id, count)
				readItemPostedUser = globalVars.app.config.getint("autoReadingOptions", "readItemPostedUser", 0)
				multiUser = False
				if len(users) > 1:
					for k in range(1, len(users) - 1):
						if users[0] != users[k]:
							multiUser = True
							break
				readReceivedItems = globalVars.app.config.getboolean("autoReadingOptions", "readReceivedItems", True)
				if readReceivedItems == True:
					if readItemPostedUser == 0:
						if count == 1:
							globalVars.app.say(_("%sをもらいました。") %name)
						else:
							globalVars.app.say(_("%sを%i個もらいました。") %(name, count))
					else:
						if readItemPostedUser == 1:
							users[0] = twitcasting.twitcasting.GetUserInfo(users[0])["user"]["screen_id"]
						elif readItemPostedUser == 2:
							users[0] = twitcasting.twitcasting.GetUserInfo(users[0])["user"]["name"]
						if multiUser == False:
							if count == 1:
								globalVars.app.say(_("%sさんから%sをもらいました。") %(users[0], name))
							else:
								globalVars.app.say(_("%sさんから%sを%i個もらいました。") %(users[0], name, count))
						else:
							if count == 1:
								globalVars.app.say(_("%sさんなどから%sをもらいました。") %(users[0], name))
							else:
								globalVars.app.say(_("%sさんなどから%sを%i個もらいました。") %(users[0], name, count))
			if globalVars.app.config.getboolean("fx", "playItemReceivedSound", True) == True and len(receivedItem) != 0:
				self.playFx(globalVars.app.config["fx"]["itemReceivedSound"])
			self.oldItem = self.newItem
			self.createItemList(update)
			self.newCoins = self.connection.coins
			if self.newCoins != self.oldCoins:
				if self.newCoins < self.oldCoins:
					globalVars.app.say(_("コイン消費"))
				if self.newCoins % 5 == 0:
					globalVars.app.say(_("コイン%d枚") %(self.newCoins))
				if self.hasEnoughCoins(self.oldCoins) == False and self.hasEnoughCoins(self.newCoins) == True:
					globalVars.app.say(_("完走に必要なコインが集まりました。"))
			self.oldCoins = self.newCoins
		elif id == evtCountDown:
			self.resetTimer()
			try:
				self.MainView.liveInfo.SetString(1, _("経過時間：%s") %(self.formatTime(self.elapsedTime).strftime("%H:%M:%S")))
				self.MainView.liveInfo.SetString(2, _("残り時間：%s") %(self.formatTime(self.remainingTime).strftime("%H:%M:%S")))
			except:
				self.MainView.liveInfo.SetString(1, _("配信時間が４時間を超えているため、タイマーを使用できません。"))
				self.MainView.liveInfo.SetString(2, _("配信時間が４時間を超えているため、タイマーを使用できません。"))
		elif id == evtTyping:
			typingUser = self.connection.getTypingUser()
			if typingUser != "":
				if globalVars.app.config.getboolean("autoReadingOptions", "readTypingUser", False) == True:
					globalVars.app.say(_("%sさんが入力中") %(typingUser))
				if globalVars.app.config.getboolean("fx", "playTypingSound", True) == True:
					self.playFx(globalVars.app.config["fx"]["typingSound"])
		elif id == evtPlaystatus:
			if self.livePlayer.getStatus() != PLAYER_STATUS_PLAYING and self.livePlayer.getStatus() != PLAYER_STATUS_LOADING:
				self.stop()

	def play(self):
		if self.livePlayer == None:
			self.livePlayer = soundPlayer.player.player()
			self.livePlayer.setAmp(globalVars.app.config.getint("livePlay", "defaultVolume", 100))
			self.livePlayer.setHlsTimeout(globalVars.app.config.getint("livePlay", "audioDelay", 7))
			self.changeDevice(globalVars.app.config["livePlay"]["device"])
		if self.livePlayer.getStatus() != PLAYER_STATUS_PLAYING:
			if self.connection.movieInfo["movie"]["hls_url"] == None:
				simpleDialog.errorDialog(_("再生URLを取得できません。"))
				return
			setSource = self.livePlayer.setSource(self.connection.movieInfo["movie"]["hls_url"])
			if setSource == False:
				simpleDialog.errorDialog(_("再生に失敗しました。"))
				return
			self.livePlayer.play()
			globalVars.app.say(_("再生"))
		self.MainView.menu.EnableMenu("play", False)
		self.MainView.menu.EnableMenu("stop", True)
		self.MainView.menu.EnableMenu("volumeUp", True)
		self.MainView.menu.EnableMenu("volumeDown", True)
		self.MainView.menu.EnableMenu("resetVolume", True)
		self.playStatusTimer.Start(playstatusTimerInterval)

	def stop(self):
		if self.playStatusTimer.IsRunning() == True:
			self.playStatusTimer.Stop()
		if self.livePlayer.getStatus() != PLAYER_STATUS_STOPPED:
			self.livePlayer.stop()
			globalVars.app.say(_("停止"))
		self.MainView.menu.EnableMenu("stop", False)
		self.MainView.menu.EnableMenu("play", True)
		self.MainView.menu.EnableMenu("volumeUp", False)
		self.MainView.menu.EnableMenu("volumeDown", False)
		self.MainView.menu.EnableMenu("resetVolume", False)

	def volumeUp(self):
		self.livePlayer.setAmp(self.livePlayer.getConfig(PLAYER_CONFIG_AMP) + 10)
		globalVars.app.say(_("音量%d") %self.livePlayer.getConfig(PLAYER_CONFIG_AMPVOL))

	def volumeDown(self):
		self.livePlayer.setAmp(self.livePlayer.getConfig(PLAYER_CONFIG_AMP) - 10)
		globalVars.app.say(_("音量%d") %self.livePlayer.getConfig(PLAYER_CONFIG_AMPVOL))

	def resetVolume(self):
		self.livePlayer.setAmp(100)

	def changeDevice(self, deviceName = ""):
		try:
			if deviceName == "":
				result = self.livePlayer.setDevice(PLAYER_DEFAULT_SPEAKER)
			else:
				result = self.livePlayer.setDeviceByName(deviceName)
		except AttributeError:
			result = True
		if result == True:
			if deviceName == "":
				globalVars.app.config["livePlay"]["device"] = ""
			else:
				globalVars.app.config["livePlay"]["device"] = deviceName
		else:
			self.changeDevice()

	def playFx(self, filePath = ""):
		if globalVars.app.config.getboolean("fx", "syncAudioDevice", False) == True and globalVars.app.config["livePlay"]["device"] != "":
			device = globalVars.app.config["livePlay"]["device"]
		else:
			device = PLAYER_DEFAULT_SPEAKER
		soundPlayer.fxPlayer.playFx(filePath, device, globalVars.app.config.getint("fx", "fxVolume", 100, 0, 100))

	def playCommentReceivedSoundIfSkipped(self):
		if globalVars.app.config.getboolean("fx", "playcommentreceivedsound", True) == True and globalVars.app.config.getboolean("fx", "playcommentreceivedsoundifskipped", False) == True:
			self.playFx(globalVars.app.config["fx"]["commentreceivedsound"])
	def changeMenuState(self, connectionState):
		if connectionState == False:
			menuItems = {
				"connect": True,
				"viewHistory": True,
				"viewFavorites": True,
				"disconnect": False,
				"play": False,
				"stop": False,
				"volumeUp": False,
				"volumeDown": False,
				"resetVolume": False,
				"viewComment": False,
				"replyToSelectedComment": False,
				"deleteSelectedComment": False,
				"replyToBroadcaster": False,
				"viewBroadcaster": False,
				"openLive": False,
				"addFavorites": False,
				"accountManager": True,
			}
		elif connectionState == True:
			menuItems = {
				"connect": False,
				"viewHistory": False,
				"viewFavorites": False,
				"disconnect": True,
				"play": True,
				"replyToBroadcaster": True,
				"viewBroadcaster": True,
				"openLive": True,
				"addFavorites": True,
				"accountManager": False,
			}
		for key, value in menuItems.items():
			self.MainView.menu.EnableMenu(key, value)

	def openLiveWindow(self):
		webbrowser.open("https://twitcasting.tv/%s" %(self.connection.movieInfo["broadcaster"]["screen_id"]))

	def hasEnoughCoins(self, count):
		current = (self.elapsedTime + (1800 - (self.elapsedTime % 1800))) // 1800 - 1
		current = current * 5
		return current + count >= 35

	def refreshReplaceSettings(self):
		if hasattr(self, "connection") == False:
			return
		for idx in range(len(self.connection.comments)):
			name = self.connection.comments[idx]["from_user"]["name"]
			for i in globalVars.app.config.items("nameReplace"):
				if i[0] == self.connection.comments[idx]["from_user"]["screen_id"]:
					name = i[1]
			self.MainView.commentList.SetItem(idx, 0, name)
			body = self.connection.comments[idx]["message"]
			for i in globalVars.app.config.items("commentReplaceBasic"):
				body = body.replace(i[0], i[1])
			for i in globalVars.app.config.items("commentReplaceReg"):
				body = re.sub(i[0], i[1], body)
			urls = list(self.connection.comments[idx]["urls"])
			domains = re.finditer("(https?://[^/]+/)", body)
			for url in urls:
				for domain in domains:
					if len(globalVars.app.config["commentReplaceSpecial"]["url"]) != 0:
						body = re.sub(url.group(), globalVars.app.config["commentReplaceSpecial"]["url"], body)
					if globalVars.app.config.getboolean("commentReplaceSpecial", "deleteProtcolName", False) == True:
						body = body.replace("http://", "")
						body = body.replace("https://", "")
					if globalVars.app.config.getboolean("commentReplaceSpecial", "onlyDomain", False) == True:
						body = body.replace(url.group(), domain.group())
			self.MainView.commentList.SetItem(idx, 1, body)
