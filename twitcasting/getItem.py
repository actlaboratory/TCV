# -*- coding: utf-8 -*-
# アイテム情報取得モジュール

import requests
from bs4 import BeautifulSoup
import simpleDialog

def getItem(screenId):
	req = requests.get("http://twitcasting.tv/gearajax.php?c=showitems&u=" + screenId + "&hl=ja").text
	soup = BeautifulSoup(req, "lxml")
	itemName = []
	itemCount = []
	result = {}
	tmp = soup.find_all("img", class_ = "item")
	for i in tmp:
		itemName.append(i.get("title"))
	tmp = soup.find_all("span", class_ = "tw-item-count-badge")
	for i in tmp:
		itemCount.append(i.text)
	for keys, values in zip(itemName, itemCount):
		result[keys] = values
	return result
