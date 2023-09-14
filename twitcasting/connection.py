# -*- coding: utf-8 -*-
# コネクション

from pprint import pformat
from twitcasting.twitcasting import *
from twitcasting.getItem import *
from twitcasting.getMovieType import *
from twitcasting.getTypingUser import *
import views.main
import datetime
import globalVars
import threading
import time

class connection(threading.Thread):
	def __init__(self, userId):
		super().__init__(daemon=True)
		self.userId = userId
		self.update(0)
		self.comments = []
		self.errorFlag = 0
		self.typingUser = ""
		self.is_games = False
		self.is_vtuber = False
		self.is_corporate_broadcasting = False

	def getInitialComment(self, number):
		if self.hasMovieId == False:
			return []
		limit = min(50, number)
		result = GetComments(self.movieId, limit=limit)
		try:
			result = result["comments"]
		except KeyError:
			if "error" in result:
				self.errorFlag = result["error"]["code"]
			result = []
		if len(result) == 0:
			self.lastCommentId = ""
			return []
		self.lastCommentId = result[0]["id"]
		if number > len(result):
			while True:
				offset = len(result)
				limit = min(50, number - len(result))
				if limit == 0:
					break
				result2 = GetComments(self.movieId, offset, limit)
				try:
					result2 = result2["comments"]
				except KeyError:
					if "error" in result2:
						self.errorFlag = result2["error"]["code"]
					result2 = []
				rm = []
				for i in range(len(result2)):
					if result2[i] in result:
						rm.append(i)
				rm.reverse()
				for i in rm:
					del result2[i]
				result = result + result2
				if len(result2) == 0 or len(result) == number:
					break
		for i in result:
			i["movieId"] = self.movieId
			i["urls"] = list(re.finditer("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", i["message"]))
		self.comments = result + self.comments
		result.reverse()
		return result

	def getComment(self):
		if self.hasMovieId == False:
			return
		ret = []
		if hasattr(self, "lastCommentId"):
			result = GetComments(self.movieId, slice_id=self.lastCommentId)
		else:
			result = GetComments(self.movieId)
		try:
			result = result["comments"]
		except KeyError:
			if "error" in result and result["error"]["code"] != 404:
				self.errorFlag = result["error"]["code"]
			result = []
		if len(result) == 0:
			return 
		self.lastCommentId = result[0]["id"]
		ret = result
		for i in ret:
			i["movieId"] = self.movieId
			i["urls"] = list(re.finditer("https?://[\w/:%#\$&\?\(\)~\.=\+\-]+", i["message"]))
		self.comments = ret + self.comments

	def postComment(self, body, idx):
		commentToSns = globalVars.app.config.getint("general", "commentToSns", 0)
		if commentToSns == 0:
			sns = "none"
		elif commentToSns == 1:
			sns = "reply"
		elif commentToSns == 2:
			sns = "normal"
		result = PostComment(self.movieId, body, sns, globalVars.app.accountManager.getToken(idx))
		return result

	def deleteComment(self, comment):
		result = DeleteComment(comment["movieId"], comment["id"])
		if "error" in result:
			return False
		else:
			return True

	def getTypingUser(self):
		self.typingUser = getTypingUser(self.userId, self.userId)

	def update(self, mode=1):
		userInfo = GetUserInfo(self.userId)
		if "error" in userInfo:
			self.connected = False
			if userInfo["error"]["code"] != 404:
				self.errorFlag = userInfo["error"]["code"]
			return
		else:
			self.connected = True
		self.movieId = userInfo["user"]["last_movie_id"]
		if self.movieId == None:
			self.hasMovieId = False
			self.createDummyMovieInfo(userInfo)
		else:
			self.hasMovieId = True
		if userInfo["user"]["is_live"] == True:
			self.isLive = True
		elif userInfo["user"]["is_live"] == False:
			self.isLive = False
		if self.hasMovieId == True:
			self.movieInfo = GetMovieInfo(self.movieId)
			self.movieInfo["duration_updated_at"] = time.time()
			if "error" in self.movieInfo:
				if self.movieInfo["error"]["code"] == 404:
					self.hasMovieId = False
					self.isLive = False
				else:
					self.errorFlag = self.movieInfo["error"]["code"]
			if self.hasMovieId == True:
				self.category = self.movieInfo["movie"]["category"]
				self.categoryName = self.getCategoryName(self.category)
				self.viewers = self.movieInfo["movie"]["current_view_count"]
				self.subtitle = self.movieInfo["movie"]["subtitle"]
		if self.hasMovieId == False:
			self.category = None
			self.categoryName = self.getCategoryName(self.category)
			self.viewers = 0
			self.subtitle = None
			self.createDummyMovieInfo(userInfo)
		item = getItem(self.userId)
		if type(item) == list:
			self.item = item
			self.coins = 0
			for i in self.item:
				if i["name"] == "コンティニューコイン":
					self.coins = i["count"]
		else:
			if not hasattr(self, "item"):
				self.item = []
				self.coins = 0
		if mode == 1:
			self.getComment()
			self.getTypingUser()

	def updateMovieType(self):
		if self.movieId is None:
			return
		data = getMovieType(self.userId)
		self.is_games = data["is_games"]
		self.is_vtuber = data["is_vtuber"]
		self.is_corporate_broadcasting = data["is_corporate_broadcasting"]

	def getCategoryName(self, id):
		if id == None:
			return _("カテゴリなし")
		if globalVars.app.config["general"]["language"] == "ja-JP":
			lang = "ja"
		else:
			lang = "en"
		categories = GetCategories(lang)
		try:
			categories = categories["categories"]
		except KeyError:
			if "error" in categories:
				self.errorFlag = categories["error"]["code"]
			categories = []
		for category in categories:
			for subCategory in category["sub_categories"]:
				if subCategory["id"] == id:
					return subCategory["name"]

	def createDummyMovieInfo(self, userInfo):
		self.movieInfo = {}
		self.movieInfo["movie"] = {
			"id": "",
			"user_id": self.userId,
			"title": "",
			"subtitle": None,
			"category": None,
			"is_live": False,
			"is_collabo": False,
			"comment_count": 0,
			"duration": 0,
			"max_view_count": 0,
			"current_view_count": 0,
			"total_view_count": 0,
			"hls_url": None,
			"user_id": self.userId,
		}
		self.movieInfo["duration_updated_at"] = time.time()
		self.movieInfo["broadcaster"] = userInfo["user"]

	def run(self):
		self.running = True
		while self.running:
			time.sleep(5)
			self.update()

	def getUserObject(self, user):
		result = GetUserInfo(user)
		try:
			return result["user"]
		except KeyError:
			if "error" in result:
				if result["error"]["code"] != 404:
					self.errorFlag = result["error"]["code"]
			return {}
