#controlBase for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>

import ctypes
import wx

class controlBase():
	def AcceptsFocusFromKeyboard(self):
		return self.focusFromKbd

	def hideScrollBar(self, orient=wx.VERTICAL):
		assert orient in (wx.VERTICAL, wx.HORIZONTAL, wx.VERTICAL | wx.HORIZONTAL)
		if orient & wx.VERTICAL==wx.VERTICAL:
			ctypes.windll.user32.ShowScrollBar(self.GetHandle(),1,0)
		if orient & wx.HORIZONTAL==wx.HORIZONTAL:
			ctypes.windll.user32.ShowScrollBar(self.GetHandle(),0,0)
