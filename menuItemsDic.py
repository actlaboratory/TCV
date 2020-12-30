#menuItemsDic
#Copyright (C) 2020 Hiroki Fujii <hfujii@hisystron.com>

import re

def getValueString(ref_id):
	""" ナビキーとダイアログ文字列を消去した文字列を取り出し """
	dicVal = dic[ref_id]
	s = re.sub("\.\.\.$", "", dicVal)
	s = re.sub("\(&.\)$", "", s)
	return re.sub("&", "", s)

dic={
	"CONNECT": _("接続(&C)") + "...",
	"VIEW_HISTORY": _("接続履歴を開く(&H)") + "...",
	"VIEW_FAVORITES": _("お気に入り一覧を開く(&F)") + "...",
	"DISCONNECT": _("切断(&D)"),
	"EXIT": _("終了(&X)"),
	#再生メニュー
	"PLAY": _("再生(&P)"),
	"STOP": _("停止(&S)"),
	"VOLUME_UP": _("音量を上げる(&U)"),
	"VOLUME_DOWN": _("音量を下げる(&D)"),
	"RESET_VOLUME": _("音量を１００％に設定(&R)"),
	"CHANGE_DEVICE": _("再生デバイスを変更(&C)") + "...",
	#コメントメニュー
	"COPY_COMMENT":  _("選択中のコメントをコピー(&C)"),
	"VIEW_COMMENT": _("コメントの詳細を表示(&V)") + "...",
	"REPLY2SELECTED_COMMENT": _("選択中のコメントに返信(&R)"),
	"DELETE_SELECTED_COMMENT": _("選択中のコメントを削除(&D)"),
	"REPLY2BROADCASTER": _("配信者に返信(&B)"),
	"SELECT_ALL_COMMENT": _("全てのコメントを選択(&A)"),
	#ライブメニュー
	"VIEW_BROADCASTER": _("配信者の情報を表示(&B)") + "...",
	"OPEN_LIVE": _("このライブをブラウザで開く(&O)"),
	"ADD_FAVORITES": _("お気に入りに追加(&A)") + "...",
	#設定メニュー
	"SETTING": _("設定(&S)") + "...",
	"SET_KEYMAP": _("ショートカットキーの設定(&K)") + "...",
	"SET_HOTKEY": _("グローバルホットキーの設定(&G)") + "...",
	 "INDICATOR_SOUND_SETTING": _("効果音設定(&I)") + "...",
	"COMMENT_REPLACE": _("コメント文字列置換設定(&C)") + "...",
	"USER_NAME_REPLACE": _("表示名置換設定(&N)") + "...",
	"ACCOUNT_MANAGER": _("アカウントマネージャ(&M)") + "...",
	"SAPI_SETTING": _("SAPI設定を開く(&A)") + "...",
	#ヘルプメニュー
	"HELP": _("ヘルプを開く(&H)"),
	"VERSION_INFO": _("バージョン情報(&V)") + "...",
	"CHECK4UPDATE": _("更新を確認(&C)") + "...",
	#その他
	"SILENCE": _("読み上げの中断"),
	"":""		#セパレータ追加時用
}
