
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
