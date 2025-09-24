#!/usr/bin/python3
# -*- coding: utf-8 -*-


import xbmcgui

from resources.lib.modules import _xbmc

__addon__ = 'plugin.video.tmdbtrailers'

class _RateSlider(xbmcgui.WindowXMLDialog):
	"""
	docstring for RateSlider
	"""

	ACTION_PREVIOUS_MENU = 10
	ACTION_NAV_BACK = 92

	HEADER_LABEL = 1002
	CLOSE_BUTTON = 1004
	SLIDERCONTROL = 2001
	RATE_BUTTON = 3001
	CANCEL_BUTTON = 3002
	

	def __new__(cls,media_title):
		return super(_RateSlider, cls).__new__(cls,'Rate_slider.xml',_xbmc._AddonInfo(__addon__,'path'),'Default', '1080i')

	def __init__(self,media_title):
		super().__init__()
		self.rating = None
		self.media_title = _xbmc._AddonLocalStr(__addon__,32076).format(name=media_title)


	def onInit(self):
		self.SetSliderValues()
		self.SetLabel(f'[B]{self.media_title}[/B]')


	def onClick(self,controlID):
		_xbmc.Log(f'onClick{controlID}')
		if controlID in [self.CANCEL_BUTTON,self.CLOSE_BUTTON]:
			self.Close()
		elif controlID == self.RATE_BUTTON:
			self.GetRating()
			self.Close()


	def onAction(self,actionID):
		actionid = actionID.getId()
		_xbmc.Log(f'onAction {actionid}')
		if actionid in [self.ACTION_PREVIOUS_MENU,self.ACTION_NAV_BACK]:
			self.Close()



	def Close(self):
		super().close()


	def SetSliderValues(self):
		control = self.getControl(self.SLIDERCONTROL)
		control.setFloat(5.0, 0.0,0.5,10.0)

	def GetRating(self):
		control = self.getControl(self.SLIDERCONTROL)
		self.rating = control.getFloat()

	def SetLabel(self,label,control_id):
		control = self.getControl(control_id)
		control.setLabel(label)





def RateSlider(media_title):
	d = _RateSlider(media_title)
	d.doModal()
	rating = d.rating
	del d
	_xbmc.Log(f'rating {rating}')
	return rating
