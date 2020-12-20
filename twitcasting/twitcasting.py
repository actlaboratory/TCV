# -*- coding: utf-8 -*-
# ツイキャスAPI操作モジュール

import requests
import globalVars

baseURL = "https://apiv2.twitcasting.tv"
def makeHeader(token = None):
	if token == None:
		token = globalVars.app.accountManager.getDefaultToken()
	return {
		"X-Api-Version": "2.0",
		"Authorization": "Bearer " + token
	}

# User
def GetUserInfo(user_id):
	result = requests.get(baseURL + "/users/" + user_id, headers=makeHeader())
	dict = result.json()
	return dict

def VerifyCredentials():
	result = requests.get(baseURL + "/verify_credentials", headers=makeHeader())
	dict = result.json()
	return dict

# Movie
def GetMovieInfo(movie_id):
	result = requests.get(baseURL + "/movies/" + movie_id, headers=makeHeader())
	dict = result.json()
	return dict

def GetCurrentLive(user_id):
	result = requests.get(baseURL + "/users/" + user_id + "/current_live", headers=makeHeader())
	dict = result.json()
	return dict

# Comments
def GetComments(movie_id, offset=0, limit=10, slice_id=""):
	result = requests.get(baseURL + "/movies/" + str(movie_id) + "/comments?offset=" + str(offset) + "&limit=" + str(limit) + "&slice_id=" + str(slice_id), headers=makeHeader())
	dict = result.json()
	return dict

def PostComment(movie_id, comment, sns="none", token=None):
	result = requests.post(baseURL + "/movies/" + movie_id + "/comments", json = {"comment": comment, "sns": sns}, headers=makeHeader(token))
	dict = result.json()
	return dict

def DeleteComment(movie_id, comment_id):
	for i in globalVars.app.accountManager.tokens:
		result = requests.delete(baseURL + "/movies/" + movie_id + "/comments/" + comment_id, headers=makeHeader(i["access_token"]))
		if result.status_code == 200:
			break
	dict = result.json()
	return dict

# Category
def GetCategories(lang = "ja"):
	result = requests.get(baseURL + "/categories?lang=" + lang, headers=makeHeader())
	dict = result.json()
	return dict
