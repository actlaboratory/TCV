# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime
import wx
import globalVars
import simpleDialog

evtComment = 0
evtLiveInfo = 1
evtCountDown = 2

first = 0
update = 1

commentTimerInterval = 5000
liveInfoTimerInterval = 10000
countDownTimerInterval = 1000
class manager:
	def __init__(self, MainView):
		self.MainView = MainView
		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.timer)

	def connect(self, userId):
		self.connection = twitcasting.connection.connection(userId)
		if self.connection.connected == False:
			simpleDialog.dialog(_("エラー"), _("指定されたユーザが見つかりません。"))
		else:
			self.countDownTimer = wx.Timer(self.evtHandler, evtCountDown)
			if self.connection.isLive == True:
				globalVars.app.say(_("接続。現在配信中。"))
				self.countDownTimer.Start(countDownTimerInterval)
				globalVars.app.say(_("タイマー開始。"))
			else:
				globalVars.app.say(_("接続。現在オフライン。最終配信時の情報を表示中。"))
				self.connection.elapsedTime = 0
				self.connection.remainingTime = 0
			self.initialComments = self.connection.getInitialComment(50)
			self.commentTimer = wx.Timer(self.evtHandler, evtComment)
			self.commentTimer.Start(commentTimerInterval)
			self.addComments(self.initialComments, first)
			self.connection.getLiveInfo()
			self.oldViewers = self.connection.movieInfo["movie"]["current_view_count"]
			self.oldIsLive = self.connection.isLive
			self.liveInfoTimer = wx.Timer(self.evtHandler, evtLiveInfo)
			self.liveInfoTimer.Start(liveInfoTimerInterval)
			self.createLiveInfoList(first)

	def addComments(self, commentList, mode):
		for i in commentList:
			result = {
				"dispname": i["from_user"]["name"],
				"message": i["message"],
				"time": datetime.datetime.fromtimestamp(i["created"]).strftime("%H:%M:%S"),
				"user": i["from_user"]["screen_id"]
			}
			self.MainView.commentList.InsertItem(0	, "")
			self.MainView.commentList.SetItem(0, 0, result["dispname"])
			self.MainView.commentList.SetItem(0, 1, result["message"])
			self.MainView.commentList.SetItem(0, 2, result["time"])
			self.MainView.commentList.SetItem(0, 3, result["user"])

			if mode == update:
				globalVars.app.say("%(dispname)s, %(message)s, %(time)s, %(user)s" %{"dispname": result["dispname"], "message": result["message"], "time": result["time"], "user": result["user"]})

	def createLiveInfoList(self, mode):
		result = [
			_("経過時間：%(elapsedTime)s、残り時間：%(remainingTime)s") %{"elapsedTime": self.formatTime(self.connection.elapsedTime).strftime("%H:%M:%S"), "remainingTime": self.formatTime(self.connection.remainingTime).strftime("%H:%M:%S")},
			_("タイトル：%(title)s") %{"title": self.connection.movieInfo["movie"]["title"]},
			_("閲覧：現在%(current)d人、合計%(total)d人") %{"current": self.connection.movieInfo["movie"]["current_view_count"], "total": self.connection.movieInfo["movie"]["total_view_count"]},
			_("カテゴリ：%(category)s") %{"category": self.connection.movieInfo["movie"]["category"]},
			_("コメント数：%(number)d") %{"number": self.connection.movieInfo["movie"]["comment_count"]},
			self.connection.movieInfo["broadcaster"]["screen_id"]
		]
		if self.connection.movieInfo["movie"]["is_live"] == True:
			result.insert(0, _("現在配信中"))
		else:
			result.insert(0, _("オフライン（最終放送時の情報を表示中）"))
		if self.connection.movieInfo["movie"]["is_collabo"] == True:
			result.insert(-1, _("コラボ可能"))
		else:
			result.insert(-1, _("コラボ不可"))
		if mode == 0:
			for i in range(0, len(result)):
				self.MainView.liveInfo.InsertItem(i, result[i])
		elif mode == 1:
			for i in range(0, len(result)):
				bool = result[i] == self.MainView.liveInfo.GetItemText(i)
				if bool == False:
					self.MainView.liveInfo.SetItemText(i, result[i])

	def postComment(self, commentBody):
		result = self.connection.postComment(commentBody)
		if "error" in result and "comment" in result["error"]["details"] and "length" in result["error"]["details"]["comment"]:
			simpleDialog.dialog(_("エラー"), _("コメント文字数が１４０字を超えているため、コメントを投稿できません。"))
			return False
		elif "error" in result:
			dialog(_("エラー"), _("エラーが発生しました。詳細：%(detail)s") %{"detail": str(result["error"])})
			return False
		else:
			return True

	def formatTime(self, second):
		time = datetime.time(hour = int(second / 3600), minute = int(second % 3600 / 60), second = int(second % 3600 % 60))
		return time

	def timer(self, event):
		if self.connection.isLive == False or "error" in self.connection.movieInfo:
			self.connection.update()
		timer = event.GetTimer()
		id = timer.GetId()
		if id == evtComment:
			newComments = self.connection.getComment()
			self.addComments(newComments, update)
		elif id == evtLiveInfo:
			self.connection.getLiveInfo()
			self.newViewers = self.connection.movieInfo["movie"]["current_view_count"]
			if self.newViewers < self.oldViewers:
				globalVars.app.say(_("閲覧%(viewers)d人。") %{"viewers": self.newViewers})
			elif self.newViewers > self.oldViewers:
				globalVars.app.say(_("閲覧%(viewers)d人。") %{"viewers": self.newViewers})
			self.oldViewers = self.newViewers
			self.newIsLive = self.connection.movieInfo["movie"]["is_live"]
			if self.oldIsLive == True and self.newIsLive == False:
				globalVars.app.say(_("ライブ終了。"))
				self.countDownTimer.Stop()
				self.connection.elapsedTime = 0
				self.connection.remainingTime = 0
			elif self.oldIsLive == False and self.newIsLive == True:
				globalVars.app.say(_("ライブ開始。"))
				self.connection.totalTime = 1800
				self.connection.elapsedTime = self.connection.movieInfo["movie"]["duration"]
				self.connection.remainingTime = self.connection.totalTime - self.connection.elapsedTime
				self.countDownTimer.Start(countDownTimerInterval)
			self.oldIsLive = self.newIsLive
			self.createLiveInfoList(update)
		elif id == evtCountDown:
			self.connection.elapsedTime += 1
			self.connection.remainingTime -= 1
			if self.connection.remainingTime == 900:
				globalVars.app.say(_("残り１５分。"))
			if self.connection.remainingTime == 300:
				globalVars.app.say(_("残り５分。"))
			if self.connection.remainingTime == 180:
				globalVars.app.say(_("残り３分。"))
			if self.connection.remainingTime == 60:
				globalVars.app.say(_("残り１分"))
			if self.connection.remainingTime == 30:
				globalVars.app.say(_("残り３０秒。"))
			if self.connection.remainingTime == 10:
				globalVars.app.say(_("残り１０秒。"))
			if self.connection.remainingTime == 0:
				globalVars.app.say(_("３０分経過。"))
				self.connection.remainingTime += 1800
			self.MainView.liveInfo.SetItemText(1, _("経過時間：%(elapsedTime)s、残り時間：%(remainingTime)s") %{"elapsedTime": self.formatTime(self.connection.elapsedTime).strftime("%H:%M:%S"), "remainingTime": self.formatTime(self.connection.remainingTime).strftime("%H:%M:%S")})
