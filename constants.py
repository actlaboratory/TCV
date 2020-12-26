# -*- coding: utf-8 -*-
#constant values
#Copyright (C) 20XX anonimous <anonimous@sample.com>

import wx

#アプリケーション基本情報
APP_NAME="TCV"
APP_FULL_NAME = "Twitcasting Viewer"
APP_VERSION="0.0.1"
APP_ICON = None
APP_COPYRIGHT_YEAR="2020"
APP_DEVELOPERS="ACT Laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL=""
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All lights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

#対応言語
SUPPORTING_LANGUAGE={"ja_JP": "日本語","en_US": "English"}

#各種ファイル名
SETTING_FILE_NAME="settings.ini"
KEYMAP_FILE_NAME="keymap.ini"
LOG_PREFIX="app"
LOG_FILE_NAME="application.log"
HISTORY_FILE_NAME="history.dat"
FAVORITES_FILE_NAME="favorites.dat"
TOKEN_FILE_NAME="accounts.dat"

#フォントの設定可能サイズ範囲
FONT_MIN_SIZE=5
FONT_MAX_SIZE=35

#３ステートチェックボックスの状態定数
NOT_CHECKED=wx.CHK_UNCHECKED
HALF_CHECKED=wx.CHK_UNDETERMINED
FULL_CHECKED=wx.CHK_CHECKED

#メニュー
MENU_URL_FIRST=10000
#build関連定数
BASE_PACKAGE_URL = None#差分元のpackageのファイル名またはURL
PACKAGE_CONTAIN_ITEMS = ("fx",)#パッケージに含めたいファイルやfolderがあれば指定
NEED_HOOKS = ()#pyinstallerのhookを追加したい場合は指定
STARTUP_FILE = "tcv.py"#起動用ファイルを指定
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_VERSION = "1.0.0"
UPDATER_WAKE_WORD = "hello"
