# -*- coding: utf-8 -*-
# ツイキャスとの通信用定数

from accessToken import accessToken

baseURL = "https://apiv2.twitcasting.tv"
baseHeaders = {
	"X-Api-Version": "2.0",
	"Authorization": "Bearer {" + accessToken + "}"
}
