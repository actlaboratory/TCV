# -*- coding: utf-8 -*-
# ツイキャスAPI操作モジュール

import requests

baseURL = "https://apiv2.twitcasting.tv"
baseHeaders = {
	"X-Api-Version": "2.0",
	# "Authorization": "Bearer " + accessToken
}

# User
def GetUserInfo(user_id):
	result = requests.get(baseURL + "/users/" + user_id, headers=baseHeaders)
	dict = result.json()
	return dict

def VerifyCredentials():
	result = requests.get(baseURL + "/verify_credentials", headers=baseHeaders)
	dict = result.json()
	return dict

# Movie
def GetMovieInfo(movie_id):
	result = requests.get(baseURL + "/movies/" + movie_id, headers=baseHeaders)
	dict = result.json()
	return dict

def GetCurrentLive(user_id):
	result = requests.get(baseURL + "/users/" + user_id + "/current_live", headers=baseHeaders)
	dict = result.json()
	return dict

# Comments
def GetComments(movie_id, offset=0, limit=10, slice_id=""):
	result = requests.get(baseURL + "/movies/" + str(movie_id) + "/comments?offset=" + str(offset) + "&limit=" + str(limit) + "&slice_id=" + str(slice_id), headers=baseHeaders)
	dict = result.json()
	if "error" in dict:
		return dict
	else:
		return dict["comments"]

def PostComment(movie_id, comment, sns="none"):
	result = requests.post(baseURL + "/movies/" + movie_id + "/comments", json = {"comment": comment, "sns": sns}, headers=baseHeaders)
	dict = result.json()
	return dict

def DeleteComment(movie_id, comment_id):
	result = requests.delete(baseURL + "/movies/" + movie_id + "/comments/" + comment_id, headers=baseHeaders)
	dict = result.json()
	return dict

# Category
def GetCategories(lang = "ja"):
	result = requests.get(baseURL + "/categories?lang=" + lang, headers=baseHeaders)
	dict = result.json()
	return dict["categories"]
