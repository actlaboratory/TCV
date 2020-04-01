# -*- coding: utf-8 -*-
# ツイキャスライブ接続･切断モジュール

from twitcasting.twitcasting import *
import globalVars
from simpleDialog import dialog
import views.main

connected = False

def connect(user_id):
	info = GetUserInfo(user_id)
	if "error" in info:
		dialog(_("エラー"), _("ライブへの接続に失敗しました。"))
	elif info["user"]["is_live"] == True:
		globalVars.app.say(_("接続しました。現在配信中です。"))
		connected = True
		movie = GetCurrentLive(user_id)["movie"]["id"]
		getCommentList(movie)
		getLiveInfo(movie)
	elif info["user"]["is_live"] == False:
		globalVars.app.say(_("接続しました。現在オフラインです。"))
		connected = True
		movie = info["user"]["last_movie_id"]
		getCommentList(movie)
		getLiveInfo(movie)

def disconnect():
	connected = False
	globalVars.app.say(_("切断しました。"))

def getCommentList(movie):
	commentList = []
	src = GetComments(movie)
	comments = src["comments"]
	for i in comments:
		commentData = {
			"commentID": i["id"],
			"dispname": i["from_user"]["name"],
			"message": i["message"],
			"user": i["from_user"]["screen_id"]
		}
		commentList.append(commentData)
	dialog("コメント", str(commentList))
	return commentList

def getLiveInfo(movie):
	src = GetMovieInfo(movie)
	info = {
		"movieID": src["movie"]["id"],
		"title": src["movie"]["title"],
		"category": src["movie"]["category"],
		"commentCount": src["movie"]["comment_count"],
		"currentViewCount": src["movie"]["current_view_count"],
		"totalViewCount": src["movie"]["total_view_count"],
		"hlsURL": src["movie"]["hls_url"]
	}
	dialog("ライブ情報", str(info))
	return info

