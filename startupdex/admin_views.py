#from pyramid.response import Response
from pyramid.view import (
    view_config,
    #notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPFound,
    #HTTPNotFound,
    )

from sqlalchemy.exc import IntegrityError
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
    Category,
    UserHasStartups,
    StartupHasCategories,
    FrontpageStartup,
    fix_integer_fields,
    get_images_from_angelco,
    name_to_local_url,
    add_startup_has_category,
    rem_startup_has_category,
    )

from startupdex.view_warlock import ViewWarlock

import json
import math
import pprint
import requests
import datetime

import logging

#from peewee import *
#from playhouse.sqlite_ext import *

logger = logging.getLogger(__name__)


def startups_for_scroller(results):
    startups = []
    for result in results:
        startups.append({"id": result.id,
                            "name": result.name,
                            "logo_url": result.logo_url,
                            "local_url": result.local_url,
                            "short_info": result.short_info[:100],
                        })
    return startups


class AdminView(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='admin_frontpage', renderer='templates/admin/frontpage.jinja2')
    def admin_frontpage(self):
        # when loser logs in, we could pre-populate the list of recommended
        # startups to check out. perhaps pull like 50, then randomly pull from
        # that list
        return {'gibs': self.gibs,
                }

    @view_config(name='startup_search_by_name.json', renderer='json')
    def startup_search_by_name(self):
        request = self.request
        josh = request.json_body

        if len(josh['startup_search_by_name']) <= 1:
            return ""

        results = DBSession.query(Startup).filter(Startup.name.ilike("%{name}%"
                                                                    .format(name=josh['startup_search_by_name'])))
        startups = []
        for result in results:
            startups.append({"id": result.id,
                             "name": result.name,
                             "logo_url": result.logo_url,
                             "local_url": result.local_url,
                             "short_info": result.short_info[:100],
                            })
        #if startups is not None:
            #return ("Taken")
        #else:
            #return ("No results")
        return startups

    @view_config(name='admin_add_to_frontpage_db.json', renderer='json')
    def admin_add_to_frontpage_db(self):
        request = self.request
        try:
            startupid = request.json_body["startupid"]
        except Exception:
            return ("startup id missing")

        startup_check = DBSession.query(FrontpageStartup).filter(FrontpageStartup.startupid == startupid).first()
        if startup_check is not None:
            return ("Already listed")

        newItem = FrontpageStartup(startupid=startupid)
        DBSession.add(newItem)
        DBSession.flush()

        results = DBSession.query(Startup) \
            .join(FrontpageStartup).all()
            #.filter(FrontpageStartup.startupid == self.current_user['id']).all()

        startups = startups_for_scroller(results)
        return startups

    @view_config(name='admin_get_frontpage_db.json', renderer='json')
    def admin_get_frontpage_db(self):
        results = DBSession.query(Startup) \
            .join(FrontpageStartup).all()

        startups = startups_for_scroller(results)
        return startups

    @view_config(name='admin_remove_from_frontpage_db.json', renderer='json')
    def admin_remove_from_frontpage_db(self):
        request = self.request
        try:
            startupid = request.json_body["startupid"]
        except Exception:
            return ("startup id missing")

        frontpage_startup = DBSession.query(FrontpageStartup).filter(FrontpageStartup.startupid == startupid).first()
        DBSession.delete(frontpage_startup)

        return "Success"



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
        print(str(rangestart))
        print(str(rangeend))

        for i in range(rangestart, rangeend):
            print("+++++++++++++++++++++++++++++++")
            print("+++++++++++++++++++++++++++++++")
            print("getting startup ID " + str(i))
            query = requests.get(url+str(i))
            query_dict = json.loads(query.text)

            angelco_check = None
            try:
                angelco_check = DBSession.query(AngelCoMirror).filter(AngelCoMirror.id == query_dict['id']).first()
            except:
                print("query_dict['id'] must not exist")

            try:
                if 'success' in query_dict:
                    logger.debug("startup ID " + str(i) + " at angel.co returned false success boolean")
                    print("startup ID " + str(i) + " at angel.co returned false success boolean")
                    pprint.pprint(query_dict)
                elif query_dict['hidden'] is True:
                    logger.debug("startup ID " + str(i) + " at angel.co is hidden")
                    print("startup ID " + str(i) + " at angel.co is hidden")
                elif angelco_check is not None:
                    logger.debug("startup ID " + str(i) + " at angel.co is already in the database")
                    print("startup ID " + str(i) + " at angel.co is already in the database")
                else:
                    for key, value in query_dict.items():
                        if bool(value) is False:
                            query_dict[key] = ""
                        if type(value) is list or type(value) is dict:
                            query_dict[key] = json.dumps(value)

                    ca = query_dict

                    ### Generate local_url ###
                    url_test = False
                    local_url = name_to_local_url(ca['name'])
                    num = 1
                    local_url_num = local_url
                    while not url_test:
                        st = DBSession.query(Startup).filter(Startup.local_url == local_url_num).first()
                        if st is None:
                            url_test = True
                        else:
                            local_url_num = local_url + "-" + str(num)
                            num = num + 1

                    fix_integer_fields(ca)
                    #pprint.pprint(ca)

                    #### Get location data ###
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

                    ### Fix name ###
                    name = ca['name'].replace('/', '')

                    ### Convert date strings to datetimes ###
                    ca_string = ca['created_at'].split('-')
                    year = ca_string[0]
                    month = ca_string[1]
                    ca_string = ca_string[2].split('T')
                    day = ca_string[0]
                    ca_string = ca_string[1].split(':')
                    hour = ca_string[0]
                    minute = ca_string[1]
                    ca_string = ca_string[2].split('Z')
                    second = ca_string[0]
                    created_at = datetime.datetime(year=int(year),
                                                   month=int(month),
                                                   day=int(day),
                                                   hour=int(hour),
                                                   minute=int(minute),
                                                   second=int(second))

                    ua_string = ca['created_at'].split('-')
                    year = ua_string[0]
                    month = ua_string[1]
                    ua_string = ua_string[2].split('T')
                    day = ua_string[0]
                    ua_string = ua_string[1].split(':')
                    hour = ua_string[0]
                    minute = ua_string[1]
                    ua_string = ua_string[2].split('Z')
                    second = ua_string[0]
                    updated_at = datetime.datetime(year=int(year),
                                                   month=int(month),
                                                   day=int(day),
                                                   hour=int(hour),
                                                   minute=int(minute),
                                                   second=int(second))

                    ### try to avoid blank fields ###
                    about = ca['product_desc']
                    short_info = ca['product_desc']
                    tags = ca['high_concept']
                    if ca['product_desc'] == "":
                        about = ca['high_concept']
                        short_info = ca['high_concept']
                    if ca['high_concept'] != "":
                        short_info = ca['high_concept']

                    ### Commit to database ###
                    # startup.id is needed for the following functions
                    startup = Startup(name=name,
                                      local_url=local_url_num,
                                      userid_creator=1,
                                      about=about,
                                      short_info=short_info,
                                      tags=tags,
                                      # status of 50 implies what options are set
                                        # in this instantiation
                                      status="50",
                                      country=country,
                                      postal_code=postal_code,
                                      state_province=state_province,
                                      city=city,
                                      lng=lng,
                                      lat=lat,
                                      created_at=created_at,
                                      updated_at=updated_at,
                                      #created_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M'),
                                      #updated_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M'),
                                      home_url=ca['company_url'],
                                      twitter_url=ca['twitter_url'],
                                      facebook_url=ca['facebook_url'],
                                      blog_url=ca['blog_url'],
                                      company_size=ca['company_size'],
                                      angelco_quality=int(ca['quality']),
                                      angelco_follower_count=int(ca['follower_count']),
                                      angelco_status=ca['status'],
                                      language='english',
                                      )
                    DBSession.add(startup)
                    DBSession.flush()
                    startup = DBSession.query(Startup).filter(Startup.local_url == local_url_num).first()
                    ### commit with user id of 0 to sort which startups are unclaimed ###
                    user_has_startup = UserHasStartups(userid=1,
                                                       startupid=startup.id
                                                       )
                    DBSession.add(user_has_startup)

                    ### Fix angelcomirror data if necessary ###
                    ca['updated_at'] = updated_at
                    ca['created_at'] = created_at
                    new_angelco_mirror = AngelCoMirror(**query_dict)
                    # We don't need to commit since we already have
                    # angelcomirror.id
                    DBSession.add(new_angelco_mirror)
                    # not needed
                    #angelcomirror = DBSession.query(AngelCoMirror).filter(AngelCoMirror.id == ca['id']).first()

                    ### Create categories and commit them to database ###
                    categories = []
                    if 'markets' in ca:
                        markets = json.loads(ca['markets'])
                        for market in markets:
                            categories.append(market['display_name'])

                    for category in categories:
                        cat_local_url = name_to_local_url(category)
                        # check if category must be created
                        cat_check = DBSession.query(Category).filter(Category.local_url == cat_local_url).first()
                        if cat_check is None:
                            cat = Category(name=category,
                                           local_url=cat_local_url,
                                           num_startups=0,
                                           )
                            DBSession.add(cat)
                            DBSession.flush()
                            cat_check = DBSession.query(Category).filter(Category.local_url == cat_local_url).first()
                        add_startup_has_category(startupid=startup.id, categoryid=cat_check.id)

                    folder_group = str(int(math.ceil(int(startup.id) / 10000.0) * 10000.0))
                    thumb_url = "startups/thumbs/" + folder_group+"/"+str(startup.id) + ".jpg"
                    logo_url = "startups/logos/" + folder_group+"/"+str(startup.id) + ".jpg"

                    print("++++++++++++")
                    print(ca['thumb_url'])
                    print(ca['logo_url'])
                    response = get_images_from_angelco(startup.id, ca['thumb_url'], ca['logo_url'])
                    if response == "no_image":
                        startup.logo_url = None
                        startup.thumb_url = None
                    else:
                        startup.logo_url = logo_url
                        startup.thumb_url = thumb_url

            except KeyError:
                print("+++++++++++++++++++++++++++++++")
                print("+++++++++++++++++++++++++++++++")
                log.debug("startup ID " + str(i) + " at angel.co returned a KeyError")
                print("startup ID " + str(i) + " at angel.co returned a KeyError")


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

            if test_exists is None:
                url_test = False
                local_url = name_to_local_url(name)
                num = 1
                local_url_num = local_url
                while not url_test:
                    st = DBSession.query(Startup).filter(Startup.local_url == local_url_num).first()
                    if st is None:
                        url_test = True
                    else:
                        local_url_num = local_url + "-" + str(num)
                        num = num + 1
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
                    language = 'english',
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
