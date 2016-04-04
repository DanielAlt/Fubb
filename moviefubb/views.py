import cgi, datetime, shutil, os, random

from string import Template
from docutils.core import publish_parts
from sqlalchemy.exc import DBAPIError

from pyramid.renderers import get_renderer
from pyramid.response import FileResponse
from pyramid.interfaces import IBeforeRender
from pyramid.events import subscriber
from pyramid.httpexceptions import (HTTPFound, HTTPNotFound, HTTPForbidden)
from pyramid.view import (view_config, forbidden_view_config, notfound_view_config)
from pyramid.security import (remember, forget)

from .models import (
    DBSession, 
    Movie, 
    User, 
    Group, 
    Profile,
    Privacy,
    Page,
    Hit
    )

from .security import (hashpassword, generateConfirmationCode)

from .controller import (
    AddUserForm, 
    AddMovieForm, 
    UserPrivacyForm,
    UpdateProfileForm
    )

from bots import (sweep, email_bot)

_here = os.path.join(os.getcwd(), 'moviefubb')
_email_templates = os.path.join(_here, 'bots', 'email_templates')

""" Helper Functions """
def getCurrentUser(request):
    email = request.authenticated_userid
    return (DBSession.query(User).filter_by(email=email).first())

def parse_genres(genre_string):
    genre_list = []

    if (genre_string):

        while (len(genre_string) > 0):
            hashtag_index = genre_string.find('#')

            if (hashtag_index is not -1):
                genre_string = genre_string[hashtag_index+1:]
                hashtag_index = genre_string.find('#')
        
                if (hashtag_index is not -1):
                    genre_list.append('#' + genre_string[:hashtag_index])
                    genre_string = genre_string[hashtag_index:]
                else:
                    genre_list.append('#' + genre_string)
                    genre_string = '' 
            else:
                genre_string = ''

    return (genre_list)

def parseIndexArgs(kargs):
    kargs = kargs[kargs.find('?')+1:]
    kargs = kargs.split('&')
    args = {
        'query': None,
        'orderby': None,
        'order': None,
        'page' : 0, 
        'results': 100,
        'view': 'details'
    }
    for k in kargs:
        k = k.split("=")
        if k[0] in args.keys():
            if not (k[1] == ""):
                args.update({k[0]:k[1]})
    return (args)

def paginate(to_paginate, args):
    pagination_args = args
    try:
        pagination_args['page'] = int(pagination_args['page'])
        pagination_args['results'] = int(pagination_args['results'])    
    except ValueError:
        return False

    to_paginate_size = len(to_paginate)
    number_of_pages = (to_paginate_size/int(pagination_args['results']))
    page_list = [x for x in range(0,number_of_pages+1)]
    lower_bound = pagination_args['page']-2
    upper_bound = pagination_args['page']+3
    upper_bal = number_of_pages-5
    lower_bal = 5

    if ((lower_bound > 0) and (upper_bound <= number_of_pages)):
        page_list = [0] + page_list[lower_bound : upper_bound] + [number_of_pages-1]

    elif ((upper_bal >=0) and (upper_bound >= number_of_pages)):
        page_list = [0] + page_list[upper_bal : number_of_pages]

    elif ((lower_bound <= 0) and (lower_bal <= number_of_pages)):
        page_list = page_list[0:lower_bal] + [number_of_pages-1]

    if ((to_paginate_size - (pagination_args['page']*pagination_args['results'])) > 0):
        to_paginate = to_paginate[pagination_args['page']*pagination_args['results']:(pagination_args['page']*pagination_args['results'])+pagination_args['results']]
    else:
        to_paginate = to_paginate[pagination_args['page']*pagination_args['results']:]

    return dict(
        page_content = to_paginate,
        number_of_pages = number_of_pages,
        current_page = pagination_args['page'],
        next_page = int(pagination_args['page'])+1,
        prev_page = int(pagination_args['page'])-1,
        results= int(pagination_args['results']),
        page_list = page_list
    )

def getRandomTrailer():
    all_embeds = []
    all_movies = DBSession.query(Movie).order_by('embed').all()
    for movie in all_movies:
        if not movie.embed in all_embeds:
            all_embeds.append(movie)
    
    if not (len(all_embeds) == 0):    
        max_embeds = len(all_embeds)
        embed = all_embeds[random.randrange(0,max_embeds)].embed
        return (embed)
    else:
        return "dKrVegVI0Us"

""" Global Template """
@subscriber(IBeforeRender)
def globals_factory(event):
    master = get_renderer('templates/master.pt').implementation()
    event['master'] = master

@notfound_view_config(
    renderer='templates/static_pages/404.pt',
)
def notfound(exc, request):
    msg = exc.args[0] if exc.args else ""
    current_user = getCurrentUser(request)
    return dict(
        message = msg,
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid, 
        current_user=current_user,
    )

@forbidden_view_config(
    renderer='templates/static_pages/403.pt'
)
def forbidden(exc, request):
    msg = exc.args[0] if exc.args else ""
    current_user = getCurrentUser(request)
    return dict(
        message = msg,
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid, 
        current_user=current_user,
    )

def updateAnalytics(page_url, request, user=None):
    page = DBSession.query(Page).filter_by(page_url=page_url).first()
    if page is None:
        page = Page(page_url = page_url)
        DBSession.add(page)
        page = DBSession.query(Page).filter_by(page_url=page_url).first()

    query = ''
    if "?" in page_url:
        query = page_url.split("?")[-1]

    user_id = None
    if user is not None:
        user_id = user.id

    hit = Hit(
        page_id=page.id,
        user_id=user_id,
        query=query, 
        user_agent=request.user_agent,
        user_addr= request.remote_addr,
        referrer=request.referrer
    )
    DBSession.add(hit)

""" Home Page """
@view_config(
    route_name='home', 
    renderer='templates/static_pages/home.pt', 
    permission='show'
)
def home(request):
    current_user = getCurrentUser(request)
    recent_movies = None
    random_trailer = getRandomTrailer()
    updateAnalytics((request.application_url + "/"), request, current_user)

    if current_user is not None:
        recent_movies = DBSession.query(Movie).filter_by(user_id=current_user.id).order_by('entry_date').all()
        recent_movies = recent_movies[-4:len(recent_movies)]

    return dict(
        request=request,
        random_trailer=random_trailer,
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid, 
        current_user=current_user,
        recent_movies=recent_movies
    ) 

""" About Page """
@view_config(
    route_name='about', 
    renderer='templates/static_pages/about.pt',
    permission='show'
)
def about(request):
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/about"), request, current_user)
    return dict(
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user = current_user
    )

@view_config(
    route_name='terms', 
    renderer='templates/static_pages/terms.pt',
    permission='show'
)
def terms(request):
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/terms"), request, current_user)
    return dict(
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user = current_user
    )

@view_config(
    route_name='privacy_statement', 
    renderer='templates/static_pages/privacy.pt',
    permission='show'
)
def privacy_statement(request):
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/privacy"), request, current_user)
    return dict(
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user = current_user,
    )
    
""" License Page """
@view_config(
    route_name='license', 
    renderer='templates/static_pages/license.pt',
    permission='show'
)
def license(request):
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/license"), request, current_user)
    return dict(
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user = current_user
    )

""" Help Page Index"""
@view_config(
    route_name='help_index', 
    renderer='templates/static_pages/help.pt',
    permission='show'
)
def help_index(request):
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/help"), request, current_user)
    return dict(
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user = current_user
    )

""" Add Movie """
@view_config(
    route_name='movie_add', 
    renderer='templates/movies/add.pt', 
    permission='edit'
)
def movie_add(request):
    current_user = getCurrentUser(request)

    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()

    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/movies/add"), request, current_user)

    if ('form.submitted' in request.params) and (current_user.id == user.id):

        """ Getting Form Data """
        title = request.params['title']
        location = request.params['location']
        genre_tags = request.params['genre_tags']
        status_dl = request.params['status_dl']
        status_w = request.params['status_w']
        entry_date = str(datetime.datetime.today())

        bot_info = sweep.botSweep(title=title)
        movie = Movie(
            # ID
            user_id = user.id,
        
            # User Supplied Data
            title = title,
            location = location,
            status_dl = status_dl,
            status_w = status_w,
            genre_tags = genre_tags,
            entry_date = entry_date,

            # Bot supplied Datas
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

        DBSession.add(movie)
        movie = DBSession.query(Movie).filter_by(user_id=user.id, title=title).one()

        return HTTPFound(
            location=request.route_url(
                'movie_show', 
                movie_id=movie.id, 
                user_id=user.id
            )
        )

    return dict(
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user=current_user,
        user=user
    )

""" Show Movie """
@view_config(
    route_name='movie_show', 
    renderer='templates/movies/show.pt', 
    permission='show'
)
def movie_show(request):
    current_user = getCurrentUser(request)
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()

    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    came_from = request.referrer
    continuous_addition = False
    if (came_from==(request.application_url + '/accounts/' + str(user.id) + "/movies/add")):
        continuous_addition = True


    movie_id = request.matchdict['movie_id']
    movie = DBSession.query(Movie).filter_by(user_id=user.id, id=movie_id).first()

    if (movie is None):
        raise HTTPNotFound('There is no such film on our servers')

    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/movies/" + str(movie.id)), request, current_user)

    """ Satisfying User Defined Privacy Settings """
    if (current_user is not None):
        if not (user.id == current_user.id):
            if ((user.privacy is not None) and (user.privacy.show_collection == 'onlyme')):
                raise HTTPForbidden('This User is not Displaying their Collection Publicly')
            if (user.privacy is None):
                raise HTTPForbidden('This User is not Displaying their Collection Publicly') 
    else:
        if ((user.privacy is not None) and (user.privacy.show_collection) == 'onlyme'):
            raise HTTPForbidden('This User is not Displaying their Collection Publicly')
        if ((user.privacy is not None) and (user.privacy.show_collection == 'fubbusers')):
            raise HTTPForbidden('This User is only Displaying their Collection to Fubb Users')

    if ((user.privacy is not None) and (user.privacy.show_collection == 'friends')):
        pass

    edit_url = request.route_url('movie_edit', movie_id=movie_id, user_id = user.id)

    return dict(
        movie=movie,
        continuous_addition=continuous_addition,
        request=request, 
        datetime=datetime.datetime.today(), 
        edit_url=edit_url, 
        logged_in=request.authenticated_userid,
        user=user,
        current_user=current_user
    )

""" Edit Movie """
@view_config(
    route_name='movie_edit', 
    renderer='templates/movies/edit.pt', 
    permission='edit'
)
def movie_edit(request):
    current_user = getCurrentUser(request)
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()
    message = ""

    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    movie = DBSession.query(Movie).filter_by(user_id=user.id, id=request.matchdict['movie_id']).first()  
    if movie is None:
        raise HTTPNotFound("There is no Such Movie associated with this user")

    if not (current_user.id==user.id):
        raise HTTPForbidden('You cannot edit another users movies.')

    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/movies/" + str(movie.id) + "/edit"), request, current_user)
    
    if (('form.submitted' in request.params)):
        # Update Immediately
        movie.location = request.params['location']
        movie.genre_tags = request.params['genre_tags']
        movie.status_dl = request.params['status_dl']
        movie.status_w = request.params['status_w']

        """ Update Info if IMDB ID is new """
        if 'imdb_id' in request.params.keys():
            bot_info = None
            imdb_id = request.params['imdb_id']
            if not (str(imdb_id) == str(movie.imdb_id)):
                bot_info = sweep.botSweep(imdbID=imdb_id)
                if bot_info is not None:
                    movie.year = bot_info['Year']
                    movie.rated = bot_info['Rated']
                    movie.runtime = bot_info['Runtime']
                    movie.director = bot_info['Director']
                    movie.writer = bot_info['Writer']
                    movie.actors = bot_info['Actors']
                    movie.plot = bot_info['Plot']
                    movie.country = bot_info['Country']
                    movie.awards = bot_info['Awards']
                    movie.imdb_rating = bot_info['imdbRating']
                    movie.imdb_votes = bot_info['imdbVotes']
                    movie.language = bot_info['Language']
                    movie.poster = bot_info['poster']
                    movie.imdb_id = bot_info["imdbID"]
                    movie.embed = bot_info['embed']
                else:
                    message += "Our Bots returned with nothing, :( \n"
            
        """ Update Trailer if New """
        if 'embed' in request.params.keys():
            embed = request.params['embed']
            if not (embed == movie.embed):
                movie.embed = embed

        DBSession.add(movie)
        return HTTPFound(
            location=request.route_url(
                'movie_show', 
                movie_id=movie.id, 
                user_id=user.id
            )
        )
    message = "There was an Error in the Form. Please make sure the form is correct, and try again."

    return dict(
        movie=movie,
        message=message,
        user = user,
        request=request, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user=current_user
    )

""" Movie Index """
@view_config(
    route_name='movie_index', 
    renderer='templates/movies/index.pt', 
    permission='show'
)
def movie_index(request):
    current_user = getCurrentUser(request)
    user = DBSession().query(User).filter_by(id=request.matchdict['user_id']).first()

    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/movies"), request, current_user)

    """ Satisfying User Defined Privacy Settings """
    if (current_user is not None):
        if not (user.id == current_user.id):
            if ((user.privacy is not None) and (user.privacy.show_collection == 'onlyme')):
                raise HTTPForbidden('This User is not Displaying their Collection Publicly')
            if (user.privacy is None):
                raise HTTPForbidden('This User is not Displaying their Collection Publicly') 
    else:
        if ((user.privacy is not None) and (user.privacy.show_collection) == 'onlyme'):
            raise HTTPForbidden('This User is not Displaying their Collection Publicly')
        if ((user.privacy is not None) and (user.privacy.show_collection == 'fubbusers')):
            raise HTTPForbidden('This User is only Displaying their Collection to Fubb Users')

    if ((user.privacy is not None) and (user.privacy.show_collection == 'friends')):
        pass

    page_args = parseIndexArgs(request.url)
    movies = DBSession.query(Movie).filter_by(user_id=user.id).all()
    collection_size = 0
    if movies is not None:
        collection_size = len(movies)

    orderby = 'status_dl'
    if (page_args['orderby'] is not None):
        orderby = page_args['orderby']

    query = page_args['query']
    if (query is not None):
        query = query.lower()
        query = query.replace('%20', ' ')
        query = query.replace('+', ' ')
        movies = DBSession.query(Movie).filter_by(user_id=user.id, title=query).order_by(orderby).all()
    else:
        movies = DBSession.query(Movie).filter_by(user_id=user.id).order_by(orderby).all()
    
    """ Pagination """
    pagination = paginate(movies, page_args)

    return dict(
        request=request, 
        movies=pagination['page_content'],
        pagination=pagination,
        page_args=page_args,
        collection_size=collection_size,
        datetime=datetime.datetime.today(), 
        current_user=current_user,
        user=user,
        logged_in=request.authenticated_userid
    )

""" Random Movie """
@view_config(route_name='movie_random', permission='show')
def movie_random(request):
    current_user = getCurrentUser(request)
    user = DBSession().query(User).filter_by(id=request.matchdict['user_id']).first()
    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/movies/random"), request, current_user)

    movies = DBSession().query(Movie).filter_by(user_id=user.id).all()
    if len(movies) == 0:
        raise HTTPNotFound("It's kind of hard to make out the movies in %s's collection. If you could just read me..." % user.username)
    seed = random.randrange(0,len(movies))
    movie = movies[seed]
    print """
    -------------------------------------------------
    Random Movie: %s
    -------------------------------------------------
    """ % movie.id
    return HTTPFound(
        location=request.route_url(
            'movie_show',
            movie_id=movie.id,
            user_id=user.id
        )
    )

""" Movie Stats """
@view_config(
    route_name='movie_stats', 
    renderer='templates/movies/stats.pt', 
    permission='show'
)
def movie_stats(request):
    current_user = getCurrentUser(request)
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()
    
    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")
  
    updateAnalytics((request.application_url + "/account/" + str(user.id) + "/movies/stats" ), request, current_user)
  
    """ Satisfying User Defined Privacy Settings """
    if (current_user is not None):
        if not (user.id == current_user.id):
            if ((user.privacy is not None) and (user.privacy.show_stats == 'onlyme')):
                raise HTTPForbidden('This User is not Displaying their Stats Publicly')
            if (user.privacy is None):
                raise HTTPForbidden('This User is not Displaying their Stats Publicly') 
    else:
        if ((user.privacy is not None) and (user.privacy.show_stats) == 'onlyme'):
            raise HTTPForbidden('This User is not Displaying their Stats Publicly')
        if ((user.privacy is not None) and (user.privacy.show_stats == 'fubbusers')):
            raise HTTPForbidden('This User is only Displaying their Stats to Fubb Users')

    if ((user.privacy is not None) and (user.privacy.show_stats == 'friends')):
        pass

    movies = DBSession.query(Movie).filter_by(user_id=user.id).order_by('status_dl').all()
    collection_size = len(movies)
    total_genres = {'Unclassified': collection_size}
    total_formats = {}
    total_decades = {}

    for movie in movies:
        
        # Get Genre Dictionary         
        genre_list = parse_genres(movie.genre_tags)
        for genre in genre_list:
            if (genre in total_genres):
                total_genres[genre] += 1
                total_genres['Unclassified'] -= 1
            else:
                total_genres.update({genre: 1})
                total_genres['Unclassified'] -= 1

        # Get Format Dictionary
        m_format = movie.location
        if (m_format in total_formats):
            total_formats[m_format] += 1
        else:
            total_formats.update({m_format: 1})

        #Get Year Dictionary
        decade = movie.year
        if (decade in total_decades):
            total_decades[decade] += 1
        else:
            total_decades.update({decade: 1})
    
    return dict(
        request = request, 
        user = user,
        logged_in = request.authenticated_userid,
        current_user = current_user,
        total_genres = total_genres,
        total_formats = total_formats,
        total_decades = total_decades,
        movies = movies,
        collection_size = collection_size,
        datetime = datetime.datetime.today() 
    )

""" Delete Movie """
@view_config(
    route_name='movie_delete', 
    permission='edit'
)
def movie_delete(request):
    current_user = getCurrentUser(request)
    user = DBSession().query(User).filter_by(id=request.matchdict['user_id']).first()
    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    movie = DBSession().query(Movie).filter_by(id=request.matchdict['movie_id']).first()
    if movie is None:
        raise HTTPNotFound("It's kind of hard to make out that Movie ID. If you could just read me...")

    if (movie.user_id == current_user.id):
        DBSession.delete(movie)

    return HTTPFound(
        location=request.route_url(
            'movie_index',
            user_id=user.id
        )
    )

""" Log In """
@view_config(
    route_name='login', 
    renderer='templates/accounts/login.pt'
)
def login(request):
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/login"), request, current_user)

    login_url = request.route_url('login')
    referrer = request.url
    if referrer == login_url:
        referrer = '/' # never use the login form itself as came_from
    
    came_from = request.params.get('came_from', referrer)

    message = ''
    email = ''
    password = ''

    if 'form.submitted' in request.params:
        email = request.params['email']
        email = email.lower()

        user = DBSession.query(User).filter_by(email=email).first()
        if (user is not None):
            password = request.params['password']
            password_hash = hashpassword(password)
            if (user.password == password_hash):
                headers = remember(request, email)
                return HTTPFound(
                    location = came_from, 
                    headers = headers
                )
            
        message = 'Incorrect Email or Password'

    return dict(
        message = message,
        url = request.application_url + '/login',
        came_from = came_from,
        password = password,
        logged_in=request.authenticated_userid,
        current_user=current_user
    )

""" Logout """
@view_config(route_name='logout')
def logout(request):
    headers = forget(request)
    return HTTPFound(
        location = request.route_url('home'),
        headers = headers
    )

"""
    ---------------------[Signup]--------------------------

    1.
    Define the Singup Form as a Dictionary with Default
    Values.
        
    2.
    When the form is submitted, update the default values, 
    with the values from the submitted Form.

    3.
    If the Passwords Match, Validate the Form Input using
    the AddUserForm validator defined in controller.py
    
    4.
    Hash the Password, and Generate Confirmation ID 
    using functions from security.py

    5.
    Add User to Database, and Add User to User Group

    6.
    Load User, to obtain unique ID

    7. 
    Send a Confirmation Email to the users Email.

    8.
    Log the User in and Rediret to Login Page

    ---------------------[Signup]--------------------------
"""

@view_config(
    route_name='signup', 
    renderer='templates/accounts/add.pt',
    permission='show'
)

def signup(request):
    #1: Default Values
    args = {
        'username': '',
        'email': '',
        'password': '',
        'password_confirm': '',
        'terms_accepted': False,
        'solicitation': False,
    }
    message = ""
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/signup"), request, current_user)

    if ('form.submitted' in request.params):
        #2: Get Form
        for arg in request.params.keys():
            if (arg in args.keys()):
                args.update({arg: request.params[arg]})

        if (args['password'] == args['password_confirm']):
            #3: Validation
            validity = AddUserForm().isValid(args) 
            if (validity[0]):
                #4: Security
                password_hash = hashpassword(args['password'])
                confirmation_string = generateConfirmationCode(random.randrange(1,100))
                #5: Save to DB
                user = User(
                    username=args['username'],
                    email=args['email'],
                    password= password_hash,
                    entry_date= str(datetime.datetime.today()),
                    solicitation =args['solicitation'],
                    confirmed = False,
                    confirmation_string = confirmation_string
                )
                user_group = DBSession.query(Group).filter_by(groupname='user').first()
                user.addGroup(user_group)
                DBSession.add(user)

                #6: Load The User from the Database
                user = DBSession.query(User).filter_by(email=args['email']).one()

                # 7: Send Confirmation Email
                bot = email_bot.EmailBot('julien.altenburg@gmail.com', 'psviegvkbsofljig')
                bot.appendRecipient([user.email])
                message_html = ""

                template_path = os.path.join(_email_templates, 'signup_confirmation.html')
                with open(template_path, 'rb') as f:
                    message_html = f.read()
                    f.close()
                s = Template(message_html)

                message_html = s.substitute(dict(
                    application_name = request.application_url,
                    username = user.username,
                    user_id = user.id,
                    confirmation_string = user.confirmation_string
                ))
                bot.sendMessage(
                    message = message_html,
                    sender = 'no-reply@fubb.com',
                    subject = 'Confirm Your Fubb Account'
                )

                #8: Log User In, Redirect to Login
                headers = remember(request, args['email'])
                return HTTPFound(
                    location=request.route_url('user_show', user_id=user.id),
                    headers=headers
                )
            else:
                message = "Sorry, The Information entered was invalid, %s" % (validity[1])
        else:    
            message = "Sorry, Those Passwords did not Match."

    # This is the default Page
    return dict(
        request=request,
        username = args['username'],
        password = args['password'],
        password_confirm = args['password'],
        terms_accepted = args['terms_accepted'],
        solicitation=args['solicitation'],
        message = message,
        datetime=datetime.datetime.today(),
        logged_in=request.authenticated_userid,
        current_user=current_user
    )

""" Resend Confirmation Email """
@view_config(
    route_name = 'user_confirm_resend', 
    renderer='templates/accounts/confirm_resend.pt',
    permission='edit'
)
def user_confirm_resend(request):
    current_user = getCurrentUser(request)
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).one()
    success = False
    updateAnalytics((request.application_url + "/account/" + str(user.id) + "confirm/resend"), request, current_user)

    if (user is None) or (current_user is None):
        success = False

    if (current_user.id == user.id) and (user.confirmed == False):
        success = True
        # Update Confirmation String
        confirmation_string = generateConfirmationCode(random.randrange(1,100))

        user.confirmation_string = confirmation_string
        DBSession.add(user)
        # Send Email
        bot = email_bot.EmailBot('julien.altenburg@gmail.com', 'psviegvkbsofljig')
        bot.appendRecipient([user.email])
        message_html = ""

        template_path = os.path.join(_email_templates, 'signup_confirmation.html')
        with open(template_path, 'rb') as f:
            message_html = f.read()
            f.close()
        s = Template(message_html)

        message_html = s.substitute(dict(
            application_name = request.application_url,
            username = user.username,
            user_id = user.id,
            confirmation_string = user.confirmation_string
        ))
        bot.sendMessage(
            message = message_html,
            sender = 'no-reply@fubb.com',
            subject = 'RESEND: Confirm Your Fubb Account'
        )

    return dict(
        request=request,
        user=user,
        current_user=current_user,
        success=success,
        datetime=datetime.datetime.now(),
        logged_in=request.authenticated_userid,
    )

""" Forgot Password"""
@view_config(
    route_name='psswd_forgot',
    renderer='templates/accounts/forgot.pt',
    permission='show'
)
def psswd_forgot(request):
    message = None
    email = ''
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/forgot"), request, current_user)

    if 'form.submitted' in request.params:
        email = request.params['email']
        user = DBSession.query(User).filter_by(email=email).first()

        if (user is not None):
            if (user.confirmed):
                confirmation_string = generateConfirmationCode(user.id)
                user.confirmation_string = confirmation_string

                bot = email_bot.EmailBot('julien.altenburg@gmail.com', 'psviegvkbsofljig')
                bot.appendRecipient([user.email])
                message_html = ""

                template_path = os.path.join(_email_templates, 'psswd_forgot.html')
                with open(template_path, 'rb') as f:
                    message_html = f.read()
                    f.close()

                s = Template(message_html)

                message_html = s.substitute(dict(
                    application_name = request.application_url,
                    username = user.username,
                    user_id = user.id,
                    confirmation_string = user.confirmation_string
                ))

                bot.sendMessage(
                    message = message_html,
                    sender = 'no-reply@fubb.com',
                    subject = 'Recover your Password'
                )
                mesage = """
                    An email was successfully delivered to %s, please follow the directions in the email
                    to recover your account.
                """ % user.email
            else:
                message = """
                    The account associated with this Email was never confirmed. 
                    you cannot recover the password. Please create a new account.
                """
        else:
            message = """ 
                There is no such User with the Email, '%s'. 
                Are you sure that is the right email?
            """ % email
    
    return dict(
        request = request,
        message = message,
        datetime=datetime.datetime.now(),
        logged_in=request.authenticated_userid
    )

""" Password Recovery """
@view_config(
    route_name = 'psswd_recover',
    permission='show'
)
def psswd_recover(request):
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()
    if user is None:
        raise HTTPNotFound('No such User')

    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/recover" ), request, current_user)

    """ Sign User In, and Redirect to Login Form"""
    if (request.matchdict['confirmation_string'] == user.confirmation_string):

        headers = remember(request, user.email)
        return HTTPFound(
            location=request.route_url('user_edit', user_id=user.id),
            headers=headers
        )

    raise HTTPForbidden("Nope")

""" Confirm Account Email """
@view_config(
    route_name = 'user_confirm',
    renderer='templates/accounts/confirm.pt',
    permission='edit'
)
def user_confirm(request):
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()
    current_user = getCurrentUser(request)
    confirmed = False
    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/confirm"), request, current_user)

    if (user is None):
        raise HTTPNotFound('User ID ')
    if not (user.id == current_user.id):
        raise HTTPForbidden('That is not your Account')

    if (user.confirmation_string == request.matchdict['confirmation_string']):
        user.confirmed = True
        DBSession().add(user)
        confirmed = True

    return dict(
        request=request, 
        user=user, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user=current_user,
        confirmed = confirmed
    )

""" Accounts Index """
@view_config(
    route_name='user_index', 
    renderer='templates/accounts/index.pt', 
    permission='edit'
)
def user_index(request):
    current_user = getCurrentUser(request)
    page_args = parseIndexArgs(request.url)
    updateAnalytics((request.application_url + "/accounts"), request, current_user)

    query = page_args['query']
    if (query is not None):
        query = query.lower()
        query = query.replace('%20', ' ')
        query = query.replace('+', ' ')
        users = DBSession.query(User).filter_by(username=query).all()
    else:
        users = DBSession.query(User).order_by('username').all()
    
    """ Pagination """
    pagination = paginate(users, page_args)

    return dict(
        request=request, 
        pagination=pagination,
        users= pagination['page_content'],
        page_args=page_args, 
        datetime=datetime.datetime.today(), 
        logged_in=request.authenticated_userid,
        current_user=current_user
    )

""" Accounts Show """
@view_config(
    route_name='user_show', 
    renderer='templates/accounts/show.pt', 
    permission='show'
)
def user_show(request):
    current_user = getCurrentUser(request)
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first() 
    updateAnalytics((request.application_url + "/accounts/" + str(user.id)), request, current_user)

    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    """ Satisfying User Defined Privacy Settings """
    if (current_user is not None):
        if not (user.id == current_user.id):
            if ((user.privacy is not None) and (user.privacy.show_profile == 'onlyme')):
                raise HTTPForbidden('This User is not Displaying their Profile Publicly')
            if (user.privacy is None):
                raise HTTPForbidden('This User is not Displaying their Profile Publicly') 
    else:
        if ((user.privacy is not None) and (user.privacy.show_profile) == 'onlyme'):
            raise HTTPForbidden('This User is not Displaying their Profile Publicly')
        if ((user.privacy is not None) and (user.privacy.show_profile == 'fubbusers')):
            raise HTTPForbidden('This User is only Displaying their Profile to Fubb Users')

    if ((user.privacy is not None) and (user.privacy.show_profile == 'friends')):
        pass

    movies = DBSession.query(Movie).filter_by(user_id=user.id).order_by('title').all()

    if movies is None:
        collection_total = 0
        recent_movies = None
    else:
        collection_total = len(movies)
        recent_movies = list(reversed(DBSession.query(Movie).filter_by(user_id=user.id).order_by('entry_date').all()[-5:]))

    edit_url = request.route_url('user_settings', user_id=user.id)
    return dict(
        request=request,
        user=user,
        datetime=datetime.datetime.today(),
        edit_url = edit_url,
        logged_in=request.authenticated_userid,
        current_user=current_user,
        recent_movies=recent_movies,
        collection_total=collection_total
    )

""" Accounts Settings """
@view_config(
    route_name='user_settings', 
    renderer='templates/accounts/settings.pt',
    permission='edit'
)
def user_settings(request):
    current_user = getCurrentUser(request)
    user = DBSession.query(User).filter_by(id=request.matchdict['user_id']).first()
    updateAnalytics((request.application_url + "/accounts/" + str(user.id) + "/settings"), request, current_user)

    message = ""
    last_form = 'core'

    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    if not (user.id == current_user.id):
        raise HTTPForbidden("That is not your account")

    core_form = {
        'username': user.username,
        'email': user.email,
        'password': None,
        'password_confirm': None,   
    }

    if user.profile is None:
        profile_form = {
            'fav_film': '',
            'fav_show': '',
            'fav_genre': '',
            'about_me': ''
        }
    else:
        profile_form = {
            'fav_film': user.profile.fav_film,
            'fav_show': user.profile.fav_show,
            'fav_genre': user.profile.fav_genre,
            'about_me': user.profile.about_me
        }
    if (user.privacy is None):
        privacy_form = {
            'show_profile': None,
            'show_collection': None,
            'show_stats': None,
        }
    else:
        privacy_form = {
            'show_profile': user.privacy.show_profile,
            'show_collection': user.privacy.show_collection,
            'show_stats': user.privacy.show_stats,
        }
    
    if ('core.submitted' in request.params):

        for key in request.params.keys():
            if key in core_form.keys():
                core_form.update({key: request.params[key]})

        core_form.update({'terms_accepted': 'true'})
        core_valid = AddUserForm().isValid(core_form)
        if (core_valid[0]):
            password_hash = hashpassword(core_form['password'])
            user.username = core_form['username']
            user.email = core_form['email']
            user.password = password_hash

            DBSession.add(user)

            headers = forget(request)
            headers += remember(request, core_form['email'])
            message = "You have Successfully Updated your Core Settings"
        else:
            message = "Sorry, The Information you entered was invalid, Please try again. %s" % str(core_valid[1])
        last_form = 'core'

    if ('profile.submitted' in request.params): 

        for key in request.params.keys():
            if key in profile_form.keys():
                profile_form.update({key: request.params[key]})

        if (UpdateProfileForm().isValid(profile_form)):

            profile_form.update({'user_id': user.id})
            if user.profile is None:
                profile = Profile(
                    user_id = user.id,
                    fav_film = profile_form['fav_film'],
                    fav_show = profile_form['fav_show'],
                    fav_genre = profile_form['fav_genre'],
                    about_me = profile_form['about_me']
                )
                DBSession.add(profile)
            else:
                user.profile.fav_film = profile_form['fav_film']
                user.profile.fav_show = profile_form['fav_show']
                user.profile.fav_genre = profile_form['fav_genre']
                user.profile.about_me = profile_form['about_me']

            message = 'Your Profile Settings have been Updated'

        else:
            message = "There was a mistake in the Profile Form"

        last_form = 'profile'

    if ('privacy.submitted' in request.params):
        
        for key in request.params.keys():
            if key in privacy_form.keys():
                privacy_form.update({key: request.params[key]})
            
        if (UserPrivacyForm().isValid(privacy_form)):
            privacy_form.update({'user_id': user.id})

            if (user.privacy is None):

                privacy_obj = Privacy(
                    user_id=user.id,
                    show_profile=privacy_form['show_profile'],
                    show_collection=privacy_form['show_collection'],
                    show_stats=privacy_form['show_stats']
                )
                DBSession.add(privacy_obj)
            else:
                privacy_obj = user.privacy
                privacy_obj.show_profile = privacy_form['show_profile']
                privacy_obj.show_collection = privacy_form['show_collection']
                privacy_obj.show_stats = privacy_form['show_stats']
                DBSession.add(privacy_obj)

            message = 'You have successfully updated your privacy Settings'
        else:
            message = 'There was a mistake in the Privacy Form. Please try Again.'
        last_form = 'privacy'

    # This is the default Page
    return dict(
        request=request,
        core_form = core_form,
        profile_form=profile_form,
        privacy_form=privacy_form,
        message = message,
        last_form = last_form,
        datetime=datetime.datetime.today(),
        logged_in=request.authenticated_userid,
        current_user=current_user,
        user=user
    )

""" USER delete"""
@view_config(
    route_name='user_delete',
    permission='edit'
)
def user_delete(request):
    current_user = getCurrentUser(request)
    user = DBSession().query(User).filter_by(id=request.matchdict['user_id']).first()
    if user is None:
        raise HTTPNotFound("The ID on that username is a little fuzzy, if you could just read me...")

    if (user.id == current_user.id):
        """ Make sure to delete everything the user owns also """
        movies = DBSession.query(Movie).filter_by(user_id=user.id).all()

        for movie in movies:
            DBSession.delete(movie)

        DBSession.delete(user)
        headers = forget(request)
        return HTTPFound(location=request.route_url('home'), headers=headers)
    else:
        raise HTTPForbidden("Please don't do that. That's not your account")


""" Trailer Index """
@view_config(
    route_name='trailer_index', 
    renderer='templates/trailers/index.pt',
    permission='show'
)
def trailer_index(request):
    referrer = request.url
    came_from = request.params.get('came_from', referrer)
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/trailers"), request, current_user)

    page_args = parseIndexArgs(request.url)

    orderby = 'embed'
    if (page_args['orderby'] is not None):
        orderby = page_args['orderby']

    query = page_args['query']
    if (query is not None):
        query = query.lower()
        query = query.replace('%20', ' ')
        query = query.replace('+', ' ')
        movies = DBSession.query(Movie).filter_by(title=query).order_by(orderby).all()
    else:
        movies = DBSession.query(Movie).order_by(orderby).all()

    all_embeds = []
    for movie in movies:
        if not movie.embed in all_embeds:
            all_embeds.append(movie)    

    pagination = paginate(all_embeds, page_args)

    return dict(
        request=request,
        all_embeds= pagination['page_content'],
        pagination=pagination,
        page_args=page_args,
        datetime=datetime.datetime.today(),
        logged_in=request.authenticated_userid,
        current_user=current_user,
    )

""" Trailer Show """
@view_config(
    route_name='trailer_show', 
    renderer='templates/trailers/show.pt',
    permission='show'
)
def trailer_show(request):
    current_user = getCurrentUser(request)
    referrer = request.url
    came_from = request.params.get('came_from', referrer)
    movie = DBSession.query(Movie).filter_by(embed=request.matchdict['embed_id']).first()
    if movie is None:
        raise HTTPNotFound("I can't make out what trailer you wanted to see, maybe you could read..")

    updateAnalytics((request.application_url + "/trailers/" + movie.embed), request, current_user)
 
    return dict(
        request=request,
        movie=movie,
        datetime=datetime.datetime.today(),
        logged_in=request.authenticated_userid,
        current_user=current_user,
    )

""" Trailer Random """
@view_config(
    route_name='trailer_random',
    permission='show'
)
def trailer_random(request):
    referrer = request.url
    came_from = request.params.get('came_from', referrer)
    current_user = getCurrentUser(request)
    updateAnalytics((request.application_url + "/trailers/random"), request, current_user)
    embed = getRandomTrailer()
    return HTTPFound(
        location=request.route_url(
            'trailer_show',
            embed_id=embed
        )
    )

@view_config(
    route_name='admin_analytics',
    renderer='templates/admin/analytics.pt',
    permission='admin'
)

def admin_analytics(request):
    current_user = getCurrentUser(request)

    pages = DBSession.query(Page).order_by('page_url').all()
    page_args = parseIndexArgs(request.url)
    pagination = paginate(pages, page_args)

    total_hits = 0
    fav_agent_nums = {}
    for page in pages:
        total_hits += len(page.myhits)
        for hit in page.myhits:
            if hit.user_agent in fav_agent_nums.keys():
                fav_agent_nums[hit.user_agent] += 1
            else:
                fav_agent_nums.update({hit.user_agent: 1})

    fav_agent = ['', 0]
    for agent in fav_agent_nums.keys():
        if (fav_agent_nums[agent] >= fav_agent[1]):
            fav_agent = [agent, fav_agent_nums[agent]]

    return dict(
        request=request,
        total_hits=total_hits,
        fav_agent=fav_agent,
        pagination=pagination,
        page_args=page_args,
        pages= pagination["page_content"],
        datetime=datetime.datetime.today(),
        logged_in=request.authenticated_userid,
        current_user=current_user,
    )    