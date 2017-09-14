import requests, json, threading, urllib
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


class LookupHandler(threading.Thread):
	def __init__(self, dispatcher, **kwargs):
		threading.Thread.__init__(self)
		self.config = Helpers.updateConfig({
			'request_id': Helpers.generateUUID(),
			'api_key': '1a5aa1a70f532a35ce7f75c09b339609',
			'movie_title': None,
			'imdb_id': None
		}, kwargs)

		self.dispatcher = dispatcher
		self.target_url = "http://api.themoviedb.org/3/search/movie?query=%s&api_key=%s" % (
			urllib.quote("+".join( self.config['movie_title'].split(" ") )),
			self.config['api_key']
		)

	def run(self):
		self.dispatcher.logger.log(Logger.DEBUG, "GET on %s" % self.target_url)
		self.req = requests.get(self.target_url, verify=False)
