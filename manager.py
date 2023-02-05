# -*- coding: utf-8 -*-
# manager

import json
import threading
import time
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
import sys
from copy import deepcopy
import os
import traceback
import logging
import requests
import websocket

evtComment = 0
evtLiveInfo = 1
evtCountDown = 2
evtTyping = 3
evtPlaystatus = 4
evtError = 5

first = 0
update = 1

commentTimerInterval = 3000
liveInfoTimerInterval = 5000
countDownTimerInterval = 1000
typingTimerInterval = 5000
playstatusTimerInterval = 500
errorCheckTimerInterval = 1000

historyData = pathlib.Path(constants.HISTORY_FILE_NAME)
favoritesData = pathlib.Path(constants.FAVORITES_FILE_NAME)

# mainViewAccess
block = 0
def mainViewAccess(func):
	def wrapper(*args, **kwargs):
		global block
		block += 1
		ret = func(*args, **kwargs)
		block -= 1
		return ret
	return wrapper

class manager:
	def __init__(self, MainView):
		self.log = logging.getLogger("%s.%s" %(constants.LOG_PREFIX, "manager"))
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
		userId = userId.replace("tcv://twitcasting.tv/", "")
		if "/" in userId:
			userId = userId[0:userId.find("/")]
		if globalVars.app.accountManager.hasDefaultAccount() == False:
			if len(globalVars.app.accountManager.tokens) == 0:
				simpleDialog.errorDialog(_("アカウントが登録されていません。ライブに接続する前に、設定メニューのアカウントマネージャからアカウントの登録を行ってください。"))
			else:
				simpleDialog.errorDialog(_("通信用アカウントが設定されていません。ライブに接続する前に、設定メニューのアカウントマネージャから通信用アカウントの設定を行ってください。"))
			self.MainView.createStartScreen()
			return
		self.connection = twitcasting.connection.connection(userId)
		self.errorCheckTimer = wx.Timer(self.evtHandler, evtError)
		self.timers.append(self.errorCheckTimer)
		self.errorCheckTimer.Start(errorCheckTimerInterval)
		if self.connection.connected == False:
			simpleDialog.errorDialog(_("接続に失敗しました。"))
			self.MainView.createStartScreen()
			return
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
		try:
			historyData.write_text("\n".join(self.history))
		except Exception as e:
			simpleDialog.errorDialog(_("履歴データの保存に失敗しました。以下のファイルへのアクセスが可能であることを確認してください。") + "\n" + os.path.abspath(constants.HISTORY_FILE_NAME))
			traceback.print_exc()
			self.log.warning("Failed to write history data. detail:" + traceback.format_exc())
		self.connection.updateMovieType()
		try:
			self.elapsedTime = self.connection.movieInfo["movie"]["duration"]
		except:
			self.elapsedTime = 0
		self.countDownTimer = wx.Timer(self.evtHandler, evtCountDown)
		self.timers.append(self.countDownTimer)
		initialCommentCount = globalVars.app.config.getint("general", "initialCommentCount", 50)
		self.initialComments = self.connection.getInitialComment(initialCommentCount)
		self.addComments(self.initialComments, first)
		self.commentTimer = wx.Timer(self.evtHandler, evtComment)
		self.timers.append(self.commentTimer)
		self.commentTimer.Start(commentTimerInterval)
		self.liveInfoTimer = wx.Timer(self.evtHandler, evtLiveInfo)
		self.timers.append(self.liveInfoTimer)
		self.liveInfoTimer.Start(liveInfoTimerInterval)
		self.createLiveInfoList(first)
		if self.connection.isLive == True:
			if self.connection.is_games:
				globalVars.app.say(_("接続。ゲームズ配信中。"))
			elif self.connection.is_vtuber:
				globalVars.app.say(_("接続。VTuber配信中。"))
			elif self.connection.is_corporate_broadcasting:
				globalVars.app.say(_("接続。法人向けプログラムで配信中。"))
			else:
				globalVars.app.say(_("接続。現在配信中。"))
			self.elapsedTime += int(time.time() - self.connection.movieInfo["duration_updated_at"])
			self.resetTimer()
			self.countDownTimer.Start(countDownTimerInterval)
			globalVars.app.say(_("タイマー開始。"))
			try:
				globalVars.app.say(_("残り時間：%s") %self.formatTime(self.remainingTime).strftime("%H:%M:%S"))
			except:
				globalVars.app.say(_("配信時間が４時間を超えているため、タイマーを使用できません。"))
			if self.hasEnoughCoins(self.connection.coins) == True:
				globalVars.app.say(_("完走に必用なコインが集まっています。"))
		else:
			self.resetTimer()
			globalVars.app.say(_("接続。現在オフライン。"))
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
		titlebar = globalVars.app.config.getint("general", "titlebar", 1, 0, 2)
		if titlebar == constants.TB_USER:
			self.MainView.hFrame.SetTitle("%s - %s" %(self.connection.userId, constants.APP_NAME))
		if globalVars.app.config.getboolean("livePlay", "autoPlay", False) == True and self.connection.movieInfo["movie"]["hls_url"] != None:
			self.play()
		if globalVars.app.config.getboolean("general", "openlivewindow", False) == True:
			self.openLiveWindow()
		self.connection.start()
		self.items = []
		if self.connection.movieId:
			self.itemWatcher = ItemWatcher(self, self.connection.movieId)
			self.itemWatcher.start()

	def disconnect(self):
		self.connection.running = False
		if hasattr(self, "itemWatcher"):
			self.itemWatcher.exit()
		if self.livePlayer != None:
			self.stop()
			self.livePlayer.exit()
		self.livePlayer = None
		for i in self.timers:
			i.Stop()
		self.MainView.Clear()
		self.MainView.hFrame.SetTitle(constants.APP_NAME)
		self.MainView.createStartScreen()
		self.changeMenuState(False)
		self.connection.connected = False

	def getPopular(self):
		self.log.debug("getting popular live movies...")
		ret = twitcasting.twitcasting.searchLiveMovies("recommend", limit=100)
		if "error" in ret:
			self.log.error(ret)
		return ret

	@mainViewAccess
	def getNewComments(self):
		limit = len(self.connection.comments) - self.MainView.commentList.GetItemCount()
		result = self.connection.comments[:limit]
		result.reverse()
		return result

	@mainViewAccess
	def addComments(self, commentList, mode):
		for commentObject in commentList:
			commentData = self.getCommentdata(commentObject)
			self.MainView.commentList.InsertItem(0	, "")
			self.MainView.commentList.SetItem(0, 0, commentData["dispname"])
			self.MainView.commentList.SetItem(0, 1, commentData["message"])
			self.MainView.commentList.SetItem(0, 2, commentData["time"])
			self.MainView.commentList.SetItem(0, 3, commentData["user"])
			self.MainView.commentList.Focus(self.MainView.commentList.GetFocusedItem() + 1)
			sels = self.MainView.commentList.getItemSelections()
			for i in sels:
				self.MainView.commentList.Select(i, 0)
			for i in sels:
				self.MainView.commentList.Select(i + 1, 1)
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

	@mainViewAccess
	def createLiveInfoList(self, mode):
		result = [
			_("タイトル：%s") %(self.connection.movieInfo["movie"]["title"]),
			_("テロップ：%s") %(self.connection.movieInfo["movie"]["subtitle"]),
			_("閲覧者数：現在%(current)d人、合計%(total)d人") %{"current": self.connection.movieInfo["movie"]["current_view_count"], "total": self.connection.movieInfo["movie"]["total_view_count"]},
			_("カテゴリ：%s") %(self.connection.categoryName),
			_("コメント：%d件") %(self.connection.movieInfo["movie"]["comment_count"]),
			self.connection.movieInfo["broadcaster"]["screen_id"]
		]
		if self.connection.movieInfo["movie"]["is_live"] == True:
			if self.connection.is_games:
				result.insert(0, _("ゲームズ配信中"))
			elif self.connection.is_vtuber:
				result.insert(0, _("VTuber配信中"))
			elif self.connection.is_corporate_broadcasting:
				result.insert(0, _("法人向け配信中"))
			else:
				result.insert(0, _("配信中"))
		else:
			result.insert(0, _("オフライン"))
		try:
			result.insert(1, _("経過時間：%s") %(self.formatTime(self.elapsedTime).strftime("%H:%M:%S")))
			result.insert(2, _("残り時間：%s") %(self.formatTime(self.remainingTime).strftime("%H:%M:%S")))
		except:
			result.insert(2, _("残り時間：無制限"))
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

	@mainViewAccess
	def createItemList(self, mode):
		result = []
		for i in self.connection.item:
			result.append(i["name"] + ":" + str(i["count"]))
		result.sort()
		mp = None
		for i in range(len(result)):
			if result[i][0:2] == "MP":
				mp = i
				break
		if type(mp) == int:
			result[mp], result[-1] = result[-1], result[mp]
		if mode == update:
			cursor = self.MainView.itemList.GetSelection()
			self.MainView.itemList.Clear()
		for i in range(0, len(result)):
			self.MainView.itemList.Insert(result[i], i)
		if mode == update and cursor != wx.NOT_FOUND and self.MainView.itemList.GetCount() - 1 >= cursor:
			self.MainView.itemList.SetSelection(cursor)

	def postComment(self, commentBody, idx):
		if self.connection.movieId == None:
			simpleDialog.errorDialog(_("コメント投稿に失敗しました。次にこのユーザがライブを行うまで、コメントを投稿できません。"))
			return False
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
			elif result["error"]["code"] == 404:
				simpleDialog.errorDialog(_("コメント投稿に失敗しました。次にこのユーザがライブを行うまで、コメントを投稿できません。"))
				return False
			else:
				simpleDialog.errorDialog(_("エラーが発生しました。詳細：%s") %(str(result)))
				return False
		else:
			if globalVars.app.config.getboolean("fx", "playCommentPostedSound", True) == True:
				self.playFx(globalVars.app.config["fx"]["commentPostedSound"])
			return True

	def formatTime(self, second):
		if second<0:
			raise ValueError("second must be larger than 0.")
		time = datetime.time(hour = int(second / 3600), minute = int(second % 3600 / 60), second = int(second % 3600 % 60))
		return time

	@mainViewAccess
	def deleteComment(self):
		tmp = len(self.connection.comments) - self.MainView.commentList.GetItemCount()
		selected = self.MainView.commentList.getItemSelections()
		selected.reverse()
		success = 0
		fail = 0
		for i in selected:
			lstidx = i + tmp
			result = self.connection.deleteComment(self.connection.comments[lstidx])
			if result == False:
				fail += 1
			else:
				success += 1
				del self.connection.comments[lstidx]
				self.MainView.commentList.DeleteItem(i)
		if success == 0:
			simpleDialog.errorDialog(_("コメントの削除に失敗しました。これらのコメントを削除する権限がありません。"))
		elif success > 0 and fail > 0:
			simpleDialog.errorDialog(_("%d個のコメントを削除できませんでした。これらのコメントを削除する権限がありません。") %fail)

	@mainViewAccess
	def copyComment(self):
		selections = self.MainView.commentList.getItemSelections()
		tmplst = deepcopy(self.connection.comments)
		if len(tmplst) > self.MainView.commentList.GetItemCount():
			tmplst = tmplst[-1 * self.MainView.commentList.GetItemCount():]
		items = [self.readComment(self.getCommentdata(tmplst[i]), False) for i in selections]
		pyperclip.copy("\n\n".join(items))

	def resetTimer(self, speech = False):
		if speech == True:
			globalVars.app.say(_("タイマーリセット。"))
		timerType = globalVars.app.config.getint("general", "timerType", 0)
		if self.connection.isLive == False:
			self.elapsedTime = 0
			self.remainingTime = 0
			return
		if self.connection.is_corporate_broadcasting:	# コーポレート
			totalTime = 60*60*24						# 24時間固定
		elif self.connection.is_vtuber:					# vtuber
			totalTime = 60*60*4							# 4時間固定
		elif self.connection.is_games:					# ゲーム配信
			tmp = 1800 - (self.elapsedTime % 1800)
			if timerType == 0:
				totalTime = self.elapsedTime + tmp
			else:
				if self.elapsedTime >= 60*60*4:
					totalTime = self.elapsedTime + tmp + (int(self.connection.coins / 5) * 1800)
				else:
					totalTime = 60*60*4 + (int(self.connection.coins / 5) * 1800)
				if totalTime > 60*60*8:					# 上限8時間
					totalTime = 60*60*8
		else:											# 通常配信
			tmp = 1800 - (self.elapsedTime % 1800)
			if timerType == 0:
				totalTime = self.elapsedTime + tmp
			else:
				totalTime = self.elapsedTime + tmp + (int(self.connection.coins / 5) * 1800)
				if totalTime > 14400:					# 4時間上限
					totalTime = 14400
		self.elapsedTime = self.elapsedTime + 1
		self.remainingTime = totalTime - self.elapsedTime

		if self.connection.is_games and self.elapsedTime <= 60*60*3.5:
			# 4H無料なので3.5Hまでは読上げ不要
			return
		if (self.connection.is_vtuber or self.connection.is_corporate_broadcasting) and self.remainingTime >= 1800:
			# コインや延長という概念がない枠は残り30分以上の場合読み上げ不要
			return
		if timerType == 2 and self.remainingTime >= 1800:
			# vtuberの3.5H以降と通常配信で、残り30分以上ある＝延長可能な場合のみここにくる
			if int(self.remainingTime % 1800) == 180:
				self.sayRemainingTime()
				globalVars.app.say(_("コインが%d枚あるので延長可能です。") %(self.connection.coins))
			return
		announceTime = [900, 600, 300, 180, 60, 30, 10]
		for i in announceTime:
			if self.remainingTime % 1800 == i:
				self.sayRemainingTime()
				if self.remainingTime >= 1800 and timerType != 0:
					globalVars.app.say(_("コインが%d枚あるので延長可能です。") %(self.connection.coins))
		if self.remainingTime > 0 and self.remainingTime % 1800 == 0:
			globalVars.app.say(_("次の枠に切り替わります。"))

	def clearHistory(self):
		self.history.clear()
		try:
			historyData.write_text("\n".join(self.history))
		except Exception as e:
			simpleDialog.errorDialog(_("履歴データの保存に失敗しました。以下のファイルへのアクセスが可能であることを確認してください。") + "\n" + os.path.abspath(constants.HISTORY_FILE_NAME))
			traceback.print_exc()
			self.log.warning("Failed to write history data. detail:" + traceback.format_exc())

	def addFavorites(self):
		self.favorites.insert(0, self.connection.userId.lower())
		self.favorites.sort()
		try:
			favoritesData.write_text("\n".join(self.favorites))
		except Exception as e:
			simpleDialog.errorDialog(_("お気に入りデータの保存に失敗しました。以下のファイルへのアクセスが可能であることを確認してください。") + "\n" + os.path.abspath(constants.FAVORITES_FILE_NAME))
			traceback.print_exc()
			self.log.warning("Failed to write favorites data. detail:" + traceback.format_exc())

	def deleteFavorites(self, index):
		del self.favorites[index]
		self.favorites.sort()
		try:
			favoritesData.write_text("\n".join(self.favorites))
		except Exception as e:
			simpleDialog.errorDialog(_("お気に入りデータの保存に失敗しました。以下のファイルへのアクセスが可能であることを確認してください。") + "\n" + os.path.abspath(constants.FAVORITES_FILE_NAME))
			traceback.print_exc()
			self.log.warning("Failed to write favorites data. detail:" + traceback.format_exc())

	def clearFavorites(self):
		self.favorites.clear()
		try:
			favoritesData.write_text("\n".join(self.favorites))
		except Exception as e:
			simpleDialog.errorDialog(_("お気に入りデータの保存に失敗しました。以下のファイルへのアクセスが可能であることを確認してください。") + "\n" + os.path.abspath(constants.FAVORITES_FILE_NAME))
			traceback.print_exc()
			self.log.warning("Failed to write favorites data. detail:" + traceback.format_exc())

	def sayRemainingTime(self):
		if globalVars.app.config.getboolean("fx", "playTimersound") == True:
			self.playFx(globalVars.app.config["fx"]["timerSound"])
		remainingTime = self.formatTime(self.remainingTime % 1800)
		if remainingTime.minute == 0:
			string = _("残り%s秒です。") %(str(remainingTime.second))
		elif remainingTime.second == 0:
			string = _("残り%s分です。") %(str(remainingTime.minute))
		else:
			string = _("残り%(minutes)s分%(seconds)s秒です。") %{"minutes": str(remainingTime.minute), "seconds": str(remainingTime.second)}
		if globalVars.app.config.getboolean("autoReadingOptions", "readRemainingTime", True):
			globalVars.app.say(string)

	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == evtComment:
			self.checkComment()
		elif id == evtLiveInfo:
			self.checkIsLive()
			self.checkSubtitle()
			self.checkCategory()
			self.checkMovieId()
			self.checkViewers()
			self.createLiveInfoList(update)
			self.createItemList(update)
			self.checkCoins()
		elif id == evtCountDown:
			self.resetTimer()
			try:
				self.MainView.liveInfo.SetString(1, _("経過時間：%s") %(self.formatTime(self.elapsedTime).strftime("%H:%M:%S")))
				self.MainView.liveInfo.SetString(2, _("残り時間：%s") %(self.formatTime(self.remainingTime).strftime("%H:%M:%S")))
				titlebar = globalVars.app.config.getint("general", "titlebar", 1, 0, 2)
				if titlebar == constants.TB_TIME:
					t = self.formatTime(self.remainingTime)
					map = {"hour": t.hour, "minute": t.minute, "second": t.second}
					if t.hour > 0:
						disp = _("残り%(hour)d時間%(minute)d分%(second)d秒") %map
					elif t.minute > 0:
						disp = _("残り%(minute)d分%(second)d秒") %map
					else:
						disp = _("残り%(second)d秒") %map
					self.MainView.hFrame.SetTitle(disp + " - " + constants.APP_NAME)
			except:
				self.MainView.liveInfo.SetString(2, _("残り時間：無制限"))
		elif id == evtTyping:
			if self.connection.typingUser != "":
				if globalVars.app.config.getboolean("autoReadingOptions", "readTypingUser", False) == True:
					globalVars.app.say(_("%sさんが入力中") %(typingUser))
				if globalVars.app.config.getboolean("fx", "playTypingSound", True) == True:
					self.playFx(globalVars.app.config["fx"]["typingSound"])
		elif id == evtPlaystatus:
			if self.livePlayer.getStatus() != PLAYER_STATUS_PLAYING and self.livePlayer.getStatus() != PLAYER_STATUS_LOADING:
				self.stop()
		elif id == evtError:
			self.checkError()

	def checkComment(self):
		newComments = self.getNewComments()
		self.addComments(newComments, update)

	def checkIsLive(self):
		self.newIsLive = self.connection.isLive
		if self.oldIsLive == True and self.newIsLive == False:
			globalVars.app.say(_("ライブ終了。"))
			self.countDownTimer.Stop()
			titlebar = globalVars.app.config.getint("general", "titlebar", 1, 0, 2)
			if titlebar == constants.TB_TIME:
				self.MainView.hFrame.SetTitle("%s" %constants.APP_NAME)
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

	def checkSubtitle(self):
		self.newSubtitle = self.connection.subtitle
		if self.newSubtitle != self.oldSubtitle and self.connection.isLive == True:
			if self.newSubtitle == None:
				globalVars.app.say(_("テロップ削除"))
			else:
				globalVars.app.say(_("テロップ変更。"))
				globalVars.app.say(self.newSubtitle)
			if globalVars.app.config.getboolean("fx", "playothersound", True) == True:
				self.playFx(globalVars.app.config["fx"]["othersound"])
		self.oldSubtitle = self.newSubtitle

	def checkCategory(self):
		self.newCategory = self.connection.categoryName
		if self.newCategory != self.oldCategory and self.connection.isLive == True:
			globalVars.app.say(_("カテゴリ変更：%s") %self.newCategory)
			if globalVars.app.config.getboolean("fx", "playothersound", True) == True:
				self.playFx(globalVars.app.config["fx"]["othersound"])
		self.oldCategory = self.newCategory

	def checkMovieId(self):
		self.newMovieId = self.connection.movieId
		if self.newMovieId != self.oldMovieId:
			self.itemWatcher.exit()
			self.itemWatcher = ItemWatcher(self, self.newMovieId)
			self.itemWatcher.start()
			self.connection.updateMovieType()
			if self.connection.isLive == True:
				if self.connection.is_games:
					globalVars.app.say(_("次のゲームズ配信が開始されました。"))
				elif self.connection.is_vtuber:
					globalVars.app.say(_("次のVTuber配信が開始されました。"))
				elif self.connection.is_corporate_broadcasting:
					globalVars.app.say(_("次の法人向けプログラム配信が開始されました。"))
				else:
					globalVars.app.say(_("次のライブが開始されました。"))
				self.elapsedTime = self.connection.movieInfo["movie"]["duration"]
				if self.livePlayer != None and self.livePlayer.getStatus() == PLAYER_STATUS_PLAYING:
					self.stop()
					self.play()
		self.oldMovieId = self.newMovieId

	def checkViewers(self):
		self.newViewers = self.connection.viewers
		if self.newViewers != self.oldViewers and self.connection.isLive == True:
			if self.newViewers > self.oldViewers:
				if globalVars.app.config.getboolean("fx", "playviewersincreasedsound", True) == True:
					self.playFx(globalVars.app.config["fx"]["viewersincreasedSound"])
				if globalVars.app.config.getboolean("autoReadingOptions", "readviewersincreased", True) == True:
					viewersInfo = globalVars.app.config["autoReadingOptions"]["viewersincreasedAnnouncement"]
					viewersInfo = viewersInfo.replace("$viewers", str(self.newViewers))
					globalVars.app.say(viewersInfo)
			elif self.newViewers < self.oldViewers:
				if globalVars.app.config.getboolean("fx", "playviewersdecreasedsound", True) == True:
					self.playFx(globalVars.app.config["fx"]["viewersdecreasedSound"])
				if globalVars.app.config.getboolean("autoReadingOptions", "readviewersdecreased", True) == True:
					viewersInfo = globalVars.app.config["autoReadingOptions"]["viewersDecreasedAnnouncement"]
					viewersInfo = viewersInfo.replace("$viewers", str(self.newViewers))
					globalVars.app.say(viewersInfo)
		self.oldViewers = self.newViewers

	def checkCoins(self):
		if not self.isCoinSupportedLive():
			return
		self.newCoins = self.connection.coins
		if self.newCoins != self.oldCoins:
			if self.newCoins < self.oldCoins:
				globalVars.app.say(_("コイン消費"))
			elif self.newCoins > self.oldCoins:
				c = [i for i in range(self.oldCoins + 1, self.newCoins + 1) if i % 5 == 0]
				if len(c) > 0:
					if self.hasEnoughCoins(self.oldCoins) == False and self.hasEnoughCoins(c[-1]) == True:
						globalVars.app.say(_("完走に必要なコイン%d枚が集まりました。") %(c[-1]))
					else:
						globalVars.app.say(_("コインが%d枚集まりました。") %(c[-1]))

		self.oldCoins = self.newCoins

	def getStreamingUrl(self):
		ret = [self.connection.movieInfo["movie"]["hls_url"]]
		if globalVars.app.config.getboolean("livePlay", "login", False):
			accounts = list(globalVars.app.config["advanced_ids"].keys())
			if len(accounts) == 0:
				return "\r\n".join(ret)
			account = globalVars.app.advancedAccountManager.getDefaultAccount()
			if not globalVars.app.advancedAccountManager.login(account):
				return "\r\n".join(ret)
			if not globalVars.app.advancedAccountManager.isActive(account):
				if not globalVars.app.advancedAccountManager.relogin(account):
					return "\r\n".join(ret)
			session = globalVars.app.advancedAccountManager.getSession(account)
			cookies = session.cookies
			ret.append("Cookie: tc_id=%s;tc_ss=%s" % (cookies["tc_id"], cookies["tc_ss"]))
		return "\r\n".join(ret)

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
			source = self.getStreamingUrl()
			self.log.debug("streaming URL: %s" % source)
			setSource = self.livePlayer.setSource(source)
			if setSource == False:
				simpleDialog.errorDialog(_("再生に失敗しました。"))
				return
			self.livePlayer.play()
			globalVars.app.say(_("再生"))
		self.MainView.menu.EnableMenu("PLAY", False)
		self.MainView.menu.EnableMenu("STOP", True)
		self.MainView.menu.EnableMenu("VOLUME_UP", True)
		self.MainView.menu.EnableMenu("VOLUME_DOWN", True)
		self.MainView.menu.EnableMenu("RESET_VOLUME", True)
		self.playStatusTimer.Start(playstatusTimerInterval)

	def stop(self):
		if self.playStatusTimer.IsRunning() == True:
			self.playStatusTimer.Stop()
		if self.livePlayer.getStatus() != PLAYER_STATUS_STOPPED:
			self.livePlayer.stop()
			globalVars.app.say(_("停止"))
		self.MainView.menu.EnableMenu("STOP", False)
		self.MainView.menu.EnableMenu("PLAY", True)
		self.MainView.menu.EnableMenu("VOLUME_UP", False)
		self.MainView.menu.EnableMenu("VOLUME_DOWN", False)
		self.MainView.menu.EnableMenu("RESET_VOLUME", False)

	def volumeUp(self):
		self.livePlayer.setAmp(self.livePlayer.getConfig(PLAYER_CONFIG_AMP) + 10)
		globalVars.app.say(_("音量%d") %self.livePlayer.getConfig(PLAYER_CONFIG_AMPVOL), True)

	def volumeDown(self):
		self.livePlayer.setAmp(self.livePlayer.getConfig(PLAYER_CONFIG_AMP) - 10)
		globalVars.app.say(_("音量%d") %self.livePlayer.getConfig(PLAYER_CONFIG_AMPVOL), True)

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
				"CONNECT": True,
				"VIEW_HISTORY": True,
				"VIEW_FAVORITES": True,
				"VIEW_POPULAR": True,
				"DISCONNECT": False,
				"PLAY": False,
				"STOP": False,
				"VOLUME_UP": False,
				"VOLUME_DOWN": False,
				"RESET_VOLUME": False,
				"COPY_COMMENT": False,
				"VIEW_COMMENT": False,
				"REPLY2SELECTED_COMMENT": False,
				"DELETE_SELECTED_COMMENT": False,
				"SELECT_ALL_COMMENT": False,
				"REPLY2BROADCASTER": False,
				"VIEW_BROADCASTER": False,
				"OPEN_LIVE": False,
				"ADD_FAVORITES": False,
				"POST_ITEM": False,
				"ACCOUNT_MANAGER": True,
			}
		elif connectionState == True:
			menuItems = {
				"CONNECT": False,
				"VIEW_HISTORY": False,
				"VIEW_FAVORITES": False,
				"VIEW_POPULAR": False,
				"DISCONNECT": True,
				"PLAY": True,
				"REPLY2BROADCASTER": True,
				"VIEW_BROADCASTER": True,
				"OPEN_LIVE": True,
				"ADD_FAVORITES": True,
				"POST_ITEM": True,
				"ACCOUNT_MANAGER": False,
			}
		for key, value in menuItems.items():
			self.MainView.menu.EnableMenu(key, value)

	def openLiveWindow(self):
		webbrowser.open("https://twitcasting.tv/%s" %(self.connection.movieInfo["broadcaster"]["screen_id"]))

	def isCoinSupportedLive(self):
		return not (self.connection.is_vtuber or self.connection.is_corporate_broadcasting)

	def hasEnoughCoins(self, count):
		if not self.isCoinSupportedLive():
			return False				# コイン利用不可

		if self.connection.is_games:
			if self.elapsedTime >= 60*60*4:
				current = (self.elapsedTime - 60*60*4 + (1800 - (self.elapsedTime % 1800))) // 1800
			else:
				current = 0
			current = current * 5		# 使用済みコイン枚数
			return current + count >= 40
		else:
			current = (self.elapsedTime + (1800 - (self.elapsedTime % 1800))) // 1800 - 1
			current = current * 5		# 使用済みコイン枚数
			return current + count >= 35

	def refreshReplaceSettings(self):
		if hasattr(self, "connection") == False or hasattr(self.MainView, "commentList") == False or self.MainView.commentList == None:
			return
		tmplst = deepcopy(self.connection.comments)
		if len(tmplst) > self.MainView.commentList.GetItemCount():
			tmplst = tmplst[-1 * self.MainView.commentList.GetItemCount():]
		for idx in range(len(tmplst)):
			name = tmplst[idx]["from_user"]["name"]
			for i in globalVars.app.config.items("nameReplace"):
				if i[0] == tmplst[idx]["from_user"]["screen_id"]:
					name = i[1]
			self.MainView.commentList.SetItem(idx, 0, name)
			body = tmplst[idx]["message"]
			for i in globalVars.app.config.items("commentReplaceBasic"):
				body = body.replace(i[0], i[1])
			for i in globalVars.app.config.items("commentReplaceReg"):
				body = re.sub(i[0], i[1], body)
			urls = list(tmplst[idx]["urls"])
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

	def checkError(self):
		code = self.connection.errorFlag
		if code != 0:
			self.errorCheckTimer.Stop()
			if code == 1000:
				simpleDialog.errorDialog(_("アクセストークンが不正です。設定メニューのアカウントマネージャから、再度アカウントの追加を行ってください。"))
			elif code == 2000:
				simpleDialog.errorDialog(_("APIの実行回数が上限に達しました。しばらくたってから、再度実行してください。"))
			elif code == 500:
				simpleDialog.errorDialog(_("ツイキャスAPIが500エラーを返しました。しばらく待ってから、再度接続してください。"))
			elif code == 2001:
				simpleDialog.errorDialog(_("現在TCVは使用できません。開発者に連絡してください。"))
				sys.exit(-1)
			else:
				detail = {
					1001: "Validation Error",
					1002: "Invalid WebHook URL",
					2002: "Protected",
					2003: "Duplicate",
					2004: "Too Many Comments",
					2005: "Out Of Scope",
					2006: "Email Unverified",
					400: "Bad Request",
					403: "Forbidden",
					404: "Not Found",
				}
				simpleDialog.errorDialog(_("ツイキャスAPIとの通信中にエラーが発生しました。詳細：%s") %(detail[code]))
			self.disconnect()

	def canExit(self):
		return block == 0

class ItemWatcher(threading.Thread):
	def __init__(self, manager, movieId):
		super().__init__(daemon=True)
		self.log = logging.getLogger("%s.%s" %(constants.LOG_PREFIX, "itemWatcher"))
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
			ret =  response["url"]
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
				if i["type"] != "gift":
					continue
				self.manager.items.insert(0, {"item": i["item"]["name"], "user": i["sender"]["screenName"]})
				itemName = i["item"]["name"]
				lst = items.get(itemName, [])
				lst.append(i)
				items[itemName] = lst
			if items:
				self.processItems(items)
		except Exception as e:
			self.log.error("Failed to get item info")
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
				if multiUser == False:
					if count == 1:
						globalVars.app.say(_("%(user)sさんから%(item)sをもらいました。") % {"user": user, "item": name})
					else:
						globalVars.app.say(_("%(user)sさんから%(item)sを%(count)i個もらいました。") % {"user": user, "item": name, "count": count})
				else:
					if count == 1:
						globalVars.app.say(_("%(user)sさんなどから%(item)sをもらいました。") %{"user": user, "item": name})
					else:
						globalVars.app.say(_("%(user)sさんなどから%(item)sを%(count)i個もらいました。") % {"user": user, "item": name, "count": count})

	def exit(self):
		self.log.debug("exitting...")
		self.shouldExit = True
		if hasattr(self, "socket"):
			self.socket.close()
