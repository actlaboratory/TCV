# -*- coding: utf-8 -*-
# manager

import twitcasting.connection
import datetime

class manager:
	def __init__(self, MainView):
		self.MainView = MainView

	def connect(self, userId):
		self.connection = twitcasting.connection.connection(userId)
		self.initialComments = self.connection.getInitialComment(50)
		self.addComments(self.initialComments)

	def addComments(self, commentList):
		for i in commentList:
			result = [
				i["from_user"]["name"],
				i["message"],
				datetime.datetime.fromtimestamp(i["created"]).strftime("%H:%M:%S"),
				i["from_user"]["screen_id"]
			]
			self.MainView.commentList.Append(result)
