# -*- coding: utf-8 -*-
# コネクション

from twitcasting.twitcasting import *
import views.main
import datetime

class connection:
	def __init__(self, userId):
		self.userId = userId
		userInfo = GetUserInfo(self.userId)
		if "error" in userInfo and userInfo["error"]["code"] == 404:
			self.connected = False
		else:
			self.connected = True
			self.isLive = userInfo["user"]["is_live"]
			self.movieId = userInfo["user"]["last_movie_id"]
			self.movieInfo = GetMovieInfo(self.movieId)
			self.elapsedTime = self.movieInfo["movie"]["duration"]
			self.totalTime = 1800
			self.remainingTime = self.totalTime - self.elapsedTime
			while self.remainingTime < 0:
				self.remainingTime += 1800

	def getInitialComment(self, number):
		offset = max(0, number-50)
		limit = min(50, number)
		result = GetComments(self.movieId, offset, limit)
		if len(result) == 0:
			self.lastCommentId = ""
			return []
		else:
			self.lastCommentId = result[0]["id"]
			result2 = self.getComment()
			result3 = result2 + result
			result3.reverse()
			return result3

	def getComment(self):
		ret = []
		result = GetComments(self.movieId, 0, 50, self.lastCommentId)
		if len(result) == 0:
			return []
		else:
			while result != []:
				self.lastCommentId = result[0]["id"]
				ret = result + ret
				result = GetComments(self.movieId, 0, 50, self.lastCommentId)
			ret.reverse()
			return ret

	def getLiveInfo(self):
		self.movieInfo = GetMovieInfo(self.movieId)

	def postComment(self, body):
		result = PostComment(self.movieId, body, "none")
		return result

	def update(self):
		userInfo = GetUserInfo(self.userId)
		if userInfo["user"]["is_live"] == True:
			self.movieInfo = GetCurrentLive(self.userId)
		elif userInfo["user"]["is_live"] == False:
			self.movieInfo = GetMovieInfo(userInfo["user"]["last_movie_id"])
		self.isLive = self.movieInfo["movie"]["is_live"]
		self.movieId = self.movieInfo["movie"]["id"]
