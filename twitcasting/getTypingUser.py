# -*- coding: utf-8 -*-
# タイピングメッセージの取得

import requests
import datetime
import constants
from logging import getLogger
import traceback
import sys

log = getLogger("%s.%s" %(constants.LOG_PREFIX, "twitcasting.getTypingUser"))

def getTypingUser(user, myself):
	try:
		req = requests.get("http://twitcasting.tv/streamchecker.php?u=" + user + "&v=999&myself=" + myself + "&islive=1&lastitemid=-1&__c=" + str(int(datetime.datetime.now().timestamp())) + "000").text
	except:
		log.error("Connection failed.")
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return ""
	result = req.split("\t")
	try:
		return result[8]
	except:
		log.error("Failed. data: %s" %result)
		log.error(traceback.format_exc())
		if not hasattr(sys, "frozen"):
			import winsound
			winsound.Beep(1000, 1000)
			traceback.print_exc()
		return ""
