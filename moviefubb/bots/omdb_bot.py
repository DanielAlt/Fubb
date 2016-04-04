#!/usr/env/lib python
import urllib2, json

class LookupHandler():
	def __init__(self, **kwargs):
		self.args = {
			'title': None,
			'imdbID': None
		}
		for arg in kwargs.keys():
			if arg in self.args.keys():
				self.args.update({arg: kwargs[arg]})
		print "\tInfo Bot Configured"
		self.opener = urllib2.build_opener()
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		print "\tInfo bot initialized"
		
	def formatTitle(self):
		if 'title' in self.args.keys():
			query = str(self.args['title']).split(" ")
			query = "http://www.omdbapi.com/?t=" + "+".join(query) + "&y=&plot=short&r=json"
			print "\tInfo Bot Formated Query: %s" % query
			return (query)

	def formatIMDB(self):
		if 'imdbID' in self.args.keys():
			query = 'http://www.omdbapi.com/?i=' + str(self.args['imdbID']) + '&plot=short&r=json'
			print "\tInfo Bot Formated Query: %s" % query
			return (query)

	def run(self):
		print "\tInfo Bot is Running"

		if self.args['title'] is not None:
			try:
				query = self.formatTitle()
				req = self.opener.open(query)
				print "\tInfo Bot Got JSON"
				vorheese = json.load(req)
				return (vorheese)
			except urllib2.URLError:
				return {'Title': self.args['title']}

		if self.args['imdbID'] is not None:
			try:
				query = self.formatIMDB()
				req = self.opener.open(query)
				print "\tInfo Bot Got JSON"
				vorheese = json.load(req)
				return (vorheese)
			except urllib2.URLError:
				return {'imdbID': self.args['imdbID']}