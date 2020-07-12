# -*- coding: utf-8 -*-
#default config

from ConfigManager import *


class DefaultSettings:
	def get():
		config = ConfigManager()
		config["general"]={
			"language": "ja-JP",
			"fileVersion": "100",
			"locale": "ja-JP",
			"initialCommentCount": 50,
			"commentToSns": 0,
			"historyMax": 10
		}
		config["view"]={
			"font": "bold 'ＭＳ ゴシック' 22 windows-932",
			"colorMode":"normal"
		}
		config["mainView"]={
			"sizeX": "800",
			"sizeY": "600",
		}
		config["autoReadingOptions"]={
			"output": "AUTO",
			"announceReceivedComments": 1,
			"receivedCommentsAnnouncement": "$dispname,$message,$time,$user",
			"announceViewers": True,
			"viewersIncreasedAnnouncement": "閲覧者が$viewers人に増えました。",
			"viewersDecreasedAnnouncement": "閲覧者が$viewers人に減りました。",
			"announceTypingUser": False,
			"announceReceivedItems": True,
			"readMentions_myLive": 1,
			"readMentions_otherLive": 1
		}
		config["commentReplaceBasic"]={
		}
		config["commentReplaceReg"] = {
		}
		config["commentReplaceSpecial"] = {
			"deleteProtcolName": False,
			"onlyDomain": False,
			"url": ""
		}
		config["nameReplace"] = {
		}

		return config
