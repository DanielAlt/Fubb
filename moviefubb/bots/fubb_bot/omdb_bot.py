import requests, json, threading
from .. import (
    logger as Logger,
    helpers as Helpers
)

class LookupHandler(threading.Thread):
	def __init__(self, dispatcher, **kwargs):
		threading.Thread.__init__(self)
		self.config = Helpers.updateConfig({
			'request_id': Helpers.generateUUID(),
			'api_key': None,
			'movie_title': None,
			'imdb_id': None
		}, kwargs)

		self.dispatcher = dispatcher
		self.target_url = "http://www.omdbapi.com/?apikey=%s&" % self.config['api_key']

	def run(self):
		self.target_url += "t=%s&plot=full" % "+".join(self.config['movie_title'].split(" "))
		self.dispatcher.logger.log(Logger.DEBUG, "GET on %s" % self.target_url)
		self.req = requests.get(self.target_url)
