import threading, time, os

from .. import (
    logger as Logger,
    helpers as Helpers
)

from . import (
    omdb_bot as omdb,
    imdb_bot as imdb,
    pirate_bot as pirate,
    poster_bot as poster,
    trailer_bot as trailer,
    tmdb_bot as tmdb
)

_object_library = {
    'omdb': omdb.LookupHandler,
    'imdb': imdb.LookupHandler,
    'tmdb': tmdb.LookupHandler,
    'pirate': pirate.LookupHandler,
    'trailer': trailer.LookupHandler
}

class FubbBot(threading.Thread):

    def __init__(self, **kwargs):
        threading.Thread.__init__(self)
        self.config = Helpers.updateConfig({
            'maximum_threads': 4,
            'refresh_interval': 40,
            'application': 'META-BOT',
            'log_level': Logger.DEBUG,
            'environment': Logger.PRODUCTION,
            'log_path': os.getcwd()
        }, kwargs)

        self.logger = Logger.Logger(**kwargs)
        self.logger.log(Logger.INFO, "Meta Bot Initialized")

        self.finished_tasks = []
        self.active_tasks = []
        self.task_queue = {}

        self.awake = True

    def add_task(self, **kwargs):
        task_config = Helpers.updateConfig({
            'method': None,
            'args': {}
        }, kwargs)
        request_id = Helpers.generateUUID()
        self.task_queue.update({request_id: task_config})
        self.logger.log(Logger.INFO, "Adding New Task: %s, to task queue" % request_id)
        return (request_id)

    def clear_tasks(self):
        self.task_queue = {}
        return (self)

    def remove_tasks(self, task_ids):
        for task in task_ids:
            if task in self.task_queue.keys():
                self.task_queue.pop( self.task_queue.keys()[self.task_queue.keys().index(task)] )
        return (self)

    def exit(self):
        self.awake = False

    def run(self):
        while (self.awake):
            time.sleep(self.config['refresh_interval']/1000.0)

            """ Start new Tasks """
            threads_to_create = self.config['maximum_threads'] - len(self.active_tasks)
            threads_to_create = threads_to_create if ( threads_to_create <= len(self.task_queue) ) else len(self.task_queue)

            if (threads_to_create > 0):
                for x in range(0, threads_to_create):
                    request_id = self.task_queue.keys()[0]
                    thread_data = self.task_queue.pop( request_id )
                    thread_data['args'].update({'request_id': request_id})
                    thread = _object_library[thread_data['method']](self, **thread_data['args'])
                    thread.start()
                    self.active_tasks.append(thread)
                    self.logger.log(Logger.INFO, 'launching task: %s, in task queue' % request_id)
                    # Here you would use some object to broadcast the status to the user using
                    # the request_id

            """ Kill old Tasks """
            for thread in self.active_tasks:
                if not thread.isAlive():
                    self.active_tasks.remove(thread)
                    self.finished_tasks.append(thread)
                    self.logger.log(Logger.INFO, 'finished task: %s, removing from task queue' % thread.config['request_id'])
                    # Here you would use some object to broadcast the status to the user using
                    # the request_id
