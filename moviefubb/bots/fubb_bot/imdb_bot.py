import requests, json, threading, urllib
from HTMLParser import HTMLParser
from .. import (
    logger as Logger,
    helpers as Helpers
)

""" This suppresses some console output when skipping SSL verification """
from requests.packages.urllib3.exceptions import (
	InsecureRequestWarning, 
	InsecurePlatformWarning, 
	SNIMissingWarning
)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
requests.packages.urllib3.disable_warnings(InsecurePlatformWarning)
requests.packages.urllib3.disable_warnings(SNIMissingWarning)

class Parser(HTMLParser):
	url = ""
	def handle_starttag(self, tag, attrs):
		if (tag == "a"):
			for attr in attrs:
				if (attr[0] == 'href') and ("/title/" in attr[1]):
					self.url = str(attr[1])
					raise Helpers.ParserReturn

	def getURL(self):
		return (self.url)

class LookupHandler(threading.Thread):
	def __init__(self, dispatcher, **kwargs):
		threading.Thread.__init__(self)
		self.config = Helpers.updateConfig({
			'movie_title': '',
			'request_id': Helpers.generateUUID()
		}, kwargs)
		self.dispatcher = dispatcher
		self.parser = Parser()
		self.search_url = "https://www.imdb.com/find?ref_=nv_sr_fn&q=%s&s=all" % (
			urllib.quote("+".join(self.config['movie_title'].split(" ")) )
		)
		

	def run(self):
		self.dispatcher.logger.log(Logger.INFO, "GET on %s" % self.search_url)		
		self.req = requests.get(self.search_url, verify=False)
		try:
			self.parser.feed(self.req.text)
		except Helpers.ParserReturn:
			pass

		self.url = self.parser.getURL()
