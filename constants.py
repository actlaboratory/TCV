# -*- coding: utf-8 -*-
#constant values
#Copyright (C) 20XX anonimous <anonimous@sample.com>

import wx

#アプリケーション基本情報
APP_NAME="TCV"
APP_FULL_NAME = "TwitCasting Viewer"
APP_VERSION="3.3.0"
APP_LAST_RELEASE_DATE = "2021-07-24"
APP_ICON = None
APP_COPYRIGHT_YEAR="2019-2022"
APP_LICENSE="GNU General Public License2.0 or later"
APP_DEVELOPERS="Kazto Kitabatake, ACT Laboratory"
APP_DEVELOPERS_URL="https://actlab.org/"
APP_DETAILS_URL="https://actlab.org/software/TCV"
APP_COPYRIGHT_MESSAGE = "Copyright (c) %s %s All rights reserved." % (APP_COPYRIGHT_YEAR, APP_DEVELOPERS)

#対応言語
SUPPORTING_LANGUAGE={"ja-JP": "日本語","en-US": "English"}

#各種ファイル名
SETTING_FILE_NAME="data\\settings.ini"
KEYMAP_FILE_NAME="data\\keymap.ini"
LOG_PREFIX="TCV"
LOG_FILE_NAME="TCV.log"
HISTORY_FILE_NAME="data\\history.dat"
FAVORITES_FILE_NAME="data\\favorites.dat"
TOKEN_FILE_NAME="data\\accounts.dat"
SESSION_FILE_NAME = "data\\sessions.dat"
README_FILE_NAME = "readme.txt"

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
BASE_PACKAGE_URL = "https://github.com/actlaboratory/TCV/releases/download/3.0.0/TCV-3.0.0.zip"
PACKAGE_CONTAIN_ITEMS = ("fx",)#パッケージに含めたいファイルやfolderがあれば指定
NEED_HOOKS = ()#pyinstallerのhookを追加したい場合は指定
STARTUP_FILE = "tcv.py"#起動用ファイルを指定
UPDATER_URL = "https://github.com/actlaboratory/updater/releases/download/1.0.0/updater.zip"

# update情報
UPDATE_URL = "https://actlab.org/api/checkUpdate"
UPDATER_VERSION = "1.0.0"
UPDATER_WAKE_WORD = "hello"

# タイトルバー
TB_NONE = 0
TB_TIME = 1
TB_USER = 2
# TwitCasting
TC_CID = "1266762249164619776.c2ee817dafca62d74bbf3af6a7db1ad1c3cce334bef6e3af82c146d670f3cefe"
TC_URL = "https://apiv2.twitcasting.tv/oauth2/authorize"
TC_PORT = 9338

# URLスキーム
SCHEME_NAME = "tcv"