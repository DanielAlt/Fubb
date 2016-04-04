#!/usr/env/lib python
import urllib2

class LookupHandler():
	def __init__(self, poster_url):
		self.poster_url = poster_url
		self.opener = urllib2.build_opener()
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		print "\tPoster Bot: Initialized"
		
	def run(self):
		try:
			req = self.opener.open(self.poster_url)
			poster = req.read()
			print "\tPoster Bot: Poster Found"
			return (poster)
		except urllib2.URLError:
			print "\tPoster Bot: Poster Not Found"
			return 'N/A'