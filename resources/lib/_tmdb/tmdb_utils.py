#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import requests
import shutil
from urllib.parse import urlunparse

from resources.lib.modules._xbmc import Log

def TMDB_ImageUrl(path):
	return urlunparse(('https','image.tmdb.org',f't/p/original/{path}',None,None,None))


def TMDB_ArtWorkDownloader(path,destination_file):
	r = requests.get(TMDB_ImageUrl(path),stream=True)
	with open(destination_file, 'wb') as f:
		r.raw.decode_content = True
		shutil.copyfileobj(r.raw, f)




