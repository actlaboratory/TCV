# -*- coding: utf-8 -*-
#Simple dialog

import wx

def dialog(title, message):
	dialog = wx.MessageDialog(None,message,title,wx.OK)
	dialog.ShowModal()
	dialog.Destroy()
	return

def yesNoDialog(title, message):
	dialog = wx.MessageDialog(None,message,title,wx.YES_NO)
	result = dialog.ShowModal()
	dialog.Destroy()
	return result

def errorDialog(message):
	dialog = wx.MessageDialog(None,message,_("エラー"),wx.OK|wx.ICON_ERROR)
	dialog.ShowModal()
	dialog.Destroy()
	return

def debugDialog(message):
	dialog = wx.MessageDialog(None,str(message),_("デバッグ用"),wx.OK)
	dialog.ShowModal()
	dialog.Destroy()
	return
