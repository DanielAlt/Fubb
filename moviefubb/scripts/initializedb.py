import os, sys, transaction, datetime

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

from ..security import (hashpassword)
from ..bots import sweep

movielist_path = os.path.join(os.getcwd(), 'moviefubb', 'scripts', 'movie_list.txt')
dvdlist_path = os.path.join(os.getcwd(), 'moviefubb', 'scripts', 'dvd_list.txt')

def addMovie(user_id, title):
    try:
        bot_info = sweep.botSweep(title=title)
    except TypeError:
        bot_info = None
        
    if bot_info is not None:
        movie = Movie(
            user_id = user_id,
            title = title,
            location = 'dvd',
            status_dl = 'pending',
            status_w = 'not watched',
            genre_tags = '',
            entry_date = str(datetime.datetime.now()),
            year = bot_info['Year'],
            rated = bot_info['Rated'],
            runtime = bot_info['Runtime'],
            director = bot_info['Director'],
            writer = bot_info['Writer'],
            actors = bot_info['Actors'],
            plot = bot_info['Plot'],
            country = bot_info['Country'],
            awards = bot_info['Awards'],
            imdb_rating = bot_info['imdbRating'],
            imdb_votes = bot_info['imdbVotes'],
            language = bot_info['Language'],
            poster = bot_info['poster'],
            imdb_id = bot_info["imdbID"],
            magnet = bot_info['magnet'],
            embed = bot_info['embed']
        )
    else:
        movie = Movie(
            user_id = 1,
            title = title,
            location = 'dvd',
            status_dl = 'pending',
            status_w = 'not watched',
            genre_tags = '',
            entry_date = str(datetime.datetime.now()),
    )
    return (movie)

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

        #Load Movies From Movie list
        movie_list = []
        with open(movielist_path, 'r') as f:
            movie_list = f.readlines()
            f.close()
        movie_list = [line.strip('\n') for line in movie_list]

        #Adding Sample Movies to Database
        for title in movie_list:
            print "\n\nSweeping For: %s" % title
            movie = addMovie(1, title)
            DBSession.add(movie)

        #Load Movie From Movie List
        movie_list = []
        with open(dvdlist_path, 'r') as f:
            movie_list = f.readlines()
            f.close()

        movie_list = [line.strip('\n') for line in movie_list]
        for title in movie_list:
            print "\n\nSweeping For: %s" % title
            movie = addMovie(2, title)
            DBSession.add(movie)