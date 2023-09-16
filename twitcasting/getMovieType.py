# -*- coding: utf-8 -*-
# ライブ種別の取得
#Copyright (C) 2023 yamahubuki <itiro.ishino@gmail.com>

import bs4
import hashlib
import requests
import sys
import traceback

import constants

from logging import getLogger

log = getLogger("%s.%s" %(constants.LOG_PREFIX, "twitcasting.getMovieType"))

def getMovieType(user_id):
	result = {}
	result["is_games"] = False
	result["is_vtuber"] = False
	result["is_corporate_broadcasting"] = False

	session = requests.Session()
	session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"})

	# ライブページを取得
	try:
		ret = session.get("https://twitcasting.tv/"+ user_id, timeout=5)
		if ret.status_code!=200:
			log.error("live age connection error. bad status:" + ret.status_code)
			return result
	except:
		log.error("live age connection error")
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return result


	# 情報入手
	try:
		soup = bs4.BeautifulSoup(ret.text, "lxml")
		svg = soup.find("svg", attrs={"viewbox": "0 0 128 32"})
		if svg is None:
			log.info("svg not found. may be normal live.")
			return result
		path = svg.find("path")
		if path is None:
			log.error("path not found")
			return result
		d = path.get("d", None)
		if d is None:
			log.error("d not found")
			return result

		hash = hashlib.sha256(d.encode()).hexdigest()
		if hash == "18227d46e080763652c9a959849323be895f6648655888c21ab7ebea3092fc12":
			result["is_games"] = True
		elif hash == "62829c96bd6c1c6d40b3cf0ceb0da243c60be3b1e2a059375407b0e64cdece30":
			result["is_vtuber"] = True
		else:
			log.warning("unknown d detected!:"+d)
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


