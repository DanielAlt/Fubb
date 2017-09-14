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
