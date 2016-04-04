from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from sqlalchemy import engine_from_config

from moviefubb.security import groupfinder

from .models import (
    DBSession,
    Base,
    )

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine

    authn_policy = AuthTktAuthenticationPolicy(
        'sosecret', 
        callback=groupfinder,
        hashalg='sha512'
    )
    authz_policy = ACLAuthorizationPolicy()
    config = Configurator(
        settings=settings,
        root_factory='moviefubb.models.RootFactory'
    )
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)

    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('uploads', 'uploads')
    
    config.add_route('home', '/')
    config.add_route('about', '/about')
    config.add_route('terms', '/terms')
    config.add_route('license', '/license')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('signup', '/signup')
    config.add_route('privacy_statement', '/privacy')
    config.add_route('psswd_forgot', '/forgot')
    
    config.add_route('trailer_random', '/trailers/random')
    config.add_route('trailer_show', '/trailers/{embed_id}')
    config.add_route('trailer_index', '/trailers')

    config.add_route('user_show', '/accounts/{user_id}')
    config.add_route('user_settings', '/accounts/{user_id}/settings')
    config.add_route('user_delete', '/accounts/{user_id}/delete')
    config.add_route('user_confirm_resend', '/accounts/{user_id}/confirm/resend')
    config.add_route('psswd_recover', '/accounts/{user_id}/recovery/{confirmation_string}')
    config.add_route('user_confirm', '/accounts/{user_id}/confirm/{confirmation_string}')    

    config.add_route('admin_analytics', '/admin/analytics')

    config.add_route('movie_add', '/accounts/{user_id}/movies/add')
    config.add_route('movie_stats', '/accounts/{user_id}/movies/stats')
    config.add_route('movie_random', '/accounts/{user_id}/movies/random')
    config.add_route('movie_show', '/accounts/{user_id}/movies/{movie_id}')
    config.add_route('movie_edit', '/accounts/{user_id}/movies/{movie_id}/edit')
    config.add_route('movie_delete', '/accounts/{user_id}/movies/{movie_id}/delete')
    config.add_route('movie_index', '/accounts/{user_id}/movies')
    
    config.add_route('user_index', '/accounts')
    config.add_route('help_index', '/help')

    config.scan()
    return config.make_wsgi_app()
