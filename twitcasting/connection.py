# -*- coding: utf-8 -*-
# コネクション

from twitcasting.twitcasting import *
from twitcasting.getItem import getItem
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
			self.update()
			if "error" in self.movieInfo and self.movieInfo["error"]["code"] == 404:
				return
			else:
				self.category = self.movieInfo["movie"]["category"]
				self.categoryName = getCategoryName(self.category)
				if "コンティニューコイン" in self.item:
					self.coins = int(self.item["コンティニューコイン"])
				else:
					self.coins = 0
				self.elapsedTime = self.movieInfo["movie"]["duration"]
				self.totalTime = int(self.coins / 5) * 1800 + 1800
				self.remainingTime = self.totalTime - self.elapsedTime
				if self.elapsedTime + self.remainingTime > 14400:
					self.remainingTime = 14400 - self.elapsedTime
				while self.remainingTime < 0:
					self.remainingTime += 1800
				self.comments = []

	def getInitialComment(self, number):
		if self.movieId == "":
			return []
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
			for i in result3:
				i["movieId"] = self.movieId
			self.comments = result3 + self.comments
			result3.reverse()
			return result3

	def getComment(self):
		if self.movieId == "":
			return []
		ret = []
		result = GetComments(self.movieId, 0, 50, self.lastCommentId)
		if len(result) == 0 or "error" in result:
			return []
		else:
			while result != []:
				self.lastCommentId = result[0]["id"]
				ret = result + ret
				result = GetComments(self.movieId, 0, 50, self.lastCommentId)
			for i in ret:
				i["movieId"] = self.movieId
			self.comments = ret + self.comments
			ret.reverse()
			return ret

	def postComment(self, body):
		result = PostComment(self.movieId, body, "none")
		return result

	def deleteComment(self, comment):
		result = DeleteComment(comment["movieId"], comment["id"])
		if "error" in result and result["error"]["code"] == 403:
			return False
		else:
			return True

	def update(self):
		userInfo = GetUserInfo(self.userId)
		if userInfo["user"]["is_live"] == True:
			self.isLive = True
			self.movieInfo = GetCurrentLive(self.userId)
		elif userInfo["user"]["is_live"] == False:
			self.isLive = False
			self.movieInfo = GetMovieInfo(userInfo["user"]["last_movie_id"])
			if "error" in self.movieInfo and self.movieInfo["error"]["code"] == 404:
				self.movieId = ""
				return
		self.movieId = self.movieInfo["movie"]["id"]
		self.category = self.movieInfo["movie"]["category"]
		self.categoryName = getCategoryName(self.category)
		self.item = getItem(self.movieInfo["broadcaster"]["screen_id"])
		if "コンティニューコイン" in self.item:
			self.coins = int(self.item["コンティニューコイン"])
		else:
			self.coins = 0


def getCategoryName(id):
	if id == None:
		return _("カテゴリなし")
	categories = GetCategories()
	for category in categories:
		for subCategory in category["sub_categories"]:
			if subCategory["id"] == id:
				return subCategory["name"]
