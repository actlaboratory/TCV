# -*- coding: utf-8 -*-
# アクセストークン取得モジュール（暫定版）

import implicitGrantManager
import pickle
import webbrowser
import time
import pathlib
import requests

file = "accounts.dat"

class AccountManager:
	def __init__(self):
		self.manager = implicitGrantManager.ImplicitGrantManager("ckitabatake1013.48f1b75c1355aad8230bf1f36eb0c29b1ef04cf8047c41c1a03a566b545342fd","https://apiv2.twitcasting.tv/oauth2/authorize",9338)
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
		webbrowser.open(self.manager.getUrl(), new=1, autoraise=True)
		while(True):
			time.sleep(0.01)
			if self.manager.getToken():
				self.tokens.append(self.manager.getToken())
				break
		self.saveAsFile()

	def verifyCredentials(self, idx):
		token = self.tokens[idx]["access_token"]
		result = requests.get("https://apiv2.twitcasting.tv/verify_credentials", headers = {
			"X-Api-Version": "2.0",
			"Authorization": "Bearer " + token
		}).json()
		self.tokens[idx]["user"] = result["user"]

