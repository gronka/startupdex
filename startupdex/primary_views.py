#from pyramid.response import Response
from pyramid.view import (
    view_config,
    #notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPFound,
    #HTTPNotFound,
    )

from pyramid.response import FileResponse

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
    FrontpageStartup,
    fix_integer_fields,
    #FTSStartup,
    startup_search,
    send_mail,
    )

from startupdex.view_warlock import ViewWarlock

import json
import requests
import math
import os
from random import shuffle
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
        startups = DBSession.query(Startup).join(FrontpageStartup).all()
        shuffle(startups)
        try:
            focused_startup = startups.pop()
        except Exception:
            focused_startup = {"name": "no startups listed"}

        self.gibs['sidebar_startups'] = startups[6:11]

        return {'gibs': self.gibs,
                'startup': focused_startup,
                'startups': startups[:6],
                }

    @view_config(route_name='frontpage2', renderer='templates/frontpage2.jinja2')
    def frontpage2(self):
        startups = DBSession.query(Startup).join(FrontpageStartup).all()
        shuffle(startups)
        try:
            focused_startup = startups.pop()
        except Exception:
            focused_startup = {"name": "no startups listed"}

        return {'gibs': self.gibs,
                'startups': startups[:6],
                'startup': focused_startup,
                }

    @view_config(route_name='search_redirect', renderer='templates/search.jinja2')
    def search_redirect(self):
        params = self.request.params
        print(params)
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='search', renderer='templates/search/search.jinja2')
    def search(self):
        params = self.request.params
        search_terms = params["search_terms"]
        #print(search_terms)
        if "page" in params:
            page = int(params["page"])
        else:
            page = 1
        #per_page = param["per_page"]
        per_page = 10
        #print("number of results: " + str(rowcount))
        #print("number of pages: " + str(num_pages))
        #print("offset: " + str(offset))

        results = startup_search(search_terms)
        rowcount = len(results)
        num_pages = math.ceil(rowcount / per_page)
        offset = per_page * page - per_page

        results = results[offset:offset+per_page]

        print(type(results))

        return {'gibs': self.gibs,
                'results': results,
                'rowcount': rowcount,
                'num_pages': num_pages,
                'search_terms': search_terms,
                'page': page,
                'offset': offset,
                }


    @view_config(name='postal_code_autorefresh.json', renderer='json')
    def postal_code_autorefresh(self):
        request = self.request

        city = None
        state_province = None
        postal_code = None
        country = None
        if 'locations' in ca:
            # take the city from the json, and get the state if it's
            # there
            try:
                locations = json.loads(ca['locations'])
                loc = locations[0]['display_name'].split(", ")
                city = loc[0]
            except:
                pass
            try:
                state_province = loc[1]
            except:
                pass

        if city is not None:
            search_string = city.replace(" ", "+") + ",+"
        if state_province is not None:
            search_string += state_province.replace(" ", "+") + ",+"
        if postal_code is not None:
            search_string += postal_code.replace(" ", "+") + ",+"
        if country is not None:
            search_string += country.replace(" ", "+") + ",+"
        geocode = "http://maps.googleapis.com/maps/api/geocode/json?sensor=false&address=" + search_string
        #print(geocode)
        geocode = requests.get(geocode)
        results = json.loads(geocode.text)['results']
        #print("GEOCODEO")
        #pprint.pprint(results)

        if type(results) is list:
            results = results.pop()
        for component in results['address_components']:
            if 'country' in component['types']:
                country = component['long_name']
            elif 'administrative_area_level_1' in component['types']:
                state_province = component['long_name']
            elif 'administrative_area_level_3' in component['types']:
                city = component['long_name']
            elif 'locality' in component['types']:
                city = component['long_name']
            elif 'postal_code' in component['types']:
                postal_code = component['long_name']

        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']


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
        #sender="noreply@startupdex.com"
        #recipients = ["mr.gronka@gmail.com", "taylor@localhost.localdomain"]
        sender="Startupdex <noreply@startupdex.com>"
        recipients = ["Taylor Gronka <mr.gronka@gmail.com>",]
        send_mail(to=recipients,
                  fro=sender,
                  subject=subject,
                  text=body
                  )

        return {'gibs': self.gibs,
                }

    @view_config(route_name='favicon')
    def favicon_view(self):
        here = os.path.dirname('/var/www/startupdex/images/')
        icon = os.path.join(here, 'blank-favicon.ico')
        return FileResponse(icon, request=self.request)
