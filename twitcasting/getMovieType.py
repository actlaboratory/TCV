# -*- coding: utf-8 -*-
# タイピングメッセージの取得

import requests
import datetime
import constants
from logging import getLogger
import traceback
import sys

log = getLogger("%s.%s" %(constants.LOG_PREFIX, "twitcasting.getFrontendApiToken"))

def getMovieType(movie_id):
	result = {}
	result["is_games"] = False
	result["is_vtuber"] = False
	result["is_corporate_broadcasting"] = False

	session = requests.Session()
	session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"})

	# STEP1: Refeler対策のため、トップページへダミーアクセス
	try:
		ret = session.get("https://twitcasting.tv/", timeout=5)
		if ret.status_code!=200:
			log.error("top age connection error")
			return result
	except:
		log.error("top age connection error")
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return result

	# STEP2: トークン入手
	token = getFrontendApiToken(session, movie_id)
	if not token:
		log.error("token error")
		return result

	# STEP3: 情報入手
	try:
		"""
		レスポンス例：
		{
			"id":movie_id,
			"started_at":1666794976,
			"visibility":{"type":"public"},
			"collabo":null,			# null以外を再現できず
			"is_tool":true,			# ツール配信
			"is_games":null, 		# https://twitcasting.tv/helpcenter.php?pid=HELP_TWITCAST_GAMES
			"is_vtuber":null,		# https://twitcasting.tv/promo/vtuber
			"is_corporate_broadcasting":null,	# https://twitcasting.tv/promo/business
			"is_portrait":null,
			"is_dvr_supported":null
		}
		"""

		ret = session.get(
			"https://frontendapi.twitcasting.tv/movies/%d/info?token=%s&__n=%d" % (int(movie_id), token, int(datetime.datetime.now().timestamp()*1000)),
			timeout = 5
		).json()
		result = {}
		result["is_games"] = "is_games" in ret and ret["is_games"] == True
		result["is_vtuber"] = "is_vtuber" in ret and ret["is_vtuber"] == True
		result["is_corporate_broadcasting"] = "is_corporate_broadcasting" in ret and ret["is_corporate_broadcasting"] == True
		log.info("live type detected" + str(result))
		return result
	except:
		log.error("Failed. data: %s" % ret.text)
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return result

def getFrontendApiToken(session, movie_id):
	log.debug("getting frontend api token")
	try:
		ret = requests.post(
				"https://twitcasting.tv/happytoken.php?__n=" + str(int(datetime.datetime.now().timestamp()*1000)),
				files = {(None, None)},		# Content-Type: multipart/form-data;にするために必要
				data = {"movie_id":movie_id},
				timeout = 5
			)
	except:
		log.error("Connection failed.")
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return
	try:
		return ret.json()["token"]
	except:
		log.error("Failed. data: %s" % ret.text)
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return
