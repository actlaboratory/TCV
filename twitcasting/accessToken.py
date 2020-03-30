# -*- coding: utf-8 -*-
# アクセストークン取得モジュール（暫定版）
# 現在はAccessToken.txtからの読み込みのみ対応

file = open("twitcasting\\AccessToken.txt", "r")
accessToken = file.readlines()[0]
file.close()
