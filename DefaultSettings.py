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
			"readReceivedComments": True,
			"receivedCommentsAnnouncement": "$dispname,$message,$time,$user",
			"readMyComment": True,
			"readMentions_myLive": 1,
			"readMentions_otherLive": 1,
			"announceViewers": True,
			"viewersIncreasedAnnouncement": "閲覧者が$viewers人に増えました。",
			"viewersDecreasedAnnouncement": "閲覧者が$viewers人に減りました。",
			"announceTypingUser": False,
			"announceReceivedItems": True,
			"readItemPostedUser": 0
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
		config["livePlay"]={
			"autoPlay": False,
			"defaultVolume": 100
		}
		config["fx"] = {
			"playCommentReceivedSound": True,
			"commentReceivedSound": "fx\\receive.wav",
			"playViewersChangedSound": True,
			"viewersChangedSound": "fx\\info.wav",
			"playItemReceivedSound": True,
			"itemReceivedSound": "fx\\item.wav",
			"playCommentPostedSound": True,
			"commentPostedSound": "fx\\comsend.wav",
			"playTypingSound": True,
			"typingSound": "fx\\typing.wav",
			"playStartupSound": False,
			"startupSound": "fx\\info.wav"
		}
		return config
