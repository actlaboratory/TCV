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
		req = requests.get("http://twitcasting.tv/gearajax.php?c=showitems&u=" + screenId + "&hl=" + lang).text
	except:
		log.error("Connection failed(getItem).")
		log.error(traceback.format_exc)
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return []
	soup = BeautifulSoup(req, "lxml")
	itemName = []
	itemCount = []
	itemId = []
	result = []
	tmp = soup.find_all("img", class_ = "item")
	for i in tmp:
		itemName.append(i.get("title"))
	tmp = soup.find_all("span", class_ = "tw-item-count-badge")
	for i in tmp:
		itemCount.append(int(i.text))
	tmp = soup.find_all("a")
	for i in tmp:
		href = i.get("href")
		if re.match("javascript:((giftItem)|(showItemDialog)).*", href):
			if "," not in href or "'" not in href:
				continue
			start = href.index(",") + 3
			end = href.index("'", start)
			itemId.append(href[start: end])
	mp = soup.find("span", class_ = "tw-item-mp")
	if mp == None:
		mp = ["0", "MP"]
	else:
		mp = mp.text.split()
	itemName.append(mp[1])
	itemCount.append(int(mp[0]))
	itemId.append(mp[1])
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
