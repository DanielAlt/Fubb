import os, sys, transaction, datetime
from ..security import (hashpassword)
from sqlalchemy import engine_from_config
from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars
from ..models import (
    DBSession,
    Movie,
    Base,
    User,
    Group,
    Profile,
    )

def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)

def main(argv=sys.argv):

    if len(argv) < 2:
        usage(argv)

    config_uri = argv[1]
    options = parse_vars(argv[2:])

    setup_logging(config_uri)
    settings = get_appsettings(config_uri)

    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    with transaction.manager:

        # Create Basic User Groups
        admin_group = Group(groupname='admin')
        user_group = Group(groupname='user')

        # Create Admin and Regular Users
        admin_user = User(
            username='admin',
            email='julien.altenburg@gmail.com',
            password= hashpassword('SKY_CANDY'),
            confirmed=False,
            confirmation_string="foobar",
            terms_accepted=True,
            solicitation= True,
            entry_date = datetime.datetime.today()
        )
        
        regular_user = User(
            username='DanielAlt',
            email='daniel.j.altenburg@gmail.com',
            password=hashpassword('SKY_CANDY'),
            confirmed= False,
            confirmation_string="foobar",
            terms_accepted=True,
            solicitation= True,
            entry_date = datetime.datetime.today()
        )

        # Add Users To Groups
        admin_user.addGroup(user_group)
        admin_user.addGroup(admin_group)
        regular_user.addGroup(user_group)

        # Add Users to Database
        DBSession.add(admin_user)
        DBSession.add(regular_user)