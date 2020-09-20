# -*- coding: utf-8 -*-
# アクセストークン取得モジュール（暫定版）

import implicitGrantManager
import pickle
import webbrowser
import time
import pathlib
import requests
import datetime

file = "accounts.dat"

class AccountManager:
	def __init__(self):
		self.tokens = []
		f = pathlib.Path(file)
		if f.exists() == False:
			f.touch()
		try:
			self.loadFromFile()
		except:
			pass
		for i in range(0, len(self.tokens)):
			self.verifyCredentials(i)

	def loadFromFile(self):
		with open(file, "rb") as f:
			self.tokens = pickle.load(f)

	def saveAsFile(self):
		with open(file, "wb") as f:
			pickle.dump(self.tokens, f)

	def add(self):
		manager = implicitGrantManager.ImplicitGrantManager("ckitabatake1013.48f1b75c1355aad8230bf1f36eb0c29b1ef04cf8047c41c1a03a566b545342fd","https://apiv2.twitcasting.tv/oauth2/authorize",9338)
		webbrowser.open(manager.getUrl())
		while True:
			time.sleep(0.01)
			if manager.getToken():
				self.tokens.append(manager.getToken())
				break
		self.tokens[-1]["created"] = datetime.datetime.now().timestamp()
		self.tokens[-1]["default"] = False
		self.verifyCredentials(-1)
		self.saveAsFile()

	def verifyCredentials(self, idx):
		token = self.tokens[idx]["access_token"]
		result = requests.get("https://apiv2.twitcasting.tv/verify_credentials", headers = {
			"X-Api-Version": "2.0",
			"Authorization": "Bearer " + token
		}).json()
		self.tokens[idx]["user"] = result["user"]

	def setDefaultAccount(self, idx):
		for i in range(0, len(self.tokens)):
			if i == idx:
				self.tokens[i]["default"] = True
			else:
				self.tokens[i]["default"] = False
