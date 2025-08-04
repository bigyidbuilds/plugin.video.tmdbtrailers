#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import _jsonfiles
from . import _xbmc

class File_Paths():
	"""docstring for File_Paths"""
	def __init__(self,base_file):
		self.base_file = base_file
		self.file_data = _jsonfiles.ReadJsonFile(base_file,keys=['files'])
		for file in self.file_data:
			filepath = file.get('filepath')
			path_dict = _jsonfiles.ReadJsonFile(self.base_file,keys=['paths']).get(filepath)
			filename = file.get('filename')
			folders = path_dict.get('path_dirs')
			ext = file.get('ext')
			path = _xbmc._joinPath(path_dict.get('path_base'),folders=folders,file_name=filename,file_ext=ext)
			code_string  = f"self.{filename}=r'{path}'"
			exec(code_string)





