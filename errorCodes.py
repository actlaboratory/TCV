﻿# -*- coding: utf-8 -*-
#error codes

OK=0				#成功(エラーなし)
NOT_SUPPORTED=1		#サポートされていない呼び出し
FILE_NOT_FOUND=2
PARSING_FAILED=3

LOGIN_TWITCASTING_ERROR=4
LOGIN_TWITCASTING_WRONG_ACCOUNT=5
LOGIN_TWITTER_WRONG_ACCOUNT=6	#ID/PW誤り
LOGIN_CONFIRM_NEEDED=7	#ユーザによる権限付与が必要
LOGIN_TWITTER_ERROR=8
LOGIN_RECAPTCHA_NEEDED=9
LOGIN_UNKNOWN_ERROR=10





UNKNOWN=99999

CONNECT_TIMEOUT = 12
UPDATER_NEED_UPDATE = 200# アップデートが必要
UPDATER_LATEST = 204# アップデートが無い
UPDATER_VISIT_SITE = 205
UPDATER_BAD_PARAM = 400# パラメーターが不正
UPDATER_NOT_FOUND = 404# アプリケーションが存在しない
