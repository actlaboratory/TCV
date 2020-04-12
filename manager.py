# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime
import wx
import globalVars

evtComment = 0
evtLiveInfo = 1

first = 0
update = 1

class manager:
	def __init__(self, MainView):
		self.MainView = MainView
		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.timer)

	def connect(self, userId):
		self.connection = twitcasting.connection.connection(userId)
		self.initialComments = self.connection.getInitialComment(50)
		self.addComments(self.initialComments, first)
		self.commentTimer = wx.Timer(self.evtHandler, evtComment)
		self.commentTimer.Start(5000)
		self.liveInfo = self.connection.getLiveInfo()
		self.createLiveInfoList(self.liveInfo, first)
		self.liveInfoTimer = wx.Timer(self.evtHandler, evtLiveInfo)
		self.liveInfoTimer.Start(10000)

	def addComments(self, commentList, mode):
		for i in commentList:
			result = [
				i["from_user"]["name"],
				i["message"],
				datetime.datetime.fromtimestamp(i["created"]).strftime("%H:%M:%S"),
				i["from_user"]["screen_id"]
			]
			self.MainView.commentList.InsertItem(0	, "")
			for j in range(0, 4):
				self.MainView.commentList.SetItem(0, j, result[j])
				if mode == update:
					globalVars.app.say(str(result[j]))

	def createLiveInfoList(self, info, mode):
		result = [
			_("タイトル：%(title)s") %{"title": info["movie"]["title"]},
			_("閲覧：現在%(current)d人、合計%(total)d人") %{"current": info["movie"]["current_view_count"], "total": info["movie"]["total_view_count"]},
			_("カテゴリ：%(category)s") %{"category": info["movie"]["category"]},
			_("コメント数：%(number)d") %{"number": info["movie"]["comment_count"]},
			info["broadcaster"]["screen_id"]
		]
		if info["movie"]["is_live"] == True:
			result.insert(0, _("現在配信中"))
		else:
			result.insert(0, _("オフライン（最終放送時の情報を表示中）"))
		if info["movie"]["is_collabo"] == True:
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
		return result

	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == evtComment:
			newComments = self.connection.getComment()
			self.addComments(newComments, update)
		elif id == evtLiveInfo:
			newInfo = self.connection.getLiveInfo()
			self.createLiveInfoList(newInfo, update)
