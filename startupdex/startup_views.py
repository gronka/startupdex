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
    UserHasStartups,
    Article,
    fix_integer_fields,
    name_to_local_url,
    update_fts_startups,
    CreateStartupSchema,
    ModifyStartupSchema,
    ModifySocialSchema,
    )

from startupdex.view_warlock import ViewWarlock

import logging
import colander

#import Image
import os
import datetime
import math

log = logging.getLogger(__name__)


class StartupView(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='startup_profile', renderer='templates/startup/profile.jinja2')
    def startup_profile(self):
        ident = self.request.matchdict['ident']
        #startup = DBSession.query(Startup).filter_by(name=ident).first()
        #articles = DBSession.query(Article).filter_by(startupdexid=ident)
        startup = DBSession.execute(
                "SELECT * FROM startups WHERE local_url=:param",
                {"param": ident}
                ).first()
        articles = DBSession.execute(
                "SELECT * FROM articles WHERE startupdexid=:param",
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

    @view_config(route_name='create_startup', renderer='templates/startup/create.jinja2')
    def startup_create(self):
        request = self.request
        params = request.params
        user = self.current_user

        dont_add_startup = False
        if 'form.submitted' in params:
            schema = CreateStartupSchema()
            try:
                deserialized = schema.deserialize(params)
            except colander.Invalid as e:
                request.session.flash(e, queue='errors')
                dont_add_startup = True

            if dont_add_startup is True:
                self.gibs.update(params)
                return {'gibs': self.gibs,
                        'user': self.current_user,
                        }
            else:
                url_test = False
                local_url = name_to_local_url(deserialized['name'])
                num = 1
                local_url_num = local_url
                while not url_test:
                    st = DBSession.query(Startup).filter(Startup.local_url == local_url_num).first()
                    if st is None:
                        url_test = True
                    else:
                        local_url_num = local_url + "-" + str(num)
                        num = num + 1

                userid_creator = self.current_user.id
                startup = Startup(name=deserialized['name'],
                                  local_url=local_url_num,
                                  userid_creator=int(userid_creator),
                                  country=deserialized['country'],
                                  postal_code=deserialized['postal_code'],
                                  state_province=deserialized['state_province'],
                                  city=deserialized['city'],
                                  street_address=deserialized['street_address'],
                                  tags=deserialized['tags'],
                                  contact_email=deserialized['contact_email'],
                                  company_size=deserialized['company_size'],
                                  short_info=deserialized['short_info'],
                                  about=deserialized['about'],
                                  )
                DBSession.add(startup)
                DBSession.flush()
                startup = DBSession.query(Startup).filter(Startup.local_url == local_url_num).first()
                user_has_startup = UserHasStartups(userid=user.id,
                                                   startupid=startup.id
                                                   )
                DBSession.add(user_has_startup)
                #update_fts_startups(startup)
                request.session.flash(startup.name + " added to your startups.",
                                    queue='successes')
                return HTTPFound(location=request.route_url("upload_logo", id=startup.id))

        #startups = DBSession.query(UserHasStartups).filter(User.id == user.id)
        return {'gibs': self.gibs,
                'user': self.current_user,
                #'startups': startups,
                }


    @view_config(route_name='startup_browse', renderer='templates/startup/browse.jinja2')
    def startup_browse(self):
        request = self.request
        params = request.params
        _limit = 200

        if "page" in params:
            page = int(params["page"])
        else:
            page = 1
        #per_page = param["per_page"]
        per_page = 10

        startups = DBSession.query(Startup).limit(_limit).all()

        rowcount = len(startups)
        num_pages = math.ceil(rowcount / per_page)
        offset = per_page * page - per_page

        startups = startups[offset:offset+per_page]

        if rowcount == 200:
            num_results = "200+"
        else:
            num_results = str(rowcount)

        return {'gibs': self.gibs,
                'startups': startups,
                'num_pages': num_pages,
                'page': page,
                'offset': offset,
                'rowcount': rowcount,
                'num_results': num_results,
                }

    @view_config(route_name='startups_by_state', renderer='templates/startup/sort_by_state.jinja2')
    def startups_by_state(self):
        request = self.request
        params = request.params
        state = request.matchdict['state'].replace("_", " ")
        _limit = 200

        if "page" in params:
            page = int(params["page"])
        else:
            page = 1
        #per_page = param["per_page"]
        per_page = 10

        #startups = DBSession.query(Startup).all()
        #startups = DBSession.query(Startup).filter(Startup.state_province == )
        startups = DBSession.query(Startup.id,
                                   Startup.name,
                                   Startup.short_info,
                                   Startup.local_url,
                                   Startup.logo_url,
                                   ).filter(Startup.state_province == state).limit(_limit).all()
        rowcount = len(startups)
        num_pages = math.ceil(rowcount / per_page)
        offset = per_page * page - per_page

        startups = startups[offset:offset+per_page]

        if rowcount == 200:
            num_results = "200+"
        else:
            num_results = str(rowcount)

        return {'gibs': self.gibs,
                'startups': startups,
                'state': state,
                'num_pages': num_pages,
                'page': page,
                'offset': offset,
                'rowcount': rowcount,
                'num_results': num_results,
                }

    @view_config(route_name='startups_by_city', renderer='templates/startup/sort_by_city.jinja2')
    def startups_by_city(self):
        request = self.request
        params = request.params
        city = request.matchdict['city']
        city = request.matchdict['city'].replace("_", " ")
        _limit = 200

        if "page" in params:
            page = int(params["page"])
        else:
            page = 1
        #per_page = param["per_page"]
        per_page = 10

        #startups = DBSession.query(Startup).all()
        #startups = DBSession.query(Startup).filter(Startup.state_province == )
        startups = DBSession.query(Startup.id,
                                   Startup.name,
                                   Startup.short_info,
                                   Startup.local_url,
                                   Startup.logo_url,
                                   ).filter(Startup.city == city).limit(_limit).all()
        rowcount = len(startups)
        num_pages = math.ceil(rowcount / per_page)
        offset = per_page * page - per_page

        startups = startups[offset:offset+per_page]

        if rowcount == 200:
            num_results = "200+"
        else:
            num_results = str(rowcount)

        return {'gibs': self.gibs,
                'startups': startups,
                'city': city,
                'num_pages': num_pages,
                'page': page,
                'offset': offset,
                'rowcount': rowcount,
                'num_results': num_results,
                }

    @view_config(route_name='startups_by_country', renderer='templates/startup/sort_by_country.jinja2')
    def startups_by_country(self):
        request = self.request
        params = request.params
        country = request.matchdict['country']
        country = request.matchdict['country'].replace("_", " ")
        _limit = 200

        if "page" in params:
            page = int(params["page"])
        else:
            page = 1
        #per_page = param["per_page"]
        per_page = 10

        #startups = DBSession.query(Startup).all()
        #startups = DBSession.query(Startup).filter(Startup.state_province == )
        startups = DBSession.query(Startup.id,
                                   Startup.name,
                                   Startup.short_info,
                                   Startup.local_url,
                                   Startup.logo_url,
                                   ).filter(Startup.country == country).limit(_limit).all()
        rowcount = len(startups)
        num_pages = math.ceil(rowcount / per_page)
        offset = per_page * page - per_page

        startups = startups[offset:offset+per_page]

        if rowcount == 200:
            num_results = "200+"
        else:
            num_results = str(rowcount)

        return {'gibs': self.gibs,
                'startups': startups,
                'country': country,
                'num_pages': num_pages,
                'page': page,
                'offset': offset,
                'rowcount': rowcount,
                'num_results': num_results,
                }

    @view_config(route_name='upload_logo', renderer='templates/startup/upload_logo.jinja2')
    def upload_logo(self):
        request = self.request
        params = request.params
        startupid = request.matchdict['id']
        startup = DBSession.query(Startup).filter(Startup.id == startupid).first()

        if 'form.submitted' in params:
            #TODO: implement write_basic_image() function
            image = request.params['logo']
            folder_group = str(int(math.ceil(startup.id / 10000.0) * 10000.0))
            imagename = str(startupid) + '.png'
            logo_url = 'startups/logos/' + folder_group + '/' + imagename
            startup.logo_url = logo_url
            thumb_url = 'startups/thumbs/' + folder_group + '/' + imagename
            startup.thumb_url = thumb_url

            logo_dir = '/var/www/startupdex/images/startups/logos/' + folder_group + '/'
            d = os.path.dirname(logo_dir)
            try:
                os.stat(d)
            except:
                os.mkdir(d)
            logo_path = logo_dir + imagename
            file_path = os.path.join(logo_path)
            open(file_path, 'wb').write(image.file.read())

            thumb_dir = '/var/www/startupdex/images/startups/thumbs/' + folder_group + '/'
            d = os.path.dirname(thumb_dir)
            try:
                os.stat(d)
            except:
                os.mkdir(d)
            thumb_path = thumb_dir + imagename
            file_path = os.path.join(thumb_path)
            open(file_path, 'wb').write(image.file.read())

            request.session.flash("Startup logo uploaded.",
                                queue='successes')
            return HTTPFound(location=request.route_url("manage_startups"))

        return {'gibs': self.gibs,
                'user': self.current_user,
                'startup': startup,
                }

    @view_config(route_name='modify_startup', renderer='templates/startup/modify_startup.jinja2')
    def modify_startup(self):
        request = self.request
        startupid = request.matchdict['id']
        startup = DBSession.query(Startup).filter(Startup.id == startupid).first()

        return {'gibs': self.gibs,
                'user': self.current_user,
                'startup': startup,
                }

    @view_config(name='modify_startup_save_changes.json', renderer='json')
    def modify_startup_save_changes(self):
        request = self.request
        startup_json = request.json_body
        schema = ModifyStartupSchema()
        try:
            deserialized = schema.deserialize(startup_json)
        except colander.Invalid as e:
            request.session.flash(e, queue='errors')
            return ("Fail, reload")

        startup = DBSession.query(Startup.id).filter(Startup.local_url == startup_json['local_url']).first()
        if startup is not None:
            if startup_json['startupid'] != str(startup.id):
                request.session.flash("Startupdex Hyperlink is taken", queue='errors')
                return ("Fail, reload")
        startup = DBSession.query(Startup).filter(Startup.id == startup_json['startupid']).first()
        for key, prop in deserialized.items():
            if prop == "None":
                prop = None
            elif prop == "":
                prop = None
            elif prop == "False":
                prop = False
            elif prop == "True":
                prop = True
            if prop != getattr(startup, key):
                setattr(startup, key, prop)
        startup.updated_at = datetime.datetime.utcnow()
        return ("Success")

    @view_config(route_name='modify_social', renderer='templates/startup/modify_social.jinja2')
    def modify_social(self):
        request = self.request
        startupid = request.matchdict['id']
        startup = DBSession.query(Startup).filter(Startup.id == startupid).first()

        return {'gibs': self.gibs,
                'user': self.current_user,
                'startup': startup,
                }

    @view_config(name='modify_social_save_changes.json', renderer='json')
    def modify_social_save_changes(self):
        request = self.request
        startup_json = request.json_body
        schema = ModifySocialSchema()
        try:
            deserialized = schema.deserialize(startup_json)
        except colander.Invalid as e:
            request.session.flash(e, queue='errors')
            return ("Fail, reload")

        startup = DBSession.query(Startup).filter(Startup.id == startup_json['startupid']).first()
        for key, prop in deserialized.items():
            if prop == "None":
                prop = None
            elif prop == "":
                prop = None
            elif prop == "False":
                prop = False
            elif prop == "True":
                prop = True
            if prop != getattr(startup, key):
                setattr(startup, key, prop)
        startup.updated_at = datetime.datetime.utcnow()
        return ("Success")

    @view_config(route_name='modify_startup_delete', renderer='templates/startup/modify_startup_delete.jinja2')
    def modify_startup_delete(self):
        request = self.request
        params = request.params
        startupid = request.matchdict['id']
        startup = DBSession.query(Startup).filter(Startup.id == startupid).first()
        print(startup.hidden)

        if 'form.submitted' in params:
            if 'hide_startup' in params:
                startup.hidden = True
                request.session.flash(startup.name + ' is now hidden.', queue='warnings')
            else:
                startup.hidden = False
                request.session.flash(startup.name + ' is now visible.', queue='warnings')
            if params['delete_startup'] == "DELETE":
                DBSession.delete(startup)
                request.session.flash(startup.name + ' has been deleted.', queue='errors')
                return HTTPFound(location=request.route_url("manage_startups"))

        return {'gibs': self.gibs,
                'user': self.current_user,
                'startup': startup,
                }

    @view_config(name='test_local_url.json', renderer='json')
    def test_local_url(self):
        request = self.request
        josh = request.json_body

        startup = DBSession.query(Startup).filter(Startup.local_url == josh['local_url']).first()
        if startup is not None:
            return ("Taken")
        else:
            return ("Success")

