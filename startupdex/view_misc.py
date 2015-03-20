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
    )

from startupdex.view_warlock import ViewWarlock

import json
import requests
from datetime import datetime

import logging

# development only
#import pprint


log = logging.getLogger(__name__)


class ViewFrontpage(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='frontpage', renderer='templates/frontpage.jinja2')
    def frontpage(self):
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='search', renderer='templates/search.jinja2')
    def search(self):
        return {'data': 'test_data',
                'gibs': self.gibs,
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

    @view_config(route_name='db_angelco', renderer='templates/admin/db_angelco.jinja2')
    def db_angelco(self):
        startups = DBSession.query(Startup).all()
        angelco_first_listing = DBSession.query(AngelCoMirror).first()
        angelco_last_listing = DBSession.query(AngelCoMirror).order_by(desc("id")).first()
        startupdex_first_listing = DBSession.query(Startup).first()
        startupdex_last_listing = DBSession.query(Startup).order_by(desc("id")).first()
        print("++++++++++++++++++++++++++++++++")
        #print(str(type(startupdex_last_listing.first())))
        print(startupdex_last_listing.name)
        if angelco_last_listing is None:
            angelco_last_listing = {"id": 0}
        if angelco_first_listing is None:
            angelco_first_listing = {"id": 0}
        # this also works
        #angelco_last_listing = DBSession.query(AngelCoMirror).order_by(AngelCoMirror.id.desc()).first()

        return {'gibs': self.gibs,
                'startups': startups,
                'angelco_first_listing': angelco_first_listing,
                'angelco_last_listing': angelco_last_listing,
                'startupdex_first_listing': startupdex_first_listing,
                'startupdex_last_listing': startupdex_last_listing,
                }

    @view_config(name='db_angelco_get.json', renderer='json')
    def db_angelco_get(self):
        url = "https://api.angel.co/1/startups/"
        rangestart = int(self.request.json_body['rangestart'])
        rangeend = int(self.request.json_body['rangei']) + rangestart + 1

        print("chyeah")
        for i in range(rangestart, rangeend):
            print("+++++++++++++++++++++++++++++++")
            print("getting startup ID " + str(i))
            print("+++++++++++++++++++++++++++++++")
            query = requests.get(url+str(i))
            query_dict = json.loads(query.text)
            #pp = pprint.PrettyPrinter(indent=4)
            #pp.pprint(query_dict)

            try:
                if 'success' in query_dict:
                    print("+++++++++++++++++++++++++++++++")
                    log.debug("startup ID " + str(i) + " at angel.co returned false success boolean")
                    print("startup ID " + str(i) + " at angel.co returned false success boolean")
                    print("+++++++++++++++++++++++++++++++")
                elif query_dict['hidden'] is True:
                    print("+++++++++++++++++++++++++++++++")
                    log.debug("startup ID " + str(i) + " at angel.co is hidden")
                    print("startup ID " + str(i) + " at angel.co is hidden")
                    print("+++++++++++++++++++++++++++++++")
                else:
                    for key, value in query_dict.items():
                        if bool(value) is False:
                            query_dict[key] = ""
                        if type(value) is list or type(value) is dict:
                            query_dict[key] = json.dumps(value)

                    new_angelco_mirror = AngelCoMirror(**query_dict)
                    new_startup = Startup(name=query_dict['name'],
                                          status="",
                                          locations=query_dict['locations'],
                                          long_info=query_dict['community_profile'],
                                          angelco_quality=query_dict['quality'],
                                          angelco_follower_count=query_dict['follower_count'],
                                          updated_at=query_dict['updated_at'],
                                          angelco_status=50,  # status of 50 implies what options are set here, currently
                                          blog_url=query_dict['blog_url'],
                                          twitter_url=query_dict['twitter_url'],
                                          facebook_url=query_dict['twitter_url'],
                                          )

                    DBSession.add(new_angelco_mirror)
                    DBSession.add(new_startup)
            except KeyError:
                print("+++++++++++++++++++++++++++++++")
                log.debug("startup ID " + str(i) + " at angel.co returned a KeyError")
                print("startup ID " + str(i) + " at angel.co returned a KeyError")
                print("+++++++++++++++++++++++++++++++")

    @view_config(name='db_angelco_push_to_startupdex.json', renderer='json')
    def db_angelco_push_to_startupdex(self):
        rangestart = int(self.request.json_body['rangestart'])
        rangeend = int(self.request.json_body['rangei']) + rangestart + 1
        #start_at = DBSession.query(AngelCoMirror).filter_by
        #ident = 1000000;
        #angelco_startup = DBSession.query(AngelCoMirror).filter_by(name=ident).first()

        for i in range(rangestart, rangeend):
            #current_angelco = DBSession.query(AngelCoMirror).where(AngelCoMirror.id==i)
            #current_angelco = DBSession.select(AngelCoMirror).where(AngelCoMirror.startupdex_id==i)
            print("+++++++++++++++++++++++++++")
            print("i is now " + str(i))
            #ca = current_angelco
            ca = DBSession.execute(
                "SELECT * FROM angelcomirror WHERE startupdex_id=:param",
                {"param": str(i)}
                ).first()
            print("type of ca " + str(type(ca)))
            if ca is None:
                break
            #print(str(ca.returns_rows))
            #print(str(ca.first()))
            if "locations" in ca:
                print(ca.locations)
                locations = json.loads(ca.locations)
                print(locations)
                headquarters = None
                country = None
                state_province = None
                city = None
            else:
                headquarters = None
                country = None
                state_province = None
                city = None

            print(ca.name)
            name = ca.name.replace('/', '')

            #if ca.status == '':
                #angelco_status = -1
            #else:
                #angelco_status = int(ca.status)

            #if ca.company_size == '':
                #company_size = 0
            #else:
                #company_size = int(ca.company_size)

            company_size = ca.company_size

            startupdex = Startup(
                # already transferred - defaults
                name=name,
                #status="",
                #locations=query_dict['locations'],
                #long_info=query_dict['community_profile'],
                #angelco_quality=query_dict['quality'],
                #angelco_follower_count=query_dict['follower_count'],
                #updated_at=query_dict['updated_at'],
                #angelco_status=50,  # status of 50 implies what options are set here, currently
                #blog_url=query_dict['blog_url'],
                #twitter_url=query_dict['twitter_url'],
                #facebook_url=query_dict['twitter_url'],
                status="1",
                headquarters=headquarters,
                country=country,
                state_province=state_province,
                city=city,
                created_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M'),
                home_url=ca.company_url,
                twitter_url=ca.twitter_url,
                facebook_url=ca.facebook_url,
                logo_url=ca.logo_url,
                logo_thumb_url=ca.thumb_url,
                blog_url=ca.blog_url,
                quick_info=ca.high_concept,
                short_info=ca.product_desc,
                angelco_status=ca.status,
                company_size=company_size,
                )
            print(startupdex)
            DBSession.add(startupdex)


    # still need to fix
    #status = Column(Text)
    #startupdex_url = Column(Text)
    #logo_url = Column(Text)
    #logo_thumb_url = Column(Text)

    #header_info = Column(Text)
    #quick_info = Column(Text)
    #short_info = Column(Text)
    #long_info = Column(Text)
    #primary_category = Column(Text)
    #categories = Column(Text)
    #founders = Column(Text)
    #about = Column(Text)
    #startupdex_ranking = Column(Text)
    #created_at = Column(Text)
    #updated_at = Column(Text)

conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_startupdex_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
