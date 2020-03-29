# -*- coding: utf-8 -*-
# ユーザ情報取得モジュール

import constants
import requests

def GetUserInfo(user_id):
	req = requests.get(constants.baseURL + "/users/" + user_id, headers=constants.baseHeaders)
	return req.text
