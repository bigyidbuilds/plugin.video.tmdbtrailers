# plugin.video.tmdbtrailers

## RunPlugin methods
 
### Sample of paths
1.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=user_detatils```
2.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=favorite_add&media_type=movie&tmdbid=10000```
3.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=favorite_remove&media_type=tv&tmbid=2000```
4.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=watchlist_add&media_type=movie&tmdbid=10000```
5.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=watchlist_remove&media_type=tv&tmbid=2000```
6.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=rate&media_type=movie&tmdbid=123456&rating=8.7)```
7.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=unrate&media_type=tv&tmdbid=654321)```
8.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=clear_list&list_id=1234)```
9.  ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&action=delete_list&list_id=1234)```
10. ```RunPlugin(plugin://plugin.video.tmdbtrailers/?mode=account&&action=delete_listitem&list_id=1234&tmdbid=123456)```


### sys.argv

### mode 
	mode = account

### action
available actions:

|user_details: |Pulls account details from TMDB and sets relative settings
|sigin: |sign in and create session id
|signout: |sign out and delete session id
|favorite_add: |required params media_type(movie or tv),tmdbid(id of tmdb media)
|favorite_remove: |required params media_type(movie or tv),tmdbid(id of tmdb media)
|watchlist_add: |required params media_type(movie or tv),tmdbid(id of tmdb media)
|watchlist_remove: |required params media_type(movie or tv),tmdbid(id of tmdb media)
|rate: |required params media_type(movie or tv),tmdbid(id of tmdb media),rating(0-10 value as float 1 decimal place value must be dividable by 0.5 or '###' will call xbmc ui to enter a valve )
|unrate: |required params media_type(movie or tv),tmdbid(id of tmdb media)
|clear_list: |required params list_id (id of list)
|delete_list: |required params list_id (id of list)
|delete_listitem: |required params list_id(id of list), tmdbid(id of tmdb media)