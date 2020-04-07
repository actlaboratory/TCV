# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime
import wx

evtComment = 0
evtLiveInfo = 1

liveInfoFirst = 0
liveInfoUpdate = 1

class manager:
	def __init__(self, MainView):
		self.MainView = MainView
		self.evtHandler = wx.EvtHandler()
		self.evtHandler.Bind(wx.EVT_TIMER, self.timer)

	def connect(self, userId):
		self.connection = twitcasting.connection.connection(userId)
		self.initialComments = self.connection.getInitialComment(50)
		self.addComments(self.initialComments)
		self.commentTimer = wx.Timer(self.evtHandler, evtComment)
		self.commentTimer.Start(2000)
		self.liveInfo = self.connection.getLiveInfo()
		self.createLiveInfoList(self.liveInfo, liveInfoFirst)
		self.liveInfoTimer = wx.Timer(self.evtHandler, evtLiveInfo)
		self.liveInfoTimer.Start(10000)

	def addComments(self, commentList):
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

	def createLiveInfoList(self, info, mode):
		result = [
			_("タイトル：%(title)s") %{"title": info["movie"]["title"]},
			_("閲覧：現在%(current)d人、合計%(total)d人") %{"current": info["movie"]["current_view_count"], "total": info["movie"]["total_view_count"]},
			_("カテゴリ：%(category)s") %{"category": info["movie"]["category"]},
			_("コメント数：%(number)d") %{"number": info["movie"]["comment_count"]}
		]
		if info["movie"]["is_live"] == True:
			result.insert(0, _("現在配信中"))
		else:
			result.insert(0, _("オフライン"))
		if info["movie"]["is_collabo"] == True:
			result.append(_("コラボ可能"))
		else:
			result.append(_("コラボ不可"))

		if mode == 0:
			for i in range(0, len(result)):
				self.MainView.liveInfo.InsertItem(i, result[i])
		elif mode == 1:
			for i in range(0, len(result)):
				bool = result[i] == self.MainView.liveInfo.GetItemText(i)
				if bool == False:
					self.MainView.liveInfo.SetItemText(i, result[i])

	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == evtComment:
			newComments = self.connection.getComment()
			self.addComments(newComments)
		elif id == evtLiveInfo:
			newInfo = self.connection.getLiveInfo()
			self.createLiveInfoList(newInfo, liveInfoUpdate)
