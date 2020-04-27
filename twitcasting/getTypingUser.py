# -*- coding: utf-8 -*-
# タイピングメッセージの取得

import requests
import datetime

def getTypingUser(user, myself):
	req = requests.get("http://twitcasting.tv/streamchecker.php?u=" + user + "&v=999&myself=" + myself + "&islive=1&lastitemid=-1&__c=" + str(int(datetime.datetime.now().timestamp())) + "000").text
	result = req.split("\t")
	return result[8]
