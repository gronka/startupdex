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
    #FTSStartup,
    fix_integer_fields,
    get_images_from_angelco,
    #update_startup_fts,
    )

from startupdex.view_warlock import ViewWarlock

import json
import requests
from datetime import datetime

import logging

from peewee import *
from playhouse.sqlite_ext import *

log = logging.getLogger(__name__)


class AdminView(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='db_users', renderer='templates/admin/db_users.jinja2')
    def db_users(self):
        newest_user = DBSession.query(User).order_by(desc("id")).first()
        newest_user_list = []
        if newest_user is not None:
            for i in range(newest_user.id - 10, newest_user.id + 1):
                user = DBSession.query(User).filter(User.id == i).first()
                newest_user_list.append(user)
        else:
            newest_user = {"id": 0}
        return {'gibs': self.gibs,
                'newest_user': newest_user,
                'newest_user_list': newest_user_list,
                }

    @view_config(name='admin_update_user.json', renderer='json')
    def admin_update_user(self):
        request = self.request
        user_json = request.json_body
        user = DBSession.query(User).filter(User.id == user_json['id']).first()
        for key, prop in user_json.items():
            if prop == "None":
                prop = None
            elif prop == "":
                prop = None
            elif prop == "False":
                prop = False
            elif prop == "True":
                prop = True
            if prop != getattr(user, key):
                setattr(user, key, prop)
        return ("")

    @view_config(name='admin_remove_user.json', renderer='json')
    def admin_remove_user(self):
        request = self.request
        user_id = request.json_body['user_id']
        user = DBSession.query(User).filter(User.id == user_id).first()
        DBSession.delete(user)
        return ("")

    @view_config(route_name='db_angelco', renderer='templates/admin/db_angelco.jinja2')
    def db_angelco(self):
        angelco_first_listing = DBSession.query(AngelCoMirror).first()
        angelco_last_listing = DBSession.query(AngelCoMirror).order_by(desc("id")).first()
        startupdex_first_listing = DBSession.query(Startup).first()
        startupdex_last_listing = DBSession.query(Startup).order_by(desc("id")).first()
        print("++++++++++++++++++++++++++++++++")
        #print(str(type(startupdex_last_listing.first())))
        #print(startupdex_last_listing.name)
        if angelco_last_listing is None:
            angelco_last_listing = {"id": 0}
        if angelco_first_listing is None:
            angelco_first_listing = {"id": 0}
        #if startupdex_last_listing is None:
            #startupdex_last_listing = {"name": "table is empty"}
            #startupdex_last_listing.name = "table is empty"
        print(type(startupdex_last_listing))
        # this also works
        #angelco_last_listing = DBSession.query(AngelCoMirror).order_by(AngelCoMirror.id.desc()).first()
        startupdex_update_point = DBSession.execute(
            "SELECT id FROM startups WHERE status=:param ORDER BY id DESC",
            {"param": str(1)}
            ).first()
        print("++++++++++++++++++++++++++++++++")
        print("++++++++++++++++++++++++++++++++")
        print(str(type(startupdex_update_point)))
        startupdex_update_point_list = []
        if startupdex_update_point is not None:
            #print(str(startupdex_update_point.id))
            for i in range(startupdex_update_point.id - 5, startupdex_update_point.id + 1):
                startupdex_update_point_list.append(DBSession.execute(
                    "SELECT * FROM startups WHERE id=:param",
                    {"param": i}
                    ).first())
        else:
            startupdex_update_point = {"id": 0}

        angelcomirror_update_point = DBSession.execute(
            "SELECT id FROM angelcomirror ORDER BY id DESC",
            {"param": str(1)}
            ).first()
        angelcomirror_update_point_list = []
        if angelcomirror_update_point is not None:
            print("++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++")
            print(str(angelcomirror_update_point.id))
            for i in range(angelcomirror_update_point.id - 30, angelcomirror_update_point.id + 1):
                angelcomirror_update_point_list.append(DBSession.execute(
                    "SELECT * FROM angelcomirror WHERE id=:param",
                    {"param": i}
                    ).first())
        else:
            angelcomirror_update_point = {"id": 0}



        return {'gibs': self.gibs,
                'angelco_first_listing': angelco_first_listing,
                'angelco_last_listing': angelco_last_listing,
                'startupdex_first_listing': startupdex_first_listing,
                'startupdex_last_listing': startupdex_last_listing,
                'startupdex_update_point': startupdex_update_point,
                'startupdex_update_point_list': startupdex_update_point_list,
                'angelcomirror_update_point': angelcomirror_update_point,
                'angelcomirror_update_point_list': angelcomirror_update_point_list,
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

                    fix_integer_fields(query_dict)


                    new_angelco_mirror = AngelCoMirror(**query_dict)
                    new_startup = Startup(name=query_dict['name'],
                                          userid_creator=0,
                                          status="",
                                          locations=query_dict['locations'],
                                          about=query_dict['community_profile'],
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
            #current_angelco = DBSession.select(AngelCoMirror).where(AngelCoMirror.startupdexid==i)
            print("+++++++++++++++++++++++++++")
            print("i is now " + str(i))
            #ca = current_angelco
            ca = DBSession.execute(
                "SELECT * FROM angelcomirror WHERE startupdexid=:param",
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

            ca_string = ca.created_at.split('-')
            year = ca_string[0]
            month = ca_string[1]
            ca_string = ca_string[2].split('T')
            day = ca_string[0]
            ca_string = ca_string[1].split(':')
            hour = ca_string[0]
            minute = ca_string[1]
            ca_string = ca_string[2].split('Z')
            second = ca_string[0]
            created_at = datetime.datetime(year=year,
                                           month=month,
                                           day=day,
                                           hour=hour,
                                           minute=minute,
                                           second=second)

            ua_string = ua.created_at.split('-')
            year = ua_string[0]
            month = ua_string[1]
            ua_string = ua_string[2].split('T')
            day = ua_string[0]
            ua_string = ua_string[1].split(':')
            hour = ua_string[0]
            minute = ua_string[1]
            ua_string = ua_string[2].split('Z')
            second = ua_string[0]
            updated_at = datetime.datetime(year=year,
                                           month=month,
                                           day=day,
                                           hour=hour,
                                           minute=minute,
                                           second=second)

            #if ca.status == '':
                #angelco_status = -1
            #else:
                #angelco_status = int(ca.status)

            #if ca.company_size == '':
                #company_size = 0
            #else:
                #company_size = int(ca.company_size)

            company_size = ca.company_size

            folder_group = str(int(math.ceil(i / 10000.0) * 10000.0))
            thumb_url = "startups/thumbs/" + folder_group+"/"+str(i) + ".jpg"
            logo_url = "startups/logos/" + folder_group+"/"+str(i) + ".jpg"

            test_exists = DBSession.execute(
                "SELECT * FROM startups WHERE id=:param",
                {"param": str(i)}
                ).first()
            print("=====================")
            print("=====================")
            print("=====================")
            print(str(type(test_exists)))

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

            if test_exists is None:
                startupdex = Startup(
                    # already transferred - defaults
                    #id=ca.startupdexid,
                    name=name,
                    local_url=local_url,
                    #status="",
                    #locations=query_dict['locations'],
                    about=ca.community_profile,
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
                    #created_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M'),
                    #updated_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M'),
                    created_at=created_at,
                    updated_at=updated_at,
                    home_url=ca.company_url,
                    twitter_url=ca.twitter_url,
                    facebook_url=ca.facebook_url,
                    logo_url=logo_url,
                    thumb_url=thumb_url,
                    blog_url=ca.blog_url,
                    tags=ca.high_concept,
                    short_info=ca.product_desc,
                    angelco_status=ca.status,
                    company_size=company_size,
                    )
                print(startupdex)
                DBSession.add(startupdex)

                if startupdex.short_info is None:
                    startupdex.short_info = "na"
                if startupdex.about is None:
                    startupdex.about = "na"
                if type(startupdex.about) is int:
                    startupdex.about = "na"

                print(startupdex.tags)
                print(startupdex.short_info)
                print(startupdex.about)
                print(str(type(startupdex.about)))
                # adds startup to searchable database
                #update_startup_fts(startupdex)
                #FTSStartup.create(
                    #startupdexid=int(i),
                    #angelco_id=str(ca.id),
                    #name=name,
                    #content='\n'.join((startupdex.tags,
                                    #startupdex.short_info,
                                    #startupdex.about)),
                    #tags=startupdex.tags,
                    #short_info=startupdex.short_info,
                    #thumb_url=startupdex.thumb_url,
                #)

                # get image
                get_images_from_angelco(i, ca.thumb_url, ca.logo_url)

