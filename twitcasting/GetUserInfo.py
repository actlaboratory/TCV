# -*- coding: utf-8 -*-
# ���[�U���擾���W���[��

import constants
import requests

def GetUserInfo(user_id):
	req = requests.get(constants.baseURL + "/users/" + user_id, headers=constants.baseHeaders)
	return req.text
