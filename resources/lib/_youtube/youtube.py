#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json

import youtube_registration
import youtube_authentication
import youtube_requests
import youtube_resolver

import xbmcgui

from resources.lib.modules._xbmc import Log

def YouTubeRegistration(addon_id,api_key,client_id,client_secret):
	youtube_registration.register_api_keys(addon_id=addon_id,api_key=api_key,client_id=client_id,client_secret=client_secret)

def YouTubeGetVideos(video_id,addon_id,listitem=True):
	""" 
	params: 
		video_id can be list of youtube video ids or single id
		addod_id is addon id where api keys have been assigned to
		listem if true returns a list of xbmcgui listitem, False returns raw list of dicts
	"""
	videos = youtube_requests.get_videos(video_id=video_id, addon_id=addon_id)
	Log(videos)
	if CheckForError(videos):
		if listitem:
			return ConverttoListItem(videos)
		else:
			return videos
	else:
		return None

def YouTubeSignIn(addon_id):
	signin = youtube_authentication.sign_in(addon_id=addon_id)
	if signin:
		return True
	else:
		return False

def ResolveVideo(video_id,addon_id,listitem=True):
	resolved = youtube_resolver.resolve(video_id, addon_id=addon_id)
	if listitem:
		return ConvertPlayListitem(resolved[0])
	else:
		return resolved

def CheckForError(data):
	if isinstance(data,list):
		data = data[0]
	keys = list(data.keys())
	if keys[0] == 'error':
		error = data.get('error')
		Log(error)
		return False
	else:
		return True



def ConverttoListItem(data):
	items = []
	for d in data:
		snippet = d.get("snippet")
		local = snippet.get("localized")
		li = xbmcgui.ListItem(local.get("title",snippet.get("title")))
		li.setArt({'thumb':snippet.get("thumbnails").get("default").get("url")})
		for k,v in d.items():
			li.setProperty(k,str(v))
		li.setIsFolder(False)
		vi = li.getVideoInfoTag()
		vi.setPlot(local.get("description",snippet.get("description")))
		vi.setPremiered(snippet.get("publishedAt"))
		items.append(li)
	return items

def ConvertPlayListitem(data):
	meta = data.get('meta')
	title = meta.get('title')
	thumbs = meta.get('thumbnails')
	playpath = data.get('url')
	li = xbmcgui.ListItem(title)
	li.setPath(playpath)
	li.setArt({'thumb':thumbs.get('default').get('url')})
	vi = li.getVideoInfoTag()
	vi.setTitle(title)
	vi.setFilenameAndPath(playpath)
	return li

#Error return
'''{
    "error": {
        "code": 400,
        "message": "The request specifies an invalid filter parameter.",
        "errors": [
            {
                "message": "The request specifies an invalid filter parameter.",
                "domain": "youtube.parameter",
                "reason": "invalidFilters",
                "location": "parameters.",
                "locationType": "other"
            }
        ]
    }
}'''

#resolve video return
'''{
    "title": "[B]1080p (FHD)[/B] (mpd / avc1 / mp4a@130) English [en]",
    "url": "http://127.0.0.1:50152/youtube/manifest/dash?file=sVnCrKUsQg0.mpd",
    "meta": {
        "id": "sVnCrKUsQg0",
        "title": "A Working Man | What\u2019s Her Name \u2013 Official Clip",
        "status": {
            "unlisted": false,
            "private": false,
            "crawlable": true,
            "family_safe": false,
            "live": false
        },
        "channel": {
            "id": "UCf5CjDJvsFvtVIhkfmKAwAA",
            "author": "Amazon MGM Studios"
        },
        "thumbnails": {
            "default": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/default.jpg",
                "size": 10800,
                "ratio": 1.3333333333333333
            },
            "medium": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/mqdefault.jpg",
                "size": 57600,
                "ratio": 1.7777777777777777
            },
            "high": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/hqdefault.jpg",
                "size": 172800,
                "ratio": 1.3333333333333333
            },
            "standard": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/sddefault.jpg",
                "size": 307200,
                "ratio": 1.3333333333333333
            },
            "720": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/hq720.jpg",
                "size": 921600,
                "ratio": 1.7777777777777777
            },
            "oar": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/oardefault.jpg",
                "size": 0,
                "ratio": 0
            },
            "maxres": {
                "url": "https://i.ytimg.com/vi/sVnCrKUsQg0/maxresdefault.jpg",
                "size": 2073600,
                "ratio": 1.7777777777777777
            }
        },
        "subtitles": null
    },
    "headers": {
        "User-Agent": "youtube/0.1 (sVnCrKUsQg0)"
    },
    "playback_stats": {
        "playback_url": "",
        "watchtime_url": ""
    },
    "container": "mpd",
    "dash/audio": true,
    "dash/video": true,
    "adaptive": true,
    "sort": [
        9999,
        540.0,
        117.0
    ],
    "audio": {
        "bitrate": 130,
        "codec": "mp4a"
    },
    "video": {
        "height": 1080,
        "codec": "avc1"
    }
}'''
#get video return
'''{
	"kind": "youtube#video",
	"etag": "jIW67DIN7i9ZUAJpR67Lfs7Wsmk",
	"id": "hyEVX-4uK_4",
	"snippet": {
		"publishedAt": "2025-03-26T18:00:38Z",
		"channelId": "UCf5CjDJvsFvtVIhkfmKAwAA",
		"title": "A Working Man | Construction Site Battle \u2013 Official Clip",
		"description": "Watch this exclusive clip from #AWorkingMan and see the movie only in theaters March 28. Get tickets at www.AWorkingManMovie.com\n \nFollow A Working Man on social:\nhttps://www.instagram.com/aworkingmanmovie/\nhttps://www.facebook.com/aworkingmanmovie\n#AWorkingMan\n\nAbout Amazon MGM Studios: Amazon MGM (Metro Goldwyn Mayer) is a leading entertainment company focused on the production and global distribution of film and television content across all platforms. The company owns one of the world\u2019s deepest libraries of premium film and television content as well as the premium pay television network MGM+, which is available throughout the U.S. via cable, satellite, telco and digital distributors.  In addition, Amazon MGM has investments in numerous other television channels, digital platforms and interactive ventures and is producing premium short-form content for distribution. \n\nConnect with MGM Studios Online\nVisit the MGM Studios WEBSITE: http://amazonmgmstudios.com/\nCheck out Amazon MGM on TIKTOK: https://www.tiktok.com/@amazonmgmstudios\nFollow Amazon MGM Studios on INSTAGRAM: https://www.instagram.com/amazonmgmstudios/\nFollow Amazon MGM Studios on TWITTER: https://twitter.com/amazonmgmstudio\nLike Amazon MGM Studios on FACEBOOK: https://www.facebook.com/AmazonMGMStudios\n\nA Working Man | Construction Site Battle \u2013 Official Clip\nhttps://www.youtube.com/@AmazonMGMStudios\n\n#MGM #AWorkingMan #JasonStatham",
		"thumbnails": {
			"default": {
				"url": "https://i.ytimg.com/vi/hyEVX-4uK_4/default.jpg",
				"width": 120,
				"height": 90
			},
			"medium": {
				"url": "https://i.ytimg.com/vi/hyEVX-4uK_4/mqdefault.jpg",
				"width": 320,
				"height": 180
			},
			"high": {
				"url": "https://i.ytimg.com/vi/hyEVX-4uK_4/hqdefault.jpg",
				"width": 480,
				"height": 360
			},
			"standard": {
				"url": "https://i.ytimg.com/vi/hyEVX-4uK_4/sddefault.jpg",
				"width": 640,
				"height": 480
			},
			"maxres": {
				"url": "https://i.ytimg.com/vi/hyEVX-4uK_4/maxresdefault.jpg",
				"width": 1280,
				"height": 720
			}
		},
		"channelTitle": "Amazon MGM Studios",
		"tags": [
			"MGM",
			"MGM Studios",
			"Metro-Goldwyn- Mayer",
			"Metro Pictures Corporations",
			"Goldwyn Pictures",
			"Louis B. Mayer Pictures",
			"MGM Pictures",
			"United Artists",
			"Metro MGM/UA",
			"Amazon MGM",
			"Amazon MGM Studios",
			"Amazon",
			"A Working Man 2025",
			"A Working Man",
			"Jason Statham Movies",
			"Jason Statham",
			"Jason Statham A Working Man",
			"David Harbour",
			"Michael Pe\u00f1a",
			"Jason Flemyng",
			"Arianna Rivas",
			"Noemi Gonzalez",
			"A Working Man Official Clip",
			"A Working Man Clip",
			"Official Clip",
			"A working Man Movie Clip"
		],
		"categoryId": "24",
		"liveBroadcastContent": "none",
		"defaultLanguage": "en",
		"localized": {
			"title": "A Working Man | Construction Site Battle \u2013 Official Clip",
			"description": "Watch this exclusive clip from #AWorkingMan and see the movie only in theaters March 28. Get tickets at www.AWorkingManMovie.com\n \nFollow A Working Man on social:\nhttps://www.instagram.com/aworkingmanmovie/\nhttps://www.facebook.com/aworkingmanmovie\n#AWorkingMan\n\nAbout Amazon MGM Studios: Amazon MGM (Metro Goldwyn Mayer) is a leading entertainment company focused on the production and global distribution of film and television content across all platforms. The company owns one of the world\u2019s deepest libraries of premium film and television content as well as the premium pay television network MGM+, which is available throughout the U.S. via cable, satellite, telco and digital distributors.  In addition, Amazon MGM has investments in numerous other television channels, digital platforms and interactive ventures and is producing premium short-form content for distribution. \n\nConnect with MGM Studios Online\nVisit the MGM Studios WEBSITE: http://amazonmgmstudios.com/\nCheck out Amazon MGM on TIKTOK: https://www.tiktok.com/@amazonmgmstudios\nFollow Amazon MGM Studios on INSTAGRAM: https://www.instagram.com/amazonmgmstudios/\nFollow Amazon MGM Studios on TWITTER: https://twitter.com/amazonmgmstudio\nLike Amazon MGM Studios on FACEBOOK: https://www.facebook.com/AmazonMGMStudios\n\nA Working Man | Construction Site Battle \u2013 Official Clip\nhttps://www.youtube.com/@AmazonMGMStudios\n\n#MGM #AWorkingMan #JasonStatham"
		},
		"defaultAudioLanguage": "en-US"
	},
	"contentDetails": {
		"duration": "PT1M12S",
		"dimension": "2d",
		"definition": "hd",
		"caption": "false",
		"licensedContent": true,
		"contentRating": {},
		"projection": "rectangular"
	},
	"status": {
		"uploadStatus": "processed",
		"privacyStatus": "public",
		"license": "youtube",
		"embeddable": true,
		"publicStatsViewable": true,
		"madeForKids": false
	},
	"statistics": {
		"viewCount": "195447",
		"likeCount": "433",
		"favoriteCount": "0",
		"commentCount": "33"
	}
}'''