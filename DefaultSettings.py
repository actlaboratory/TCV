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
			"timerType": 0,
			"historyMax": 10,
			"defaultConnectAccount": ""
		}
		config["view"]={
			"font": "bold 'ＭＳ ゴシック' 22 windows-932",
			"colorMode":"normal"
		}
		config["mainView"]={
			"sizeX": "800",
			"sizeY": "600",
		}
		config["speech"] = {
			"reader": "AUTO",
		}
		config["autoReadingOptions"]={
			"readReceivedComments": True,
			"receivedCommentsAnnouncement": "$dispname,$message,$time,$user",
			"readMyComment": True,
			"readMentions_myLive": 1,
			"readMentions_otherLive": 1,
			"readViewers": True,
			"viewersIncreasedAnnouncement": "閲覧者が$viewers人に増えました。",
			"viewersDecreasedAnnouncement": "閲覧者が$viewers人に減りました。",
			"readTypingUser": False,
			"readReceivedItems": True,
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
			"defaultVolume": 100,
			"audioDelay": 10,
			"device": "",
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
			"playTimerSound": True,
			"timerSound": "fx\\time.wav",
			"playStartupSound": False,
			"startupSound": "fx\\info.wav",
			"syncAudioDevice": False,
			"fxVolume": 100
		}
		return config

initialValues={}
"""
	この辞書には、ユーザによるキーの削除が許されるが、初回起動時に組み込んでおきたい設定のデフォルト値を設定する。
	ここでの設定はユーザの環境に設定ファイルがなかった場合のみ適用され、初期値として保存される。
"""
