# -*- coding: UTF-8 -*-

import ctypes
import os

#BASS_ChannelSetAttribute
BASS_ATTRIB_REVERSE_DIR = 0x11000
BASS_ATTRIB_TEMPO = 0x10000
BASS_ATTRIB_TEMPO_PITCH = 0x10001
BASS_ATTRIB_TEMPO_FREQ = 0x10002


#Flags of CreateStream
BASS_FX_FREESOURCE = 0x10000

# BASS_ATTRIB_REVERSE_DIR��Playback direction�Ŏg���ݒ�l
BASS_FX_RVS_REVERSE = -1.0
BASS_FX_RVS_FORWARD = 1.0

func_type = ctypes.WINFUNCTYPE
bass_module = ctypes.WinDLL(os.path.split(__file__)[0]+'\\bass_fx')
BASS_FX_GetVersion = func_type(ctypes.c_ulong)(('BASS_FX_GetVersion', bass_module))
BASS_FX_ReverseCreate=func_type(ctypes.c_ulong,ctypes.c_ulong,ctypes.c_float,ctypes.c_ulong)(('BASS_FX_ReverseCreate', bass_module))
BASS_FX_TempoCreate=func_type(ctypes.c_ulong,ctypes.c_ulong,ctypes.c_ulong)(('BASS_FX_TempoCreate', bass_module))
BASS_FX_ReverseGetSource=func_type(ctypes.c_ulong,ctypes.c_ulong)(('BASS_FX_ReverseGetSource', bass_module))
