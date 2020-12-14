#listCtrlBase for ViewCreator
#Copyright (C) 2019-2020 Hiroki Fujii <hfujii@hisystron.com>
#Copyright (C) 2020 yamahubuki <itiro.ishino@gmail.com>


import wx
from views.viewObjectBase import viewObjectUtil, controlBase

class listCtrl(controlBase.controlBase, wx.ListCtrl):
	def __init__(self, *pArg, **kArg):
		self.focusFromKbd = viewObjectUtil.popArg(kArg, "enableTabFocus", True) #キーボードフォーカスの初期値
		return super().__init__(*pArg, **kArg)

	#ポップアップメニューの表示位置をクライアント座標のwx.Pointで返す
	def getPopupMenuPosition(self):
		if  self.GetFocusedItem()>=0:
			rect=self.GetItemRect(self.GetFocusedItem(),wx.LIST_RECT_LABEL)
			return rect.GetBottomRight()
		else:
			return super().getPopupMenuPosition()
