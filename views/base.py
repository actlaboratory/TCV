# -*- coding: utf-8 -*-
#views base class
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>

import wx
import constants
import keymap
import defaultKeymap
import menuItemsStore
import views.ViewCreator
from simpleDialog import dialog

import globalVars


class BaseView(object):
	"""ビューの基本クラス。"""
	def __init__(self):
		self.shortcutEnable=True

	def Initialize(self, ttl, x, y,px,py):
		"""タイトルとウィンドウサイズとポジションを指定して、ウィンドウを初期化する。"""
		self.hFrame=wx.Frame(None,-1,ttl, size=(x,y),pos=(px,py))
		self.hFrame.Bind(wx.EVT_MOVE_END,self.events.WindowMove)
		self.hFrame.Bind(wx.EVT_SIZE,self.events.WindowResize)

		self.hPanel=views.ViewCreator.makePanel(self.hFrame)
		self.creator=views.ViewCreator.ViewCreator(1,self.hPanel,None, wx.VERTICAL)

	def Show(self):
		self.creator.GetPanel().Layout()
		self.hFrame.Show()
		self.app.SetTopWindow(self.hFrame)
		return True

	def InstallMenuEvent(self,menu,event):
		"""メニューを作り、指定されたイベント処理用オブジェクトと結びつける。"""
		menu.Apply(self.hFrame)
		self.menu=menu

		#ショートカット無効状態の時に表示するダミーのメニューバー
		#これがないとメニューバーの高さ分画面がずれてしまうために必要
		self.hDisableMenuBar=wx.MenuBar()
		self.hDisableSubMenu=wx.Menu()
		self.hDisableMenuBar.Append(self.hDisableSubMenu,_("現在メニューは操作できません"))
		self.SetShortcutEnabled(True)

		self.hFrame.Bind(wx.EVT_MENU,event)

	def SetShortcutEnabled(self,en):
		"""
			ショートカットキーの有効/無効を切り替える。
			AcceleratorTableとメニューバーのそれぞれに登録されているので、両方の対策が必要。
		"""
		self.shortcutEnable=en
		if en:
			#通常のメニューバーに戻す
			self.hFrame.SetMenuBar(self.menu.hMenuBar)
		else:
			self.hFrame.SetMenuBar(self.menu.hDisableMenuBar)
		#SetMenuBarの後に呼び出しが必要
		self.creator.GetSizer().Layout()

		t=self.menu.acceleratorTable if en else wx.AcceleratorTable()
		self.hFrame.SetAcceleratorTable(t)

class BaseMenu(object):
	def __init__(self,identifier):
		"""acceleratorTable登録準備"""
		self.keymap=keymap.KeymapHandler(defaultKeymap.defaultKeymap)
		self.keymap_identifier=identifier
		self.keymap.addFile(constants.KEYMAP_FILE_NAME)
		errors=self.keymap.GetError(identifier)
		if errors:
			tmp=_(constants.KEYMAP_FILE_NAME+"で設定されたショートカットキーが正しくありません。キーが重複しているか、存在しないキー名を指定しています。以下のキーの設定内容をご確認ください。\n\n")
			for v in errors:
				tmp+=v+"\n"
			dialog(_("エラー"),tmp)
		self.acceleratorTable=self.keymap.GetTable(self.keymap_identifier)

	def RegisterMenuCommand(self,menu_handle,ref_id,title):
		"""メニューアイテム生成補助関数"""
		shortcut=self.keymap.GetKeyString(self.keymap_identifier,ref_id)
		s=title if shortcut is None else "%s\t%s" % (title,shortcut)
		menu_handle.Append(menuItemsStore.getRef(ref_id),s)


class BaseEvents(object):
	"""イベント処理のデフォルトの動作をいくつか定義してあります。"""
	def __init__(self,parent,identifier):
		self.parent=parent
		self.identifier=identifier

	def Exit(self,event=None):
		self.parent.hFrame.Destroy()

	# wx.EVT_MOVE_END→wx.MoveEvent
	def WindowMove(self,event):
		#設定ファイルに位置を保存
		globalVars.app.config[self.identifier]["positionX"]=self.parent.hFrame.GetPosition().x
		globalVars.app.config[self.identifier]["positionY"]=self.parent.hFrame.GetPosition().x

	# wx.EVT_SIZE→wx.SizeEvent
	def WindowResize(self,event):
		#設定ファイルにサイズを保存
		globalVars.app.config[self.identifier]["sizeX"]=event.GetSize().x
		globalVars.app.config[self.identifier]["sizeY"]=event.GetSize().y

		#sizerを正しく機能させるため、Skipの呼出が必須
		event.Skip()
