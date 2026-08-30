# -*- coding: utf-8 -*-
# アイテム情報取得モジュール

import requests
import globalVars
import constants
from logging import getLogger
import traceback
import sys

log = getLogger("%s.%s" % (constants.LOG_PREFIX, "twitcasting.getItem"))


def getItem(screenId):
	log.debug("Getting items...")
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
		return None
	log.debug("response: %s" % req)
	if "error" in req:
		log.error("Failed to get item. %s" % req)
		return None
	itemName = []
	itemCount = []
	itemId = []
	result = []
	try:
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
	except Exception as e:
		log.error(traceback.format_exc())
		return None

