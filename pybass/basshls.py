"""
BASSHLS 2.4 C/C++ header file
Copyright (c) 2015-2019 Un4seen Developments Ltd.
See the BASSHLS.CHM file for more detailed documentation
"""

import sys, ctypes, platform
from pybass.pybass import *

if sys.hexversion < 0x02060000:
	ctypes.c_bool = ctypes.c_byte

if platform.system().lower() == 'windows':
	bass_hls_module = ctypes.WinDLL('pybass/basshls')
	func_type = ctypes.WINFUNCTYPE
else:
	# correct by Wasylews (sabov.97@mail.ru), thank him
	bass_hls_module = ctypes.CDLL('./libbass.so', mode=ctypes.RTLD_GLOBAL)
	func_type = ctypes.CFUNCTYPE

QWORD = ctypes.c_int64

def LOBYTE(a): return (ctypes.c_byte)(a)
def HIBYTE(a): return (ctypes.c_byte)((a)>>8)
def LOWORD(a): return (ctypes.c_ushort)(a)
def HIWORD(a): return (ctypes.c_ushort)((a)>>16)
def MAKEWORD(a,b): return (ctypes.c_ushort)(((a)&0xff)|((b)<<8))
def MAKELONG(a,b): return (ctypes.c_ulong)(((a)&0xffff)|((b)<<16))

BASSVERSION = 0x204
BASSVERSIONTEXT = '2.4'

HMUSIC = ctypes.c_ulong		# MOD music handle
HSAMPLE = ctypes.c_ulong    #sample handle
HCHANNEL = ctypes.c_ulong    #playing sample's channel handle
HSTREAM = ctypes.c_ulong    #sample stream handle
HRECORD = ctypes.c_ulong    #recording handle
HSYNC = ctypes.c_ulong    #synchronizer handle
HDSP = ctypes.c_ulong    #DSP handle
HFX = ctypes.c_ulong    #DX8 effect handle
HPLUGIN = ctypes.c_ulong    # Plugin handle


# additional BASS_SetConfig options
BASS_CONFIG_HLS_DOWNLOAD_TAGS = 0x10900
BASS_CONFIG_HLS_BANDWIDTH = 0x10901
BASS_CONFIG_HLS_DELAY = 0x10902

# additional sync type
BASS_SYNC_HLS_SEGMENT = 0x10300

# additional tag types
BASS_TAG_HLS_EXTINF = 0x14000    #segment's EXTINF tag : UTF-8 string
#BASS_TAG_HLS_STREAMINF = 0x14001    #EXT-X-STREAM-INF tag : UTF-8 string
BASS_TAG_HLS_DATE = 0x14002    #EXT-X-PROGRAM-DATE-TIME tag : UTF-8 string

# additional BASS_StreamGetFilePosition mode
BASS_FILEPOS_HLS_SEGMENT = 0x10000    #segment sequence number

#HSTREAM BASSHLSDEF(BASS_HLS_StreamCreateFile)(BOOL mem, const void *file, QWORD offset, QWORD length, DWORD flags);
BASS_HLS_StreamCreateFile = func_type(HSTREAM, ctypes.c_bool, ctypes.c_void_p, QWORD, QWORD, ctypes.c_ulong)(('BASS_HLS_StreamCreateFile', bass_hls_module))

#HSTREAM BASSHLSDEF(BASS_HLS_StreamCreateURL)(const char *url, DWORD flags, DOWNLOADPROC *proc, void *user);
BASS_HLS_StreamCreateURL = func_type(HSTREAM, ctypes.c_char_p, ctypes.c_ulong, ctypes.c_void_p, ctypes.c_void_p)(('BASS_HLS_StreamCreateURL', bass_hls_module))
