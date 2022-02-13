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
		return []
	log.debug("response: %s" % req)
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
			result.append({"name": name, "count": count, "id": id, "user": getItemPostedUser(screenId, id)})
	return result

def getItemPostedUser(screenId, itemId):
	if itemId == "MP":
		return
	if globalVars.app.config["general"]["language"] == "ja-JP":
		lang = "ja"
	else:
		lang = "en"
	try:
		req = requests.get("http://twitcasting.tv/%s/gifts" % (screenId)).text
	except:
		log.error("Connection failed(getItemPostedUser).")
		log.error(traceback.format_exc)
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return []
	soup = BeautifulSoup(req, "lxml")
	tmp = soup.find("section", {"class": "tw-supporter-gift-history"})
	if tmp is None:
		return []
	result = []
	for i in tmp.find_all("div", {"class": "tw-supporter-gift"}):
		try:
			item = i.find("div", {"class": "tw-supporter-item"}).a["href"]
			if re.match("javascript:((giftItem)|(showItemDialog)).*", item):
				if "," not in item or "'" not in item:
					continue
				start = item.index(",") + 3
				end = item.index("'", start)
				item = item[start:end]
		except Exception as e:
			log.error("Failed to get item Id on getItemPostedUser.")
			log.error(traceback.format_exc())
			continue
		if item == itemId:
			try:
				user = i.find("a", {"class": "tw-user-name-icon"})["data-user-id"]
				result.append(user)
			except Exception as e:
				log.error("Failed to get user Id on getItemPostedUser.")
				log.error(traceback.format_exc())
				continue
	return result
