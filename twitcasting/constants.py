# -*- coding: utf-8 -*-
# �c�C�L���X�Ƃ̒ʐM�p�萔

from accessToken import accessToken

baseURL = "https://apiv2.twitcasting.tv"
baseHeaders = {
	"X-Api-Version": "2.0",
	"Authorization": "Bearer {" + accessToken + "}"
}
