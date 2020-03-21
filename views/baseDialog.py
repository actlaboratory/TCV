# -*- coding: utf-8 -*-
#dialogs base class
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>

import wx
import constants
import globalVars
import _winxptheme

class BaseDialog(object):
	"""モーダルダイアログの基本クラス。"""
	def __init__(self):
		self.app=globalVars.app
		self.value=None

	def Initialize(self, parent,ttl):
		"""タイトルを指定して、ウィンドウを初期化し、親の中央に配置するように設定。"""
		self.wnd=wx.Dialog(parent,-1, ttl,style=wx.DEFAULT_DIALOG_STYLE | wx.BORDER_DEFAULT)
		_winxptheme.SetWindowTheme(self.wnd.GetHandle(),"","")

		self.panel = wx.Panel(self.wnd,wx.ID_ANY)
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.sizer)

	def Show(self):
		result=self.wnd.ShowModal()
		if result!=wx.ID_CANCEL:
			self.value=self.GetData()
		self.Destroy()
		return result

	def Destroy(self):
		self.log.debug("destroy")
		self.wnd.Destroy()

	def GetValue(self):
		return self.value

	def GetData(self):
		return None

	#ウィンドウを中央に配置してモーダル表示する
	#ウィンドウ内の部品を全て描画してから呼び出す
	def ShowModal(self):
		self.sizer.Fit(self.wnd)
		self.wnd.Centre()
		return self.wnd.ShowModal()
