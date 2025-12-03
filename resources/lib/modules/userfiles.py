#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . _jsonfiles import ReadJsonFile,WriteJsonFile
from ._xbmc import _joinPath,CheckCreateFile,CheckCreatePath


def RequiredFiles(config_file):
	data = ReadJsonFile(config_file)
	paths = data.get('paths')
	files = data.get('files') 
	for f in files:
		filepath  = f.get('filepath')
		filepath  = paths.get(filepath)
		filepath  = _joinPath(filepath.get('path_base'),folders=filepath.get('path_dirs'))
		filename  = f.get('filename')
		fileext   = f.get('ext')
		base_dict = f.get('base_dict')
		exists,created = CheckCreateFile(filepath,filename,fileext)
		if exists and  created:
			WriteJsonFile(_xbmc._joinPath(filepath,file_name=filename,file_ext=fileext),base_dict)

		
def RequiredDirs(config_file):
	dirs = ReadJsonFile(config_file,keys=['paths'])
	for k,v in dirs.items():
		CheckCreatePath(v.get('path_base'),folders=v.get('path_dirs'))