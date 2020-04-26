# -*- coding: utf-8 -*-
# アイテム情報取得モジュール

import requests
from bs4 import BeautifulSoup
import simpleDialog
import re

def getItem(screenId):
	req = requests.get("http://twitcasting.tv/gearajax.php?c=showitems&u=" + screenId + "&hl=ja").text
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
		if re.match("javascript:showItemDialog.*", href):
			start = href.index(",") + 3
			end = href.index("'", start)
			itemId.append(href[start: end])
	for name, count, id in zip(itemName, itemCount, itemId):
		result.append({"name": name, "count": count, "id": id})
	return result

def getItemPostedUser(screenId, itemId):
	req = requests.get("http://twitcasting.tv/gearajax.php?c=showitem&itemid=" + itemId + "&u=" + screenId + "&hl=ja").text
	soup = BeautifulSoup(req, "lxml")
	tmp = soup.find_all("span", class_ = "tw-user-name-screen-name")
	result = []
	for i in tmp:
		result.append(i.text[1:])
	return result
