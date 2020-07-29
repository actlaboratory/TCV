# -*- coding: utf-8 -*-
# コネクション

from twitcasting.twitcasting import *
from twitcasting.getItem import *
from twitcasting.getTypingUser import *
import views.main
import datetime
import globalVars

class connection:
	def __init__(self, userId):
		self.userId = userId
		self.update()
		self.comments = []

	def getInitialComment(self, number):
		if self.hasMovieId == False:
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
				i["urls"] = list(re.finditer("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", i["message"]))
			self.comments = result3 + self.comments
			result3.reverse()
			return result3

	def getComment(self):
		if self.hasMovieId == False:
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
				i["urls"] = list(re.finditer("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", i["message"]))
			self.comments = ret + self.comments
			ret.reverse()
			return ret

	def postComment(self, body):
		commentToSns = globalVars.app.config.getint("general", "commentToSns", 0)
		if commentToSns == 0:
			sns = "none"
		elif commentToSns == 1:
			sns = "reply"
		elif commentToSns == 2:
			sns = "normal"
		result = PostComment(self.movieId, body, sns)
		return result

	def deleteComment(self, comment):
		result = DeleteComment(comment["movieId"], comment["id"])
		if "error" in result and result["error"]["code"] == 403:
			return False
		else:
			return True

	def getItemPostedUser(self, itemId, count):
		users = getItemPostedUser(self.userId, itemId)
		return users[0:count]

	def getTypingUser(self):
		result = getTypingUser(self.userId, self.userId)
		return result

	def update(self):
		userInfo = GetUserInfo(self.userId)
		if "error" in userInfo and userInfo["error"]["code"] == 404:
			self.connected = False
			return
		else:
			self.connected = True
		self.movieId = userInfo["user"]["last_movie_id"]
		if self.movieId == None:
			self.hasMovieId = False
		else:
			self.hasMovieId = True
		if userInfo["user"]["is_live"] == True:
			self.isLive = True
		elif userInfo["user"]["is_live"] == False:
			self.isLive = False
		if self.hasMovieId == True:
			self.movieInfo = GetMovieInfo(self.movieId)
			if "error" in self.movieInfo and self.movieInfo["error"]["code"] == 404:
				self.hasMovieId = False
			if self.hasMovieId == True:
				self.category = self.movieInfo["movie"]["category"]
				self.categoryName = getCategoryName(self.category)
				self.viewers = self.movieInfo["movie"]["current_view_count"]
				self.subtitle = self.movieInfo["movie"]["subtitle"]
		if self.hasMovieId == False:
			self.category = None
			self.categoryName = getCategoryName(self.category)
			self.viewers = 0
			self.subtitle = None
		self.item = getItem(self.userId)
		self.coins = 0
		for i in self.item:
			if i["name"] == "コンティニューコイン":
				self.coins = i["count"]


def getCategoryName(id):
	if id == None:
		return _("カテゴリなし")
	categories = GetCategories()
	for category in categories:
		for subCategory in category["sub_categories"]:
			if subCategory["id"] == id:
				return subCategory["name"]
