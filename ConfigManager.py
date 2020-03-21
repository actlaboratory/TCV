# -*- coding: utf-8 -*-
#ConfigManager
#Copyright (C) 2019-2020 yamahubuki <itiro.ishino@gmail.com>

import os
import configparser
import logging
from logging import getLogger

class ConfigManager(configparser.ConfigParser):


	def __init__(self):
		super().__init__()
		self.identifier="ConfigManager"
		self.log=getLogger(self.identifier)
		self.log.debug("Create config instance")

	def read(self,fileName):
		self.fileName=fileName
		if os.path.exists(fileName):
			self.log.info("read configFile:"+fileName)
			try:
				return super().read(fileName)
			except configparser.ParsingError:
				self.log.warning("configFile parse failed.")
				return []
		else:
			self.log.warning("configFile not found.")
			return []

	def write(self):
		self.log.info("write configFile:"+self.fileName)
		with open(self.fileName,"w") as f: return super().write(f)

	def __getitem__(self,key):
		try:
			return ConfigSection(super().__getitem__(key))
		except KeyError as e:
			self.log.debug("created new section:"+key)
			self.add_section(key)
			return self.__getitem__(key)

	def getint(self,section,key,default=0):
		try:
			return super().getint(section,key)
		except configparser.NoOptionError as e:
			self.log.debug("add new intval "+str(default)+" at section "+section+", key "+key)
			self[section][key]=str(default)
			return int(default)
		except configparser.NoSectionError as e:
			self.log.debug("add new section and intval "+str(default)+" at section "+section+", key "+key)
			self.add_section(section)
			self.__getitem__(section).__setitem__(key,str(default))
			return int(default)

	def add_section(self,name):
		if not self.has_section(name):
			return super().add_section(name)

class ConfigSection(configparser.SectionProxy):
	def __init__(self,proxy):
		super().__init__(proxy._parser, proxy._name)

	def __getitem__(self,key):
		try:
			return super().__getitem__(key)
		except KeyError:
			self._parser[self._name][key]=""
			return ""

	def __setitem__(self,key,value):
		return super().__setitem__(key,str(value))
