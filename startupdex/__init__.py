from pyramid.config import Configurator
from sqlalchemy import engine_from_config

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
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('frontpage', '/')
    # identifier => if int, search by id, if text, search by name
    config.add_route('startup_profile', '/startup/{identifier}')
    config.add_route('results', '/results/{query}')
    config.scan()
    return config.make_wsgi_app()
