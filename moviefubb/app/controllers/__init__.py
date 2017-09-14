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

from bots import (email_bot)

_here = os.path.join(os.getcwd(), 'moviefubb')
_email_templates = os.path.join(_here, 'bots', 'email_templates')



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