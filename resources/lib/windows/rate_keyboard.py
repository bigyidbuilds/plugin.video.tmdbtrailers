#!/usr/bin/python3
# -*- coding: utf-8 -*-


import xbmcgui

from resources.lib.modules import _xbmc

__addon__ = 'plugin.video.tmdbtrailers'

class _RateKeyBoard(xbmcgui.WindowXMLDialog):
	"""
	docstring for RateKeyBoard
	"""

	def __new__(cls):
		return super(_RateKeyBoard, cls).__new__(cls,'Rate_keyboard.xml',_xbmc._AddonInfo(__addon__,'path'),'Default', '1080i')

	def __init__(self):
		super().__init__()

	def onInit(self):
		pass








def RateKeyBoard():
	d = _RateKeyBoard()
	d.doModal()
	del d
