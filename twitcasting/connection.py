# -*- coding: utf-8 -*-
# ツイキャスライブ接続･切断等モジュール

from twitcasting.twitcasting import *
import globalVars
from simpleDialog import dialog
import views.main
import datetime

class connection:
	def __init__(self, userId):
		self.userId = userId
		userInfo = GetUserInfo(self.userId)
		self.movieId = userInfo["user"]["last_movie_id"]

	def getInitialComment(self, number):
		offset = max(0, number-50)
		limit = min(50, number)
		result = GetComments(self.movieId, offset, limit)
		self.lastCommentId = result[0]["id"]
		result2 = self.getComment()
		result3 = result2 + result
		result3.reverse()
		return result3

	def getComment(self):
		ret = []
		result = GetComments(self.movieId, 0, 50, self.lastCommentId)
		while result != []:
			self.lastCommentId = result[0]["id"]
			ret = result + ret
			result = GetComments(self.movieId, 0, 50, self.lastCommentId)
		ret.reverse()
		return ret


	"""
	def connect(user_id):
		info = GetUserInfo(user_id)
		if "error" in info:
			dialog(_("エラー"), _("ライブへの接続に失敗しました。"))
		elif info["user"]["is_live"] == True:
			globalVars.app.say(_("接続しました。現在配信中です。"))
			connected = True
			movieId = GetCurrentLive(user_id)["movie"]["id"]
			getCommentList(movieId)
			getLiveInfo(movieId)
		elif info["user"]["is_live"] == False:
			globalVars.app.say(_("接続しました。現在オフラインです。"))
			connected = True
			movieId = info["user"]["last_movie_id"]
			getCommentList(movieId)
			getLiveInfo(movieId)

	def disconnect():
		connected = False
		globalVars.app.say(_("切断しました。"))

	def getCommentList(movieId):
		commentList = []
		src = GetComments(movieId)
		comments = src["comments"]
		for i in comments:
			commentData = {
				"commentID": i["id"],
				"dispname": i["from_user"]["name"],
				"message": i["message"],
				"time": datetime.datetime.fromtimestamp(i["created"]),
				"user": i["from_user"]["screen_id"]
			}
			commentList.append(commentData)
		# テスト用
		dialog("コメント", str(commentList))
		return commentList

	def getLiveInfo(movieId):
		src = GetMovieInfo(movieId)
		info = {
			"movieID": src["movie"]["id"],
			"title": src["movie"]["title"],
			"category": src["movie"]["category"],
			"commentCount": src["movie"]["comment_count"],
			"currentViewCount": src["movie"]["current_view_count"],
			"totalViewCount": src["movie"]["total_view_count"],
			"hlsURL": src["movie"]["hls_url"]
		}
		# テスト用
		dialog("ライブ情報", str(info))
		return info
	"""
