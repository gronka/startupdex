#from pyramid.response import Response
from pyramid.view import (
    view_config,
    #notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPFound,
    #HTTPNotFound,
    )

#from sqlalchemy.exc import DBAPIError
from sqlalchemy import (
    desc,
    #engine,
    )

from .models import (
    DBSession,
    Startup,
    AngelCoMirror,
    User,
    Article,
    fix_integer_fields,
    FTSStartup,
    )

from startupdex.view_warlock import ViewWarlock

import json
import requests
import math
from datetime import datetime

import logging

from peewee import *
from playhouse.sqlite_ext import *

log = logging.getLogger(__name__)


class FrontpageView(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='frontpage', renderer='templates/frontpage.jinja2')
    def frontpage(self):
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='search_redirect', renderer='templates/search.jinja2')
    def search_redirect(self):
        params = self.request.params
        print(params)
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='search', renderer='templates/search.jinja2')
    def search(self):
        params = self.request.params
        #for item in params:
            #print(item)
        search_terms = params["search_terms"]
        if "page" in params:
            page = int(params["page"])
        else:
            page = 1
        #per_page = param["per_page"]
        per_page = 10

        results = (FTSStartup
                .select(
                    FTSStartup,
                    FTSStartup.bm25(FTSStartup.content).alias('score'))
                .where(FTSStartup.match( search_terms ))
                .order_by(SQL('score').desc())
                )
        num_pages = math.ceil(results.count() / per_page)
        offset = per_page * page - per_page
        print("now the results")
        print(results)
        print("number of results: " + str(results.count()))
        print("number of pages: " + str(num_pages))
        print("offset: " + str(offset))
        results = results[offset:offset+per_page]


        return {'data': 'test_data',
                'gibs': self.gibs,
                'results': results,
                'num_pages': num_pages,
                'search_terms': search_terms,
                'page': page,
                'offset': offset,
                }

    @view_config(route_name='user_profile', renderer='templates/user/profile.jinja2')
    def user_profile(self):
        #ident = self.request.matchdict['ident']
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='user_create', renderer='templates/user/create.jinja2')
    def user_create(self):
        params = self.request.params
        if 'form.submitted' in params:
            try:
                user = User(params)
            except Exception as err:
                print(err.__class__)
                print(err)

        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='user_edit', renderer='templates/user/edit.jinja2')
    def user_edit(self):
        #identifier = self.request.matchdict['id']
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='user_delete', renderer='templates/user/delete.jinja2')
    def user_delete(self):
        #ident = self.request.matchdict['ident']
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='startup_profile', renderer='templates/startup/profile.jinja2')
    def startup_profile(self):
        ident = self.request.matchdict['ident']
        #startup = DBSession.query(Startup).filter_by(name=ident).first()
        #articles = DBSession.query(Article).filter_by(startupdex_id=ident)
        startup = DBSession.execute(
                "SELECT * FROM startups WHERE name=:param",
                {"param": ident}
                ).first()
        articles = DBSession.execute(
                "SELECT * FROM articles WHERE startupdex_id=:param",
                {"param": startup.id}
                )
        #startup = DBSession.query(Startup).all()
        #startup = Startup.query.filter_by(name=ident).first()
        #startup = DBSession.query(Startup).all()

        return {'gibs': self.gibs,
                'ident': ident,
                'startup': startup,
                'articles': articles,
                }

    @view_config(route_name='startup_browse', renderer='templates/startup/browse.jinja2')
    def startup_browse(self):
        startups = DBSession.query(Startup).all()

        return {'data': 'test_data',
                'gibs': self.gibs,
                'startups': startups,
                }

    @view_config(route_name='admin_home', renderer='templates/admin/admin_home.jinja2')
    def admin_home(self):

        return {'gibs': self.gibs,
                }

    @view_config(route_name='test2', renderer='templates/test2.jinja2')
    def test2(self):
        startup = DBSession.execute(
            "SELECT * FROM startups WHERE id=:param",
            {"param": 1}
            ).first()
        print(startup)
        return {'gibs': self.gibs,
                }

    @view_config(route_name='test3', renderer='templates/test2.jinja2')
    def test3(self):

        return {'gibs': self.gibs,
                }

    @view_config(route_name='test', renderer='templates/test.jinja2')
    def test(self):


        return {'gibs': self.gibs,
                }
