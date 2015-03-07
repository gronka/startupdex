from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import EntryFactory

from .models import (
    DBSession,
    Base,
    )


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    # this allows imperative table definitions (as opposed to declarative
    Base.metadata.bind = engine
    authentication_policy = AuthTktAuthenticationPolicy('somesecret')
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy
                          )
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('pyramid_redis_sessions')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('blog_action', '/blog/{action}',
                     factory='startupdex.security.EntryFactory')

    config.add_route('frontpage', '/')
    config.add_route('search', '/search/{query}')
    config.add_route('startup_browse', '/browse/')

    # identifier => if int, search by id, if text, search by name
    config.add_route('startup_profile', '/startup/{ident}')
    config.add_route('startup_create', '/startup/create')
    config.add_route('startup_edit', '/startup/edit/{id}')
    config.add_route('startup_delete', '/startup/delete/{id}')
    config.add_route('startup_delete_confirmed', '/startup/delete/confirmed/{id}')

    config.add_route('user_profile', '/user/{ident}')
    config.add_route('user_create', '/user/create/')
    config.add_route('user_edit', '/user/edit/{id}')
    config.add_route('user_delete', '/user/delete/{id}')
    config.add_route('user_delete_confirmed', '/user/delete/confirmed/{id}')

    config.add_route('admin_home', '/admin/')
    config.add_route('db_angelco', '/admin/db_angelco/')

    config.scan()
    return config.make_wsgi_app()
