from . import *

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'show'),
                (Allow, 'user', 'edit'),
                (Allow, 'admin', 'admin')]
    def __init__(self, request):
        pass