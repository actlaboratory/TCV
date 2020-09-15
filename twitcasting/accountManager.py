# -*- coding: utf-8 -*-
# アクセストークン取得モジュール（暫定版）

import implicitGrantManager
import pickle

file = "accounts.dat"

class AccountManager:
	def __init__(self):
		open(file, "wb").close()
		self.manager = implicitGrantManager.ImplicitGrantManager("ckitabatake1013.48f1b75c1355aad8230bf1f36eb0c29b1ef04cf8047c41c1a03a566b545342fd","https://apiv2.twitcasting.tv/oauth2/authorize",9338)
		self.tokens = []
		try:
			self.loadFromFile()
		except:
			pass

	def loadFromFile(self):
		with open(file, "rb") as f:
			self.tokens = pickle.load(f)

	def saveFromFile(self):
		with open(file, "wb") as f:
			pickle.dump(self.tokens, f)

