#!/usr/env/lib python
import urllib2
from HTMLParser import HTMLParser

class Parser(HTMLParser):
	urls = []
	def handle_starttag(self, tag, attrs):
		if (tag == "a"):
			for attr in attrs:
				if (attr[0] == 'href') and ("/title/" in attr[1]):
					self.urls.append(str(attr[1]))

	def handle_endtag(self, tag):
		pass

	def handle_datas(self, data):
		pass
	
	def getURLS(self):
		return self.urls

	def clearURLS(self):
		self.urls = []

class LookupHandler():
	def __init__(self, title):
		self.opener = urllib2.build_opener()
		self.opener.addheaders = [('User-agent', 'Mozilla/5.0')]
		self.parser = Parser()
		self.parser.clearURLS()
		self.title = title
		print "\tIMDB Bot: Initialized"
		
	def formatQuery(self):
		full_url = "http://www.imdb.com/find?ref_=nv_sr_fn&q="
		name = self.title
		name = name.strip("./,;'\|}{][-_+=!@#$%^&*()<>")
		name = name.replace("'", "%27")
		name = name.split(" ")
		name = "+".join(name)
		full_url += name + "&s=all"
		print "\tIMDB Bot: Formatted Query - %s" % full_url
		return (full_url)

	def run(self):
		print "\tIMDB Bot: Running "
		query = self.formatQuery()
		
		try:
			req = self.opener.open(query)
			decoded_html = req.read().decode('utf-8')
			self.parser.feed(decoded_html)
			urls = self.parser.getURLS()
		except urllib2.URLError:
			pass

		self.parser.clearURLS()
		imdb_id = None

		try:
			imdb_url = urls[0]
			imdb_id = imdb_url[imdb_url.find('/title/')+7:imdb_url.find('/?')]
			print "\tIMDB Bot: Found ID - %s " % (imdb_id)
			
		except IndexError:
			imdb_id = None
			print "\tIMDB BOT: No ID Found"
		
		return (imdb_id)