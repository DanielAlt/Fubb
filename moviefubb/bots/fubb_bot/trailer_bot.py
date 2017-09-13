import urllib2
from HTMLParser import HTMLParser

class Parser(HTMLParser):
	urls = []
	def handle_starttag(self, tag, attrs):
		if (tag == "a"):
			for attr in attrs:
				if (attr[0] == 'href') and ("/watch" in attr[1]):
					self.urls.append("http://www.youtube.com" + str(attr[1]) )

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
		"\tTrailer Bot: Initialized."
		

	def formatQuery(self):
		full_url = "http://www.youtube.com/results/?search_query="
		name = self.title.strip("./,;'\|}{][-_+=!@#$%^&*()<>")
		name = name.replace("'", "%27")
		name = name.split(" ")
		name.append("trailer")
		name = "+".join(name)
		full_url += name
		print '\tTrailer Bot: Formatted Query - %s' % (full_url) 
		return (full_url)

	def run(self):
		print "Trailer Bot: Running Lookup..."
		query = self.formatQuery()
		try:
			req = self.opener.open(query)
			decoded_html = req.read().decode('utf-8')
			self.parser.feed(decoded_html)
		except UnicodeDecodeError:
			self.parser.feed(req.read())
		except UnicodeEncodeError:
			pass
			
		urls = self.parser.getURLS()
		self.parser.clearURLS()
		try:
			embed = urls[0][urls[0].find('watch?v=')+8:]
			print "Trailer Bot: Found Trailer ID - %s " % (embed)
			return (embed)

		except IndexError, urllib2.URLError:
			print "Trailer Bot: Found Nothing. That's Highly Unsual"
			return None