
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
