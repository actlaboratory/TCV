# twitcastingAccount login
# Copyright (C) 2021 yamahubuki <itiro.ishino@gmail.com>

import requests
import errorCodes

#IDとpwを用いてログインし、セッションを返却
#ID冒頭のc:は不要
def login(id,pw):
	session = requests.Session()

	# STEP1: Refeler対策のため、トップページへダミーアクセス
	ret = session.get("https://twitcasting.tv/",timeout=5)
	if ret.status_code!=200:
		return errorCodes.LOGIN_TWITCASTING_ERROR

	# STEP2: ログイン用のリクエスト
	headers = {
		"Content-Type":"application/x-www-form-urlencoded",
		"Accept":"Accept: text/html, application/xhtml+xml, image/jxr, */*",
		"Accept-Language":"ja-JP",
		"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
	}
	body = {
		"username":id,
		"password":pw,
		"action":"login",
	}
	result = session.post("https://twitcasting.tv/indexcaslogin.php?redir=%2F"+"&keep=1", body, headers=headers, timeout=5)

	#STEP3: 結果の判定と返却
	if result.status_code!=200 or len(result.history)!=1 or result.history[0].status_code!=302 or result.url!="https://twitcasting.tv/":
		if result.status_code==200 and len(result.history)==0 and result.url.startswith("https://twitcasting.tv/indexcaslogin.php?"):
			return errorCodes.LOGIN_TWITCASTING_WRONG_ACCOUNT
		return errorCodes.LOGIN_TWITCASTING_ERROR
	return session
