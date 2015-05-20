from pyramid.config import Configurator
from sqlalchemy import engine_from_config
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from .security import EntryFactory
from pyramid_mailer.mailer import Mailer

from .models import (
    DBSession,
    Base,
    )

import logging



def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    #logger = logging.getLogger(__name__)
    #hdlr = logging.FileHandler('/var/log/startupdex/wsgi.log')
    #logging.config.fileConfig(settings['logging.config'],
                              #disable_existing_loggers=False,
                              #)
    #formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    #hdlr.setFormatter(formatter)
    #logger.addHandler(hdlr)
    #logging.config.fileConfig(settings['logging.config'])
    # this allows imperative table definitions (as opposed to declarative
    Base.metadata.bind = engine
    authentication_policy = AuthTktAuthenticationPolicy(
        'somesecret', hashalg='sha512')
    authorization_policy = ACLAuthorizationPolicy()
    config = Configurator(settings=settings,
                          authentication_policy=authentication_policy,
                          authorization_policy=authorization_policy
                          )
    config = Configurator(settings=settings)
    config.registry['mailer'] = Mailer.from_settings(settings)
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)

    config.include('pyramid_mailer')
    config.include('pyramid_jinja2')
    config.include('pyramid_redis_sessions')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view(name='images', path='images', cache_max_age=3600)
    config.add_route('blog_action', '/blog/{action}',
                     factory='startupdex.security.EntryFactory')

    config.add_route('frontpage', '/')
    config.add_route('contact_us', '/contact_us')
    config.add_route('register', '/register')
    config.add_route('confirm_email', '/confirm_email/{token}')
    config.add_route('login', '/login')
    config.add_route('logout', '/logout')
    config.add_route('search_redirect', '/search_redirect')
    config.add_route('search', '/search')
    config.add_route('startup_browse', '/browse/')

    # identifier => if int, search by id, if text, search by name
    config.add_route('create_startup', '/create_startup')
    config.add_route('upload_logo', '/upload_logo/{id}')
    config.add_route('modify_startup', '/modify_startup/{id}')
    config.add_route('modify_social', '/modify_social/{id}')
    config.add_route('modify_locations', '/modify_locations/{id}')
    config.add_route('modify_images', '/modify_images/{id}')
    config.add_route('startup_profile', '/startup/{ident}')
    config.add_route('startup_delete', '/startup/delete/{id}')
    config.add_route('startup_delete_confirmed', '/startup/delete/confirmed/{id}')

    config.add_route('create_article', '/create_article')
    config.add_route('upload_article_photo', '/upload_article_photo/{id}')
    config.add_route('modify_article', '/modify_article/{id}')

    # not currently in use
    config.add_route('startup_edit', '/startup/edit/{id}')
    config.add_route('startup_images', '/startup_images/{id}')

    config.add_route('loggedin_profile', '/profile')
    config.add_route('modify_profile', '/modify_profile')
    config.add_route('modify_billing', '/modify_billing')
    config.add_route('manage_articles', '/manage/articles')
    config.add_route('manage_startups', '/manage/startups')


    config.add_route('user_create', '/user/create/')
    config.add_route('user_profile', '/user/{ident}')
    config.add_route('upload_profile_photo', '/upload_profile_photo')
    config.add_route('user_edit', '/user/edit/{id}')
    config.add_route('user_delete', '/user/delete/{id}')
    config.add_route('user_delete_confirmed', '/user/delete/confirmed/{id}')

    config.add_route('admin_home', '/admin/')
    config.add_route('db_angelco', '/admin/db_angelco/')
    config.add_route('db_users', '/admin/db_users/')
    config.add_route('admin_update_user', '/admin/update_user')
    config.add_route('db_startups', '/admin/db_startups/')
    config.add_route('db_articles', '/admin/db_articles/')

    config.add_route('test', '/test/')
    config.add_route('test2', '/test2/')
    config.add_route('test3', '/test3/')

    config.scan()
    return config.make_wsgi_app()
