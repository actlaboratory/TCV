# -*- coding: utf-8 -*-
#View Creator
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import wx
import _winxptheme
import wx.adv
import ctypes
from . import fontManager

viewHelper=ctypes.cdll.LoadLibrary("viewHelper.dll")

NORMAL=0
BUTTON_COLOUR=1
SKIP_COLOUR=2

GridSizer = -1
FlexGridSizer = -2

class ViewCreator():

	# mode=1で白黒反転。その他は白。
	def __init__(self,mode,parent,parentSizer=None,orient=wx.HORIZONTAL,space=0,label="",style=0):
		self.mode=mode
		self.parent=parent
		self.font=fontManager.FontManager()

		self.SetFace(parent)
		if orient==FlexGridSizer:
			self.sizer=self.FlexGridSizer(parentSizer,space,style)
			self.sizer.SetHGap(space)
			self.sizer.SetVGap(space)
		elif orient==GridSizer:
			self.sizer=self.GridSizer(parentSizer,space,style)
			self.sizer.SetHGap(space)
			self.sizer.SetVGap(space)
		else:
			self.sizer=self.BoxSizer(parentSizer,orient,label,space,style)
		self.space=space
		self.AddSpace(self.space)

	def AddSpace(self,space=-1):
		if self.sizer.__class__==wx.BoxSizer or self.sizer.__class__==wx.StaticBoxSizer:
			if space==-1:
				space==self.space
			self.sizer.AddSpacer(space)

	#parentで指定したsizerの下に、新たなsizerを設置
	def BoxSizer(self,parent,orient=wx.VERTICAL,label="",space=0,style=0):
		if label=="":
			sizer=wx.BoxSizer(orient)
		else:
			sizer=wx.StaticBoxSizer(orient,self.parent,label)
			self.SetFace(sizer.GetStaticBox())
		if (parent.__class__==wx.Panel or parent.__class__==wx.Window):
			parent.SetSizer(sizer)
		elif (parent==None):
			self.parent.SetSizer(sizer)
		else:
			parent.Add(sizer,0,wx.ALL | style,space)
		return sizer

	def GridSizer(self,parent,space=0,style=0):
		sizer=wx.GridSizer(2)
		if (parent.__class__==wx.Panel or parent.__class__==wx.Window):
			parent.SetSizer(sizer)
		elif (parent==None):
			self.parent.SetSizer(sizer)
		else:
			parent.Add(sizer,0,wx.ALL | style,space)
		return sizer


	def FlexGridSizer(self,parent,space=0,style=0):
		sizer=wx.FlexGridSizer(2)
		if (parent.__class__==wx.Panel or parent.__class__==wx.Window):
			parent.SetSizer(sizer)
		elif (parent==None):
			self.parent.SetSizer(sizer)
		else:
			parent.Add(sizer,0,wx.ALL | style,space)
		return sizer

	def button(self,text,event,layout=0):
		hButton=wx.Button(self.parent, wx.ID_ANY,label=text, name=text)
		hButton.Bind(wx.EVT_BUTTON,event)
		self.SetFace(hButton,mode=BUTTON_COLOUR)
		self.sizer.Add(hButton,0,layout)
		self.AddSpace(self.space)
		return hButton

	def okbutton(self,text,event):
		hButton=wx.Button(self.parent, wx.ID_OK,label=text, name=text,style=wx.BORDER_SUNKEN)
		hButton.Bind(wx.EVT_BUTTON,event)
		self.SetFace(hButton,mode=BUTTON_COLOUR)
		self.sizer.Add(hButton,1,wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL,5)
		hButton.SetDefault()
		self.AddSpace(self.space)
		return hButton

	def cancelbutton(self,text,event):
		hButton=wx.Button(self.parent, wx.ID_CANCEL,label=text, name=text)
		hButton.Bind(wx.EVT_BUTTON,event)
		self.SetFace(hButton,mode=BUTTON_COLOUR)
		self.sizer.Add(hButton,1,wx.ALIGN_BOTTOM | wx.ALIGN_RIGHT | wx.ALL,5)
		self.AddSpace(self.space)
		return hButton

	def combobox(self,text,selection,event,state=-1):
		hStaticText=wx.StaticText(self.parent,-1,label=text,name=text)
		self.sizer.Add(hStaticText,0,wx.ALIGN_CENTER_VERTICAL)

		v=""
		if state>=0:
			v=selection[state]
		hCombo=wx.ComboBox(self.parent,wx.ID_ANY,value=v,choices=selection,style=wx.CB_READONLY,name=text)
		hCombo.Bind(wx.EVT_TEXT,event)
		self.SetFace(hCombo)
		self.sizer.Add(hCombo,0,wx.ALL,5)
		self.AddSpace(self.space)
		return hCombo

	def checkbox(self,text,event,state=False):
		hPanel=wx.Panel(self.parent,wx.ID_ANY,)
		hSizer=self.BoxSizer(hPanel,self.sizer.GetOrientation())

		if (isinstance(text,str)):	#単純に一つを作成
			hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=text, name=text)
			hCheckBox.SetValue(state)
			hCheckBox.Bind(wx.EVT_CHECKBOX,event)
			self.SetFace(hCheckBox,mode=SKIP_COLOUR)
			hSizer.Add(hCheckBox)
			self.sizer.Add(hPanel,0,wx.BOTTOM | wx.LEFT | wx.RIGHT,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			return hCheckBox
		elif (isinstance(text,list)):	#複数同時作成
			hCheckBoxes=[]
			for s in text:
				hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s)
				hCheckBox.SetValue(state)
				hCheckBox.Bind(wx.EVT_CHECKBOX,event)
				self.SetFace(hCheckBox,mode=SKIP_COLOUR)
				hSizer.Add(hCheckBox)
				hCheckBoxes.append(hCheckBox)
			self.sizer.Add(hPanel,0,wx.BOTTOM | wx.LEFT | wx.RIGHT,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			return hCheckBoxes
		else:
			raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

	# 3stateチェックボックスの生成
	def checkbox3(self,text,event,state=None):
		hPanel=wx.Panel(self.parent,wx.ID_ANY,)
		hSizer=self.BoxSizer(hPanel,self.sizer.GetOrientation())

		if (isinstance(text,str)):	#単純に一つを作成
			if (state==None):
				state=wx.CHK_UNCHECKED
			hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=text, name=text,style=wx.CHK_3STATE)
			hCheckBox.Set3StateValue(state)
			if state==wx.CHK_UNDETERMINED:
				hCheckBox.SetWindowStyleFlag(wx.CHK_ALLOW_3RD_STATE_FOR_USER)
			hCheckBox.Bind(wx.EVT_CHECKBOX,event)
			self.SetFace(hCheckBox,mode=SKIP_COLOUR)
			hSizer.Add(hCheckBox)
			self.AddSpace(self.space)
			self.sizer.Add(hPanel,0,wx.BOTTOM | wx.LEFT | wx.RIGHT,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			return hCheckBox
		elif (isinstance(text,list)):	#複数同時作成
			hCheckBoxes=[]
			for i,s in enumerate(text):
				if (state==None):
					hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s)
				elif (state[i]==wx.CHK_UNDETERMINED):
					hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s,style=wx.CHK_ALLOW_3RD_STATE_FOR_USER | wx.CHK_3STATE)
					hCheckBox.Set3StateValue(state[i])
				else:
					hCheckBox=wx.CheckBox(hPanel,wx.ID_ANY, label=s, name=s)
					hCheckBox.Set3StateValue(state[i])
				hCheckBox.Bind(wx.EVT_CHECKBOX,event)
				self.SetFace(hCheckBox,mode=SKIP_COLOUR)
				hSizer.Add(hCheckBox)
				hCheckBoxes.append(hCheckBox)
			self.sizer.Add(hPanel,0,wx.BOTTOM | wx.LEFT | wx.RIGHT,self.space)
			viewHelper.ScCheckbox(hPanel.GetHandle())
			self.AddSpace()
			return hCheckBoxes
		else:
			raise ValueError("ViewCreatorはCheckboxの作成に際し正しくない型の値を受け取りました。")

	def radiobox(self,text,items,event,dimension=0,orient=wx.VERTICAL):
		if orient==wx.VERTICAL:
			style=wx.RA_SPECIFY_COLS
		else:
			style=wx.RA_SPECIFY_ROWS
		hRadioBox=wx.RadioBox(self.parent,label=text, name=text, choices=items,majorDimension=dimension,style=style)
		hRadioBox.Bind(wx.EVT_RADIOBOX,event)
		self.SetFace(hRadioBox)

		#ラジオボタンのウィンドウハンドルを使ってテーマを無効に変更する
		ptr=viewHelper.findRadioButtons(self.parent.GetHandle())
		s=ctypes.c_char_p(ptr).value.decode("UTF-8").split(",")
		for elem in s:
			_winxptheme.SetWindowTheme(int(elem),"","")
		viewHelper.releasePtr(ptr)

		self.sizer.Add(hRadioBox)
		self.AddSpace(self.space)
		return hRadioBox

	def ListCtrl(self,proportion,sizerFlag,**settings):
		hListCtrl=wx.ListCtrl(self.parent,wx.ID_ANY,**settings)
		self.SetFace(hListCtrl)
		self.sizer.Add(hListCtrl,proportion,sizerFlag)
		self.AddSpace(self.space)
		return hListCtrl

	def tabCtrl(self,title,event=None,style=wx.NB_NOPAGETHEME | wx.NB_MULTILINE,proportion=0,sizerFlag=0):
		htab=wx.Notebook(self.parent, wx.ID_ANY,name=title,style=style)
		htab.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,event)
		self.SetFace(htab)
		self.sizer.Add(htab,proportion,sizerFlag)
		self.sizer.Layout()
		return htab

	def inputbox(self,text,x=0,defaultValue=""):
		hStaticText=wx.StaticText(self.parent,-1,label=text,name=text)
		self.sizer.Add(hStaticText,0)

		hTextCtrl=wx.TextCtrl(self.parent, -1,size=(x,-1),name=text,value=defaultValue)
		self.SetFace(hTextCtrl)
		if x==-1:	#幅を拡張
			self.sizer.Add(hTextCtrl,1)
		else:
			self.sizer.Add(hTextCtrl)
		self.AddSpace(self.space)
		return hTextCtrl,hStaticText

	def timepicker(self,defaultValue=wx.DateTime.Now()):
		hTimePicker=wx.adv.TimePickerCtrl(self.parent,-1)
		hTimePicker.SetValue(defaultValue)
		#self.SetFace(hTimePicker)
		self.sizer.Add(hTimePicker)
		self.AddSpace(self.space)
		return hTimePicker

	#PCTKはおかしい。NVDAは読まない。非推奨。
	def datepicker(self,defaultValue=wx.DateTime.Now()):
		hDatePicker=wx.adv.DatePickerCtrl(self.parent,-1)
		hDatePicker.SetValue(defaultValue)
		self.SetFace(hDatePicker)
		self.sizer.Add(hDatePicker)
		self.AddSpace(self.space)
		return hDatePicker

	#PCTKは読まない。NVDAは知らない。非推奨
	def calendar(self,defaultValue=wx.DateTime.Now()):
		hCalendar=wx.adv.CalendarCtrl(self.parent,-1,defaultValue)
		self.SetFace(hCalendar)
		self.sizer.Add(hCalendar)
		self.AddSpace(self.space)
		return hCalendar



	def GetPanel(self):
		return self.parent

	def GetSizer(self):
		return self.sizer

	def SetFace(self,target,mode=NORMAL):
		if mode==NORMAL:
			if self.mode==1:
				target.SetBackgroundColour("#000000")		#背景色＝黒
				target.SetForegroundColour("#ffffff")		#文字色＝白
			else:
				target.SetBackgroundColour("#ffffff")		#背景色＝白
				target.SetForegroundColour("#000000")		#文字色＝黒
		elif (mode==BUTTON_COLOUR):
			if self.mode==1:
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


# parentで指定されたフレームにパネルを設置する
# modeはViewCreator.__init__と同様
def makePanel(parent):
	hPanel=wx.Panel(parent,wx.ID_ANY)
	return hPanel




"""
	ラジオボタン関連サンプルコード
	https://www.python-izm.com/gui/wxpython/wxpython_radiobox/

"""