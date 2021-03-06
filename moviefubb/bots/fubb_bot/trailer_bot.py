import requests, json, threading
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
		self.dispatcher = dispatcher
		self.config = Helpers.updateConfig({
			'request_id': Helpers.generateUUID(),
			'movie_title': None,
			'api_key': 'AIzaSyAhb395QHEQaFGxOtDtq0mMZkNMsMxo7K8'
		}, kwargs)

		self.target_url = 'https://www.googleapis.com/youtube/v3/search?part=id&q=%s&type=video&key=%s' % (
			"+".join(self.config["movie_title"].split(" ")),
			self.config['api_key']
		)

	def run(self):
		self.dispatcher.logger.log(Logger.DEBUG, "GET on %s" % self.target_url)
		self.req = requests.get(self.target_url, verify=False)