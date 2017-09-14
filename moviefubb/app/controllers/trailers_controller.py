
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

