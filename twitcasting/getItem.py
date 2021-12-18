# -*- coding: utf-8 -*-
# アイテム情報取得モジュール

import requests
from bs4 import BeautifulSoup
import simpleDialog
import re
import globalVars
import constants
from logging import getLogger
import traceback
import sys

log = getLogger("%s.%s" %(constants.LOG_PREFIX, "twitcasting.getItem"))

def getItem(screenId):
	if globalVars.app.config["general"]["language"] == "ja-JP":
		lang = "ja"
	else:
		lang = "en"
	try:
		req = requests.get("https://frontendapi.twitcasting.tv/item_box/%s" % (screenId), {"hl": lang}).json()
	except:
		log.error("Connection failed(getItem).")
		log.error(traceback.format_exc)
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return []
	itemName = []
	itemCount = []
	itemId = []
	result = []
	for i in req["items"]:
		itemName.append(i["name"])
		itemCount.append(i["count"])
		itemId.append(i["item_id"])
	itemName.append("MP")
	itemCount.append(req["status"]["mp"])
	itemId.append("MP")
	for name, count, id in zip(itemName, itemCount, itemId):
		if count > 0 or name == "MP":
			result.append({"name": name, "count": count, "id": id})
	return result

def getItemPostedUser(screenId, itemId):
	if itemId == "MP":
		return
	if globalVars.app.config["general"]["language"] == "ja-JP":
		lang = "ja"
	else:
		lang = "en"
	try:
		req = requests.get("http://twitcasting.tv/gearajax.php?c=showitem&itemid=" + itemId + "&u=" + screenId + "&hl=" + lang).text
	except:
		log.error("Connection failed(getItemPostedUser).")
		log.error(traceback.format_exc)
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return []
	soup = BeautifulSoup(req, "lxml")
	tmp = soup.find_all("span", class_ = "tw-user-name-screen-name")
	result = []
	for i in tmp:
		result.append(i.text[1:])
	return result
