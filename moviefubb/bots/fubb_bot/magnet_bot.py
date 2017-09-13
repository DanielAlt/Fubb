#!/usr/env/lib python
import urllib2
from HTMLParser import HTMLParser

class Parser(HTMLParser):
	urls = []
	def handle_starttag(self, tag, attrs):
		if (tag == "a"):
			for attr in attrs:
				if (attr[0] == 'href') and ("magnet:?" in attr[1]):
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
		
	def formatQuery(self):
		full_url = "https://thepiratebay.se/search/"
		name = self.title
		name = name.strip("./,;'\|}{][-_+=!@#$%^&*()<>")
		name = name.replace("'", "%27")
		name = name.split(" ")
		name = "%20".join(name)
		full_url += name + '/0/99/0'
		return (full_url)

	def run(self):
		query = self.formatQuery()
		req = self.opener.open(query)
		decoded_html = req.read().decode('utf-8')
		self.parser.feed(decoded_html)
		urls = self.parser.getURLS()
		self.parser.clearURLS()
		try:
			magnet = urls[0]
		except IndexError:
			magnet = "Undetermined"

		return(magnet)