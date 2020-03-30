# -*- coding: utf-8 -*-
# ツイキャスライブ接続･切断モジュール

from twitcasting.twitcasting import *
import globalVars

connected = False

def connect(user_id):
	info = GetUserInfo(user_id)
	if "error" in info:
		globalVars.app.say(_("ライブへの接続に失敗しました。"))
	elif info["user"]["is_live"] == True:
		globalVars.app.say(_("接続しました。現在配信中です。"))
		connected = True
	elif info["user"]["is_live"] == False:
		globalVars.app.say(_("接続しました。現在オフラインです。"))
		connected = True

def disconnect():
	connected = False
	globalVars.app.say(_("切断しました。"))
