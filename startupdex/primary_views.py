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
    #FTSStartup,
    startup_search,
    send_mail,
    )

from startupdex.view_warlock import ViewWarlock

import json
import requests
import math
from datetime import datetime

import logging

from peewee import *
from playhouse.sqlite_ext import *

from pyramid_mailer import get_mailer
from pyramid_mailer.mailer import Mailer
from pyramid_mailer.message import Message

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

        #results = (FTSStartup
                #.select(
                    #FTSStartup,
                    #FTSStartup.bm25(FTSStartup.content).alias('score'))
                #.where(FTSStartup.match( search_terms ))
                #.order_by(SQL('score').desc())
                #)
        num_pages = math.ceil(results.count() / per_page)
        offset = per_page * page - per_page
        print("now the results")
        print(results)
        print("number of results: " + str(results.count()))
        print("number of pages: " + str(num_pages))
        print("offset: " + str(offset))
        results = results[offset:offset+per_page]

        test = startup_search(search_terms)
        print("=======================")
        print("=======================")
        print(test)
        print("=======================")



        return {'data': 'test_data',
                'gibs': self.gibs,
                'results': results,
                'num_pages': num_pages,
                'search_terms': search_terms,
                'page': page,
                'offset': offset,
                }


    @view_config(route_name='admin_home', renderer='templates/admin/admin_home.jinja2')
    def admin_home(self):

        return {'gibs': self.gibs,
                }

    @view_config(route_name='test2', renderer='templates/test2.jinja2')
    def test2(self):
        #startup = DBSession.execute(
            #"SELECT * FROM startups WHERE id=:param",
            #{"param": 1}
            #).first()
        #print(startup)

        request = self.request

        body = """<p>Thanks for joining!</p>
        <p>Click the following link to complete your registration: </p>
        {confirmation_url}
        """.format(confirmation_url='linklol')
        message = Message(subject="Startupdex: New member confirmation",
                            #sender="mail@startupdex.com",
                            sender="taylor@localhost.localdomain",
                            recipients=["mr.gronka@gmail.com", "taylor@localhost.localdomain"],
                            body=body,
                            )
        #mailer = Mailer()
        #mailer = get_mailer(request)
        mailer = request.registry['mailer']
        mailer.send(message)
        #mailer.send_to_queue(message)
        #mailer.send_immediately(message, fail_silently=False)
        return {'gibs': self.gibs,
                }

    @view_config(route_name='test3', renderer='templates/test2.jinja2')
    def test3(self):

        return {'gibs': self.gibs,
                }

    @view_config(route_name='contact_us', renderer='templates/test.jinja2')
    def contact_us(self):
        from pyramid_mailer.message import Message
        request = self.request
        body = """<p>Thanks for joining!</p>
        <p>Click the following link to complete your registration: </p>
        {confirmation_url}
        """.format(confirmation_url="goodurl.com")
        subject="Startupdex: New Member Confirmation"
        sender="noreply@startupdex.com"
        recipients = ["mr.gronka@gmail.com", "taylor@localhost.localdomain"]
        send_mail(to=recipients,
                  fro=sender,
                  subject=subject,
                  text=body
                  )

        return {'gibs': self.gibs,
                }
