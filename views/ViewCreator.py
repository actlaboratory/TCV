# -*- coding: utf-8 -*-
#View Creator
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import ctypes
import win32api
import _winxptheme
import wx
#import wx.adv

from . import fontManager

viewHelper=ctypes.cdll.LoadLibrary("viewHelper.dll")

NORMAL=0
BUTTON_COLOUR=1
SKIP_COLOUR=2

GridSizer = -1
FlexGridSizer = -2

MODE_WHITE=0
MODE_DARK=1

class ViewCreator():

	# mode=1で白黒反転。その他は白。
	def __init__(self,mode,parent,parentSizer=None,orient=wx.HORIZONTAL,space=0,label="",style=0,proportion=0):
		#表示モード
		if mode==MODE_WHITE or mode=="white":
			self.mode=MODE_WHITE
		elif mode==MODE_DARK or mode=="dark":
			self.mode=MODE_DARK
		else:
			raise ValueError("モードはwhiteかdarkで指定してください。")

		#初期設定フォント
		self.font=fontManager.FontManager()

		#親ウィンドウ
		self.parent=parent
		self._setFace(parent)

		#サイザー作成
		if orient==FlexGridSizer:
			self.sizer=self.FlexGridSizer(parentSizer,space,style)
			self.sizer.SetHGap(space)
			self.sizer.SetVGap(space)
		elif orient==GridSizer:
			self.sizer=self.GridSizer(parentSizer,space,style)
			self.sizer.SetHGap(space)
			self.sizer.SetVGap(space)
		else:
			self.sizer=self.BoxSizer(parentSizer,orient,label,space,style,proportion)

		self.space=space
		self.AddSpace(self.space)

	#BoxSizerの下にスペースを挿入
	def AddSpace(self,space=-1):
		if self.sizer.__class__==wx.BoxSizer or self.sizer.__class__==wx.StaticBoxSizer:
			if space==-1:
				space==self.space
			self.sizer.AddSpacer(space)


	#parentで指定したsizerの下に、新たなBoxSizerを設置
	def BoxSizer(self,parent,orient=wx.VERTICAL,label="",space=0,style=0,proportion=0):
		if label=="":
			sizer=wx.BoxSizer(orient)
		else:
			sizer=wx.StaticBoxSizer(orient,self.parent,label)
			self._setFace(sizer.GetStaticBox())
		if type(parent) in (wx.Panel,wx.Window):
			parent.SetSizer(sizer)
		elif (parent==None):
			self.parent.SetSizer(sizer)
		else:
			Add(parent,sizer,proportion,wx.ALL | style,space)
		return sizer

	def GridSizer(self,parent,space=0,style=0):
		sizer=wx.GridSizer(2,0,space,space)
		if type(parent) in (wx.Panel,wx.Window):
			parent.SetSizer(sizer)
		elif (parent==None):
			self.parent.SetSizer(sizer)
		else:
			parent.Add(sizer,0,wx.ALL | style,space)
		return sizer

	def FlexGridSizer(self,parent,space=0,style=0):
		sizer=wx.FlexGridSizer(2)
		if type(parent) in (wx.Panel,wx.Window):
			parent.SetSizer(sizer)
		elif (parent==None):
			self.parent.SetSizer(sizer)
		else:
			parent.Add(sizer,0,wx.ALL | style,space)
		return sizer


	def button(self,text, event=None, sizerFlag=wx.ALL, proportion=0):
		hButton=wx.Button(self.parent, wx.ID_ANY,label=text, name=text, style=wx.BORDER_RAISED)
		hButton.Bind(wx.EVT_BUTTON,event)
		self._setFace(hButton,mode=BUTTON_COLOUR)
		Add(self.sizer,hButton,proportion,sizerFlag)
		self.AddSpace()
		return hButton

	def okbutton(self,text, event=None, sizerFlag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL,proportion=0):
		hButton=wx.Button(self.parent, wx.ID_OK,label=text, name=text,style=wx.BORDER_RAISED)
		hButton.Bind(wx.EVT_BUTTON,event)
		self._setFace(hButton,mode=BUTTON_COLOUR)
		Add(self.sizer,hButton,proportion,sizerFlag,5)
		hButton.SetDefault()
		self.AddSpace()
		return hButton

	def cancelbutton(self,text, event=None, sizerFlag=wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL,proportion=0):
		hButton=wx.Button(self.parent, wx.ID_CANCEL,label=text, name=text,style=wx.BORDER_RAISED)
		hButton.Bind(wx.EVT_BUTTON,event)
		self._setFace(hButton,mode=BUTTON_COLOUR)
		Add(self.sizer,hButton,proportion,sizerFlag,5)
		self.AddSpace()
		return hButton

	def staticText(self, text, style=0, x=-1, sizerFlag=wx.ALIGN_CENTER_VERTICAL, proportion=0):
		hStatic=wx.StaticText(self.parent,wx.ID_ANY,label=text,name=text,size=(x,-1),style=style)
		self._setFace(hStatic)
		Add(self.sizer,hStatic,proportion,sizerFlag)
		self.AddSpace()
		return hStatic

	def combobox(self,text, selection, event=None, state=-1, style=wx.CB_READONLY, x=-1, sizerFlag=wx.ALL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		v=""
		if state>=0:
			v=selection[state]
		hCombo=wx.ComboBox(self.parent,wx.ID_ANY,value=v,choices=selection,style=wx.BORDER_RAISED | style,name=text,size=(x,-1))
		hCombo.Bind(wx.EVT_TEXT,event)
		self._setFace(hCombo)
		Add(sizer,hCombo,proportion,sizerFlag,5)
		self.AddSpace()
		return hCombo,hStaticText

	def comboEdit(self,text, selection, event=None, defaultValue="", style=wx.CB_DROPDOWN, x=-1, sizerFlag=wx.ALL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		hCombo=wx.ComboBox(self.parent,wx.ID_ANY,value=defaultValue,choices=selection,style=wx.BORDER_RAISED | style,name=text,size=(x,-1))
		hCombo.Bind(wx.EVT_TEXT,event)
		if defaultValue in selection:
			hCombo.SetSelection(selection.index(defaultValue))
		self._setFace(hCombo)
		if x==-1:	#幅を拡張
			Add(sizer,hCombo,proportion,sizerFlag,expandFlag=wx.HORIZONTAL)
		else:
			Add(sizer,hCombo,proportion,sizerFlag)
		self.AddSpace()
		return hCombo,hStaticText

	def checkbox(self,text, event=None, state=False, style=0, x=-1, sizerFlag=0, proportion=0):
		hPanel=wx.Panel(self.parent,wx.ID_ANY)
		self._setFace(hPanel)
		hSizer=self.BoxSizer(hPanel,self.sizer.GetOrientation())

		if (isinstance(text,str)):	#単純に一つを作成
			hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=text, name=text,size=(x,-1),style=style)
			hCheckBox.SetValue(state)
			hCheckBox.Bind(wx.EVT_CHECKBOX,event)
			self._setFace(hCheckBox,mode=SKIP_COLOUR)
			hSizer.Add(hCheckBox)
			Add(self.sizer,hPanel,proportion,sizerFlag,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			return hCheckBox
		elif (isinstance(text,list)):	#複数同時作成
			hCheckBoxes=[]
			for s in text:
				hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s,size=(x,-1),style=style)
				hCheckBox.SetValue(state)
				hCheckBox.Bind(wx.EVT_CHECKBOX,event)
				self._setFace(hCheckBox,mode=SKIP_COLOUR)
				hSizer.Add(hCheckBox)
				hCheckBoxes.append(hCheckBox)
			Add(self.sizer,hPanel,proportion,sizerFlag,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			return hCheckBoxes
		else:
			raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

	# 3stateチェックボックス
	def checkbox3(self,text, event=None, state=None, style=0, x=-1, sizerFlag=0, proportion=0):
		hPanel=wx.Panel(self.parent,wx.ID_ANY)
		self._setFace(hPanel)
		hSizer=self.BoxSizer(hPanel,self.sizer.GetOrientation())

		if (isinstance(text,str)):	#単純に一つを作成
			if (state==None):
				state=wx.CHK_UNCHECKED
			hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=text, name=text,style=wx.CHK_3STATE | style,size=(x,0))
			hCheckBox.Set3StateValue(state)
			if state==wx.CHK_UNDETERMINED:
				hCheckBox.SetWindowStyleFlag(wx.CHK_ALLOW_3RD_STATE_FOR_USER)
			hCheckBox.Bind(wx.EVT_CHECKBOX,event)
			self._setFace(hCheckBox,mode=SKIP_COLOUR)
			hSizer.Add(hCheckBox)
			self.AddSpace()
			Add(self.sizer,hPanel,proportion,sizerFlag,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			return hCheckBox
		elif (isinstance(text,list)):	#複数同時作成
			hCheckBoxes=[]
			for i,s in enumerate(text):
				if (state==None):
					hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s,style=wx.CHK_3STATE | style,size=(x,0))
				elif (state[i]==wx.CHK_UNDETERMINED):
					hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s,style=wx.CHK_ALLOW_3RD_STATE_FOR_USER | wx.CHK_3STATE | style,size=(x,0))
					hCheckBox.Set3StateValue(state[i])
				else:
					hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s,style=wx.CHK_3STATE | style,size=(x,0))
					hCheckBox.Set3StateValue(state[i])
				hCheckBox.Bind(wx.EVT_CHECKBOX,event)
				self._setFace(hCheckBox,mode=SKIP_COLOUR)
				hSizer.Add(hCheckBox)
				hCheckBoxes.append(hCheckBox)
			Add(self.sizer,hPanel,proportion,sizerFlag,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			self.AddSpace()
			return hCheckBoxes
		else:
			raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

	def radiobox(self,text, items, event=None, dimension=0, orient=wx.VERTICAL, style=0, x=-1, sizerFlag=0, proportion=0):
		if orient==wx.VERTICAL:
			style=wx.RA_SPECIFY_COLS | style
		else:
			style=wx.RA_SPECIFY_ROWS | style
		hRadioBox=wx.RadioBox(self.parent,label=text, name=text, choices=items,majorDimension=dimension,style=style,size=(x,-1))
		hRadioBox.Bind(wx.EVT_RADIOBOX,event)
		self._setFace(hRadioBox)

		#ラジオボタンのウィンドウハンドルを使ってテーマを無効に変更する
		ptr=viewHelper.findRadioButtons(self.parent.GetHandle())
		s=ctypes.c_char_p(ptr).value.decode("UTF-8").split(",")
		for elem in s:
			_winxptheme.SetWindowTheme(int(elem),"","")
		viewHelper.releasePtr(ptr)

		Add(self.sizer,hRadioBox,proportion,sizerFlag)
		self.AddSpace()
		return hRadioBox

	def listbox(self,text, choices=[], event=None, state=-1, style=0, size=(-1,-1), sizerFlag=wx.ALL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		hListBox=wx.ListBox(self.parent,wx.ID_ANY,name=text,choices=choices,size=size,style=style)
		hListBox.Bind(wx.EVT_LISTBOX,event)
		hListBox.SetSelection(state)
		self._setFace(hListBox)
		Add(sizer,hListBox,proportion,sizerFlag)
		self.AddSpace()
		sizer.Layout()
		return hListBox,hStaticText

	def listCtrl(self,text, event=None, style=0, size=(-1,-1), sizerFlag=wx.ALL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout,sizerFlag, proportion)

		hListCtrl=wx.ListCtrl(self.parent,wx.ID_ANY,style=style,size=size)
		hListCtrl.Bind(wx.EVT_LIST_ITEM_FOCUSED,event)
		self._setFace(hListCtrl)
		self._setFace(hListCtrl.GetMainWindow())
		#_winxptheme.SetWindowTheme(win32api.SendMessage(hListCtrl.GetHandle(),0x101F,0,0),"","")#ヘッダーのウィンドウテーマを引っぺがす
		Add(sizer,hListCtrl,proportion,sizerFlag)
		self.AddSpace()
		return hListCtrl,hStaticText

	def tabCtrl(self,title, event=None, style=wx.NB_NOPAGETHEME | wx.NB_MULTILINE, sizerFlag=0, proportion=0):
		htab=wx.Notebook(self.parent, wx.ID_ANY,name=title,style=style)
		htab.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,event)
		self._setFace(htab)
		Add(self.sizer,htab,proportion,sizerFlag,expandFlag=wx.HORIZONTAL)
		self.sizer.Layout()
		return htab

	def inputbox(self,text, event=None, defaultValue="", style=0, x=0, sizerFlag=wx.ALL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		hTextCtrl=TextCtrl(self.parent, wx.ID_ANY,size=(x,-1),name=text,value=defaultValue,style=style | wx.BORDER_RAISED)
		hTextCtrl.Bind(wx.EVT_TEXT,event)
		self._setFace(hTextCtrl)
		if x==-1:
			Add(sizer,hTextCtrl,proportion,sizerFlag,expandFlag=wx.HORIZONTAL)
		else:
			Add(sizer,hTextCtrl,proportion,sizerFlag)
		self.AddSpace()
		return hTextCtrl,hStaticText

	def gauge(self,text,max=0,defaultValue=0,style=wx.GA_HORIZONTAL | wx.GA_SMOOTH,x=-1,sizerFlag=wx.ALL,proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		hGauge=wx.Gauge(self.parent, wx.ID_ANY, size=(x,-1), style=style,name=text,)
		self._setFace(hGauge)
		if x==-1:
			Add(sizer,hGauge,proportion,sizerFlag,expandFlag=wx.HORIZONTAL)
		else:
			Add(sizer,hGauge,proportion,sizerFlag)
		self.AddSpace()
		return hGauge,hStaticText

	def spinCtrl(self,text, min=0, max=100, event=None, defaultValue=0, style=wx.SP_ARROW_KEYS, x=-1, sizerFlag=wx.ALL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		hSpinCtrl = wx.SpinCtrl(self.parent, wx.ID_ANY, min=min, max=max, initial=defaultValue, style=wx.BORDER_RAISED | style, size=(x,-1))
		hSpinCtrl.Bind(wx.EVT_TEXT,event)
		self._setFace(hSpinCtrl)
		Add(sizer,hSpinCtrl,proportion,sizerFlag,5)
		self.AddSpace()
		return hSpinCtrl,hStaticText

	def slider(self,text, min=0, max=100, event=None, defaultValue=0, style=0, x=-1, sizerFlag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, proportion=0,textLayout=wx.DEFAULT):
		hStaticText,sizer=self._addDescriptionText(text,textLayout)

		hSlider=wx.Slider(self.parent, wx.ID_ANY, size=(x,-1),value=defaultValue, minValue=min, maxValue=max, style=style)
		hSlider.Bind(wx.EVT_SCROLL_CHANGED,event)
		self._setFace(hSlider)
		if x==-1:	#幅を拡張
			Add(sizer,hSlider,proportion,sizerFlag,expandFlag=wx.HORIZONTAL)
		else:
			Add(sizer,hSlider,proportion,sizerFlag)
		self.AddSpace()
		return hSlider,hStaticText

	"""
	def webView(self):
		wx.html2.WebView.MSWSetEmulationLevel(wx.html2.WEBVIEWIE_EMU_IE11_FORCE)
		web=wx.html2.WebView.New(self.parent,size=(800,600))
		Add(self.sizer,web,0)
		return web
	"""

	"""
	def timepicker(self,defaultValue=wx.DateTime.Now()):
		hTimePicker=wx.adv.TimePickerCtrl(self.parent,-1)
		hTimePicker.SetValue(defaultValue)
		#self._setFace(hTimePicker)
		Add(self.sizer,hTimePicker)
		self.AddSpace(self.space)
		return hTimePicker

	#PCTKはおかしい。NVDAは読まない。非推奨。
	def datepicker(self,defaultValue=wx.DateTime.Now()):
		hDatePicker=wx.adv.DatePickerCtrl(self.parent,-1)
		hDatePicker.SetValue(defaultValue)
		self._setFace(hDatePicker)
		Add(self.sizer,hDatePicker)
		self.AddSpace(self.space)
		return hDatePicker

	#PCTKは読まない。NVDAは知らない。非推奨
	def calendar(self,defaultValue=wx.DateTime.Now()):
		hCalendar=wx.adv.CalendarCtrl(self.parent,-1,defaultValue)
		self._setFace(hCalendar)
		Add(self.sizer,hCalendar)
		self.AddSpace(self.space)
		return hCalendar
	"""


	def GetPanel(self):
		return self.parent

	def GetSizer(self):
		return self.sizer

	def _addDescriptionText(self,text,textLayout,sizerFlag=0, proportion=0):
		if textLayout not in (None,wx.HORIZONTAL,wx.VERTICAL,wx.DEFAULT):
			raise ValueError("textLayout must be (None,wx.HORIZONTAL,wx.VIRTICAL,wx.DEFAULT)")
		if textLayout!=None:
			hStaticText=wx.StaticText(self.parent,wx.ID_ANY,label=text,name=text)
		else:
			hStaticText=wx.StaticText(self.parent,wx.ID_ANY,label=text,name=text,size=(0,0))
		self._setFace(hStaticText)
		if type(self.sizer) in (wx.BoxSizer,wx.StaticBoxSizer) and textLayout not in (None,self.sizer.GetOrientation(),wx.DEFAULT):
			sizer=self.BoxSizer(self.sizer,orient=textLayout, space=self.space)
			Add(sizer,hStaticText, 0, wx.ALIGN_CENTER_VERTICAL)
			Add(self.sizer,sizer, proportion, sizerFlag)
			return hStaticText,sizer
		else:
			Add(self.sizer,hStaticText,0,wx.ALIGN_CENTER_VERTICAL)
			return hStaticText,self.sizer

	def _setFace(self,target,mode=NORMAL):
		if mode==NORMAL:
			if self.mode==MODE_DARK:
				target.SetBackgroundColour("#000000")		#背景色＝黒
				target.SetForegroundColour("#ffffff")		#文字色＝白
			else:
				target.SetBackgroundColour("#ffffff")		#背景色＝白
				target.SetForegroundColour("#000000")		#文字色＝黒
		elif (mode==BUTTON_COLOUR):
			if self.mode==MODE_DARK:
				target.SetBackgroundColour("#444444")		#背景色＝灰色
				target.SetForegroundColour("#ffffff")		#文字色＝白
		#end skip
		target.SetThemeEnabled(False)
		_winxptheme.SetWindowTheme(target.GetHandle(),"","")
		target.SetFont(self.font.GetFont())


#parentで指定したsizerの下に、新たなBoxSizerを設置
def BoxSizer(parent,orient=wx.VERTICAL,flg=0,border=0):
	sizer=wx.BoxSizer(orient)
	if (parent!=None):
		parent.Add(sizer,0,flg,border)
	return sizer

def Add(sizer, window, proportion=0, flag=0, border=0, expandFlag=None):
	if isinstance(sizer,wx.BoxSizer):
		if sizer.Orientation==wx.VERTICAL:
			for i in (wx.ALIGN_TOP , wx.ALIGN_BOTTOM , wx.ALIGN_CENTER_VERTICAL):
				if flag&i==i:flag-=i
		else:
			for i in (wx.ALIGN_LEFT , wx.ALIGN_RIGHT , wx.ALIGN_CENTER_HORIZONTAL , wx.ALIGN_CENTER):
				if flag&i==i:flag-=i
	if expandFlag==wx.HORIZONTAL:	#幅を拡張
		if type(sizer) in (wx.BoxSizer,wx.StaticBoxSizer) and sizer.GetOrientation()==wx.VERTICAL:
			sizer.Add(window,proportion,flag | wx.EXPAND, border)
		else:
			sizer.Add(window,1,flag,border)
	else:
		sizer.Add(window,proportion,flag,border)

# parentで指定されたフレームにパネルを設置する
def makePanel(parent):
	hPanel=wx.Panel(parent,wx.ID_ANY)
	return hPanel


class TextCtrl(wx.TextCtrl):
	def AcceptsFocusFromKeyboard(self):
		return True
