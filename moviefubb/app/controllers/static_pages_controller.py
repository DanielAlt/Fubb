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
