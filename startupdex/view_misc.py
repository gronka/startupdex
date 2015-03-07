from pyramid.response import Response
from pyramid.view import (
    view_config,
    notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Startup,
    AngelCoMirror,
    )

from startupdex.view_warlock import ViewWarlock

import json
import requests

import logging

# development only
import pprint


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
        identifier = self.request.matchdict['id']
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='startup_profile', renderer='templates/startup/profile.jinja2')
    def startup_profile(self):
        ident = self.request.matchdict['ident']
        startup = DBSession.query(Startup).filter_by(name=ident).first()
        #startup = DBSession.query(Startup).all()
        #startup = Startup.query.filter_by(name=ident).first()
        #startup = DBSession.query(Startup).all()

        return {'data': 'test_data',
                'gibs': self.gibs,
                'ident': ident,
                'startup': startup,
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

        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='db_angelco', renderer='templates/admin/db_angelco.jinja2')
    def db_angelco(self):
        startups = DBSession.query(Startup).all()

        return {'data': 'test_data',
                'gibs': self.gibs,
                'startups': startups,
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









    #pagename = request.matchdict['pagename']
    #page = DBSession.query(Page).filter_by(name=pagename).first()
    #if page is None:
        #return HTTPNotFound('No such page')

    #def check(match):
        #word = match.group(1)
        #exists = DBSession.query(Page).filter_by(name=word).all()
        #if exists:
            #view_url = request.route_url('view_page', pagename=word)
            #return '<a href="%s">%s</a>' % (view_url, cgi.escape(word))
        #else:
            #add_url = request.route_url('add_page', pagename=word)
            #return '<a href="%s">%s</a>' % (add_url, cgi.escape(word))

    #content = publish_parts(page.data, writer_name='html')['html_body']
    #content = wikiwords.sub(check, content)
    #edit_url = request.route_url('edit_page', pagename=pagename)
    #return dict(page=page, content=content, edit_url=edit_url)

#@view_config(route_name='startup/create', renderer='templates/edit.pt')
#def add_page(request):
    #pagename = request.matchdict['pagename']
    #if 'form.submitted' in request.params:
        #body = request.params['body']
        #page = Page(name=pagename, data=body)
        #DBSession.add(page)
        #return HTTPFound(location = request.route_url('view_page',
                                                      #pagename=pagename))
    #save_url = request.route_url('add_page', pagename=pagename)
    #page = Page(name='', data='')
    #return dict(page=page, save_url=save_url)

#@view_config(route_name='startup/edit', renderer='templates/edit.pt')
#def edit_page(request):
    #pagename = request.matchdict['pagename']
    #page = DBSession.query(Page).filter_by(name=pagename).one()
    #if 'form.submitted' in request.params:
        #page.data = request.params['body']
        #DBSession.add(page)
        #return HTTPFound(location = request.route_url('view_page',
                                                      #pagename=pagename))
    #return dict(
        #page=page,
        #save_url = request.route_url('edit_page', pagename=pagename),
        #)


#@view_config(route_name='home', renderer='templates/mytemplate.pt')
#def my_view(request):
    #try:
        #one = DBSession.query(Page).filter(MyModel.name == 'one').first()
    #except DBAPIError:
        #return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #return {'one': one, 'project': 'startupdex'}


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
