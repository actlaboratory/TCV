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
		return None
	elif info["user"]["is_live"] == True:
		globalVars.app.say(_("接続しました。現在配信中です。"))
		connected = True
		movie = GetCurrentLive(user_id)["movie"]["id"]
		getCommentList(movie)
	elif info["user"]["is_live"] == False:
		globalVars.app.say(_("接続しました。現在オフラインです。"))
		connected = True
		movie = info["user"]["last_movie_id"]
		getCommentList(movie)

def disconnect():
	connected = False
	globalVars.app.say(_("切断しました。"))

def getCommentList(movie):
	commentList = []
	src = GetComments(movie)
	comments = src["comments"]
	for i in comments:
		dispname = i["from_user"]["name"]
		message = i["message"]
		user = i["from_user"]["screen_id"]
		commentList.append(dispname + "," + message + "," + user)
	dialog("デバッグ用", str(commentList))
	return commentList