# -*- coding: utf-8 -*-
#Simple dialog

import winsound
import wx

def dialog(title, message):
	dialog = wx.MessageDialog(None,message,title,wx.OK)
	winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
	dialog.ShowModal()
	dialog.Destroy()
	return

def yesNoDialog(title, message):
	dialog = wx.MessageDialog(None,message,title,wx.YES_NO)
	winsound.MessageBeep(winsound.MB_ICONQUESTION)
	result = dialog.ShowModal()
	dialog.Destroy()
	return result
