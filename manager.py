# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime
import wx

evtComment = 0

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
		self.commentTimer.Start(10000)


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


	def timer(self, event):
		timer = event.GetTimer()
		id = timer.GetId()
		if id == evtComment:
			newComments = self.connection.getComment()
			self.addComments(newComments)
