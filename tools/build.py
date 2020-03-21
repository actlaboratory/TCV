# -*- coding: utf-8 -*-
#app build tool
#Copyright (C) 2019 Yukio Nozawa <personal@nyanchangames.com>
import os
import sys
import subprocess
import shutil
import distutils.dir_util

def runcmd(cmd):
	proc=subprocess.Popen(cmd.split(), shell=True, stdout=1, stderr=2)
	proc.communicate()

if not os.path.exists("locale"):
	print("Error: no locale folder found. Your working directory must be the root of the project. You shouldn't cd to tools and run this script.")

if os.path.isdir("dist\\TCV"):
	print("Clearling previous build...")
	shutil.rmtree("dist\\")

print("Building...")
runcmd("pyinstaller --windowed --log-level=ERROR TCV.py")
shutil.copytree("locale\\","dist\\TCV\\locale", ignore=shutil.ignore_patterns("*.po", "*.pot", "*.po~"))
print("Done!")
