# -*- coding: utf-8 -*-
#views base class
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>

import _winxptheme
import wx

import constants
import defaultKeymap
import globalVars
import keymap
import menuItemsStore
import views.ViewCreator

from logging import getLogger
from simpleDialog import dialog


class BaseView(object):
	"""ビューの基本クラス。"""
	def __init__(self,identifier):
		self.identifier=identifier
		self.log=getLogger("%s.%s" % (constants.LOG_PREFIX,self.identifier))
		self.shortcutEnable=True
		self.viewMode=globalVars.app.config.getstring("view","colorMode","white",("white","dark"))
		self.app=globalVars.app


	def Initialize(self, ttl, x, y,px,py,style=wx.DEFAULT_FRAME_STYLE):
		"""タイトルとウィンドウサイズとポジションを指定して、ウィンドウを初期化する。"""
		self.hFrame=wx.Frame(None,wx.ID_ANY,ttl, size=(x,y),pos=(px,py),name=ttl,style=style)
		_winxptheme.SetWindowTheme(self.hFrame.GetHandle(),"","")
		self.hFrame.Bind(wx.EVT_MOVE_END,self.events.WindowMove)
		self.hFrame.Bind(wx.EVT_SIZE,self.events.WindowResize)
		self.hFrame.Bind(wx.EVT_CLOSE,self.events.Exit)
		self.MakePanel()

	def MakePanel(self):
		self.hPanel=views.ViewCreator.makePanel(self.hFrame)
		self.creator=views.ViewCreator.ViewCreator(self.viewMode,self.hPanel,None, wx.VERTICAL)

	def Clear(self):
		self.hFrame.DestroyChildren()
		self.MakePanel()

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
		"""メニューバー・acceleratorTable登録準備"""
		self.hMenuBar=wx.MenuBar()
		self.keymap=keymap.KeymapHandler(defaultKeymap.defaultKeymap,keymap.KeyFilter().SetDefault(False,True))
		self.keymap_identifier=identifier
		self.keymap.addFile(constants.KEYMAP_FILE_NAME)
		errors=self.keymap.GetError(identifier)
		if errors:
			tmp=_(constants.KEYMAP_FILE_NAME+"で設定されたショートカットキーが正しくありません。キーの重複、存在しないキー名の指定、使用できないキーパターンの指定などが考えられます。以下のキーの設定内容をご確認ください。\n\n")
			for v in errors:
				tmp+=v+"\n"
			dialog(_("エラー"),tmp)
		self.acceleratorTable=self.keymap.GetTable(self.keymap_identifier)

		#これ以降はユーザ設定の追加なのでフィルタを変更
		self.keymap.filter=keymap.KeyFilter().SetDefault(False,False)

	def RegisterMenuCommand(self,menu_handle,ref_id,title="",subMenu=None,index=-1):
		if type(ref_id)==dict:
			for k,v in ref_id.items():
				self._RegisterMenuCommand(menu_handle,k,v,None,index)
		else:
			return self._RegisterMenuCommand(menu_handle,ref_id,title,subMenu,index)

	def _RegisterMenuCommand(self,menu_handle,ref_id,title,subMenu,index):
		if ref_id=="" and title=="":
			if index>=0:
				menu_handle.InsertSeparator()
			else:
				menu_handle.AppendSeparator()
			return
		shortcut=self.keymap.GetKeyString(self.keymap_identifier,ref_id)
		s=title if shortcut is None else "%s\t%s" % (title,shortcut)
		if subMenu==None:
			if index>=0:
				menu_handle.Insert(index,menuItemsStore.getRef(ref_id),s)
			else:
				menu_handle.Append(menuItemsStore.getRef(ref_id),s)
		else:
			if index>=0:
				menu_handle.Insert(index,menuItemsStore.getRef(ref_id),s,subMenu)
			else:
				menu_handle.Append(menuItemsStore.getRef(ref_id),s,subMenu)

	def RegisterCheckMenuCommand(self,menu_handle,ref_id,title,index=-1):
		"""チェックメニューアイテム生成補助関数"""
		shortcut=self.keymap.GetKeyString(self.keymap_identifier,ref_id)
		s=title if shortcut is None else "%s\t%s" % (title,shortcut)
		if index>=0:
			menu_handle.InsertCheckItem(index,menuItemsStore.getRef(ref_id),s)
		else:
			menu_handle.AppendCheckItem(menuItemsStore.getRef(ref_id),s)

	def RegisterRadioMenuCommand(self,menu_handle,ref_id,title,index=-1):
		"""ラジオメニューアイテム生成補助関数"""
		shortcut=self.keymap.GetKeyString(self.keymap_identifier,ref_id)
		s=title if shortcut is None else "%s\t%s" % (title,shortcut)
		if index>=0:
			menu_handle.InsertRadioItem(index,menuItemsStore.getRef(ref_id),s)
		else:
			menu_handle.AppendRadioItem(menuItemsStore.getRef(ref_id),s)

	def CheckMenu(ref_id,state=True):
		return self.menu.Check(menuItemsStore.getRef(ref_id),state)

	def EnableMenu(self,ref_id,enable=True):
		return self.hMenuBar.Enable(menuItemsStore.getRef(ref_id),enable)

	def getItemInfo(self):
		"""
			メニューに登録されたすべてのアイテムを[(表示名,ref)...]で返します。
		"""
		ret=[]
		print(self.hMenuBar.GetMenus())
		print(self.hMenuBar.GetMenuCount())

		if self.hMenuBar==None:
			return ret
		for menu,id in self.hMenuBar.GetMenus():
			print(menu)
			self._addMenuItemList(menu,ret)
		return ret

	def _addMenuItemList(self,menu,ret):
		if type(menu)==wx.Menu:
			items=menu.GetMenuItems()
		else:
			items=menu.GetSubMenu().GetMenuItems()
		for item in items:
			if item.GetSubMenu()!=None:
				self._addMenuItemList(item,ret)
			else:
				if item.GetItemLabelText()!="":		#セパレータ対策
					ret.append((item.GetItemLabelText(),item.GetId()))

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
		globalVars.app.config[self.identifier]["positionY"]=self.parent.hFrame.GetPosition().y

	# wx.EVT_SIZE→wx.SizeEvent
	def WindowResize(self,event):
		#ウィンドウがアクティブでない時(ウィンドウ生成時など)のイベントは無視
		if self.parent.hFrame.IsActive():
			#最大化状態でなければ、設定ファイルにサイズを保存
			if not self.parent.hFrame.IsMaximized():
				globalVars.app.config[self.identifier]["sizeX"]=event.GetSize().x
				globalVars.app.config[self.identifier]["sizeY"]=event.GetSize().y

			#設定ファイルに最大化状態か否かを保存
			globalVars.app.config[self.identifier]["maximized"]=self.parent.hFrame.IsMaximized()

		#sizerを正しく機能させるため、Skipの呼出が必須
		event.Skip()

