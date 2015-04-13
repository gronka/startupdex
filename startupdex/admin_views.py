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
    FTSStartup,
    fix_integer_fields,
    get_images_from_angelco,
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
    @view_config(route_name='db_angelco', renderer='templates/admin/db_angelco.jinja2')
    def db_angelco(self):
        startups = DBSession.query(Startup).all()
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
        if startupdex_update_point is not None:
            print("++++++++++++++++++++++++++++++++")
            print("++++++++++++++++++++++++++++++++")
            print(str(startupdex_update_point.id))
            startupdex_update_point_list = []
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

        print(angelcomirror_update_point_list)


        return {'gibs': self.gibs,
                'startups': startups,
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
                #id=ca.startupdex_id,
                name=name,
                #status="",
                #locations=query_dict['locations'],
                long_info=ca.community_profile,
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
                updated_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M'),
                home_url=ca.company_url,
                twitter_url=ca.twitter_url,
                facebook_url=ca.facebook_url,
                logo_url=ca.logo_url,
                thumb_url=ca.thumb_url,
                blog_url=ca.blog_url,
                quick_info=ca.high_concept,
                short_info=ca.product_desc,
                angelco_status=ca.status,
                company_size=company_size,
                )
            print(startupdex)
            DBSession.add(startupdex)

            if startupdex.quick_info is None:
                startupdex.quick_info = "na"
            if startupdex.short_info is None:
                startupdex.short_info = "na"
            if startupdex.long_info is None:
                startupdex.long_info = "na"
            if type(startupdex.long_info) is int:
                startupdex.long_info = "na"

            print(startupdex.quick_info)
            print(startupdex.short_info)
            print(startupdex.long_info)
            print(str(type(startupdex.long_info)))
            # adds startup to searchable database
            FTSStartup.create(
                startupdex_id=str(i),
                angelco_id=str(ca.id),
                name=name,
                content='\n'.join((startupdex.quick_info,
                                   startupdex.short_info,
                                   startupdex.long_info)),
                quick_info=startupdex.quick_info,
                short_info=startupdex.short_info,
                thumb_url=startupdex.thumb_url,
            )

            # get image
            get_images_from_angelco(i, startupdex.thumb_url, startupdex.logo_url)

