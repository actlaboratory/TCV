# -*- coding: utf-8 -*-
# ツイキャスAPI操作モジュール

import requests
from twitcasting.accessToken import accessToken
import json

baseURL = "https://apiv2.twitcasting.tv"
baseHeaders = {
	"X-Api-Version": "2.0",
	"Authorization": "Bearer " + accessToken
}

# User
def GetUserInfo(user_id):
	req = requests.get(baseURL + "/users/" + user_id, headers=baseHeaders).text
	dict = json.loads(req)
	return dict

def VerifyCredentials():
	req = requests.get(baseURL + "/verify_credentials", headers=baseHeaders).text
	dict = json.loads(req)
	return dict

# Movie
def GetMovieInfo(movie_id):
	req = requests.get(baseURL + "/movies/" + movie_id, headers=baseHeaders).text
	dict = json.loads(req)
	return dict

def GetCurrentLive(user_id):
	req = requests.get(baseURL + "/users/" + user_id + "/current_live", headers=baseHeaders).text
	dict = json.loads(req)
	return dict

# Comments
def GetComments(movie_id, offset=0, limit=10, slice_id=""):
	req = requests.get(baseURL + "/movies/" + str(movie_id) + "/comments?offset=" + str(offset) + "&limit=" + str(limit) + "&slice_id=" + str(slice_id), headers=baseHeaders).text
	dict = json.loads(req)
	if "error" in dict:
		return dict
	else:
		return dict["comments"]

def PostComment(movie_id, comment, sns="none"):
	req = requests.post(baseURL + "/movies/" + movie_id + "/comments", json = {"comment": comment, "sns": sns}, headers=baseHeaders).text
	dict = json.loads(req)
	return dict

def DeleteComment(movie_id, comment_id):
	req = requests.delete(baseURL + "/movies/" + movie_id + "/comments/" + comment_id, headers=baseHeaders).text
	dict = json.loads(req)
	return dict

