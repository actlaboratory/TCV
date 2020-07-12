import sys, ctypes, platform, globalVars, os, re

def is64Bit():
	return sys.maxsize > 2 ** 32

#使用環境に応じて適切なdllをロード
if is64Bit():
	from pybass64 import pybass
	from pybass64 import bass_fx
else:
	from pybass import pybass
	from pybass import bass_fx
	from pybass import basshls


class Player():
	def __init__ (self):
		# 必要な変数を生成
		self.fileName = 0
		self.handle = 0
		self.reverseHandle = 0
		self.moveTempo = -30.0
		self.rewindFlag = 0
		self.fastForwardFlag = 0
		self.handleVolume = 1.0
		self.changeVolume(globalVars.app.config.getint("volume", "default", default=100)) #音量読み込み
		self.channelTempo = 0.0
		self.channelPitch = 0
		self.channelSourceFreq = 44100.0
		self.channelFreq = 100
		#bass.dllの初期化
		pybass.BASS_Init(-1, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0)
		pybass.BASS_SetConfig(pybass.BASS_CONFIG_BUFFER,150)
		#必要なプラグインを適用
		pybass.BASS_PluginLoad(b"basshls.dll", 0)

	def inputFile(self, fileName):
		# 以前のストリームがあればフリー
		if not(self.handle == 0 and self.reverseHandle == 0):
			self.channelFree()

		# ファイルが渡されたらファイルを登録してストリームを生成
		self.fileName = fileName
		self.handle, self.reverseHandle = self.createChannel()

		#一部設定を引き継いで再生
		self.refreshEffect()
		self.fastMoveReset()
		rtn = self.channelPlay()
		return rtn

	def createChannel(self):
		#ファイルを読み込み、ストリームを生成
		if os.path.isfile(self.fileName):
			handle = pybass.BASS_StreamCreateFile(False,self.fileName, 0, 0, pybass.BASS_UNICODE | pybass.BASS_STREAM_PRESCAN | pybass.BASS_STREAM_DECODE)
			#逆再生用のストリームを生成。さっきのhandleはこれと同時にfreeする
			reverseHandle = bass_fx.BASS_FX_ReverseCreate(handle,0.3,bass_fx.BASS_FX_FREESOURCE | pybass.BASS_STREAM_DECODE)
			#再生速度をコントロールするストリームを生成。
			handle = bass_fx.BASS_FX_TempoCreate(reverseHandle,0)		#bass_fx.BASS_FX_FREESOURCEしない
			#再生の向きを元の方向に設定
			pybass.BASS_ChannelSetAttribute(reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR,bass_fx.BASS_FX_RVS_FORWARD)
			# サンプリングレートを読み込み
			cFreq = ctypes.c_float()
			pybass.BASS_ChannelGetAttribute(handle, pybass.BASS_ATTRIB_FREQ, cFreq)
			self.channelSourceFreq = round(cFreq.value)
		elif re.search("https?://.+\..+", self.fileName) != None:
			handle = pybass.BASS_StreamCreateURL(self.fileName.encode(), 0, 0, 0, 0)
			reverseHandle = 0
		else:
			handle = 0
			reverseHandle = 0

		#再生ボリュームを初期設定
		pybass.BASS_ChannelSetAttribute(handle, pybass.BASS_ATTRIB_VOL, self.handleVolume)

		#2つのhandleを返す

		return handle,reverseHandle

	def channelPlay(self):
		rtn = pybass.BASS_ChannelPlay(self.handle,False)
		# pybass.play_handle(self.handle, show_tags = True)
		return rtn

	def channelFree(self):
		pybass.BASS_StreamFree(self.reverseHandle)
		self.reverseHandle = 0
		pybass.BASS_StreamFree(self.handle)
		self.handle = 0
		self.fastMoveReset()
		self.fileName = 0

	def pauseChannel(self):
		return pybass.BASS_ChannelPause(self.handle)


	def getChannelState(self):
		bassCode = pybass.BASS_ChannelIsActive(self.handle)
		if bassCode == pybass.BASS_ACTIVE_PLAYING:
			return 0
		elif bassCode == pybass.BASS_ACTIVE_PAUSED:
			return 1
		elif bassCode == pybass.BASS_ACTIVE_PAUSED_DEVICE:
			return 4
		else:
			if self.handle == 0:
				return 3
			else:
				return 2

	def getChannelLength(self):
		byte = pybass.BASS_ChannelGetLength(self.handle,pybass.BASS_POS_BYTE)
		return pybass.BASS_ChannelBytes2Seconds(self.handle, byte)

	def restartDevice(self, device=-1): #オーディオデバイスを設定して再起動
		pos = self.getChannelPosition()
		pybass.BASS_Stop()
		# デバイスの再設定
		if pybass.BASS_Init(device, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0) == False:
			c = 0
			for i in range(1, 100):
				if pybass.BASS_Init(i, 44100, pybass.BASS_DEVICE_CPSPEAKERS, 0, 0):
					c = i
					break
			pybass.BASS_SetDevice(c)
		else:
			pybass.BASS_SetDevice(device)
		self.inputFile(self.fileName)
		return self.setChannelPosition(pos)

	def getChannelPosition(self):
		channelPositionByte = pybass.BASS_ChannelGetPosition(self.handle, pybass.BASS_POS_BYTE)
		channelPositionSec = pybass.BASS_ChannelBytes2Seconds(self.handle, channelPositionByte)
		return channelPositionSec

	def setChannelPosition(self, sec):
		channelPositionByte = pybass.BASS_ChannelSeconds2Bytes(self.handle, sec)
		return pybass.BASS_ChannelSetPosition(self.handle, channelPositionByte, pybass.BASS_POS_BYTE)

	def rewind(self):
		if self.fastForwardFlag == 0 and self.moveTempo < 2000.0 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
			pybass.BASS_ChannelSetAttribute(self.reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR,bass_fx.BASS_FX_RVS_REVERSE)
			if pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,self.moveTempo):
				self.moveTempo += 50.0
				self.rewindFlag = 1
			else:
				self.fastMoveReset()
		elif self.fastForwardFlag == 1 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
			self.fastMoveReset()

	def fastForward(self):
		if self.rewindFlag == 0 and self.moveTempo < 2000.0 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
			if pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,self.moveTempo):
				self.moveTempo += 50.0
				self.fastForwardFlag = 1
			else:
				self.fastMoveReset()
		elif self.rewindFlag == 1 and pybass.BASS_ChannelIsActive(self.handle) == pybass.BASS_ACTIVE_PLAYING:
			self.fastMoveReset()

	def fastMoveReset(self):
		self.moveTempo = -30.0
		self.rewindFlag = 0
		self.fastForwardFlag = 0
		pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,self.channelTempo)
		pybass.BASS_ChannelSetAttribute(self.reverseHandle,bass_fx.BASS_ATTRIB_REVERSE_DIR, bass_fx.BASS_FX_RVS_FORWARD)
		pybass.BASS_ChannelUpdate(self.handle, 0)

	# 再生速度変更（速度%）
	def setTempo(self, tempo):
		self.channelTempo = tempo
		rtn = False
		if tempo >= -95 and tempo <= 5000:
			if pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO,tempo): rtn = True
		return rtn

	# 再生ピッチ変更（ピッチ-60..60）
	def setPitch(self, pitch):
		self.channelPitch = pitch
		rtn = False
		if pitch >= -60 and pitch <= 60:
			if pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO_PITCH,pitch): rtn = True
		return rtn

			# 再生周波数変更（周波数5..5000(%)）
	def setFreq(self, freq):
		self.channelFreq = freq
		rtn = False
		if freq >= 5 and freq <= 5000:
			#pass
			# パーセントから周波数に変換
			freqHz = self.channelSourceFreq * (freq/100)
			if pybass.BASS_ChannelSetAttribute(self.handle,bass_fx.BASS_ATTRIB_TEMPO_FREQ,freqHz): rtn = True
		return rtn

	def refreshEffect(self): # エフェクトリフレッシュ
		self.setTempo(self.channelTempo)
		self.setPitch(self.channelPitch)
		self.setFreq(self.channelFreq)

	# 音量変更（整数%）
	def changeVolume(self, num):
		if num < 0:
			return
		num = num/100
		self.handleVolume = num
		pybass.BASS_ChannelSetAttribute(self.handle, pybass.BASS_ATTRIB_VOL, self.handleVolume)

	def getVolume(self):
		return self.handleVolume*100

class state():
	PLAYING = 0
	PAUSED = 1
	STOPED = 2
	COLD = 3
	PAUSED_DEVICE = 4
