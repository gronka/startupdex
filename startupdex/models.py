from sqlalchemy import (
    Column,
    #Index,
    Integer,
    Text,
    #Boolean,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

import json

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

DATETIME_FORMAT = '%Y%m%d%H%M%S'

from peewee import *
from playhouse.sqlite_ext import *

ftsdb = SqliteExtDatabase('/var/www/startupdex/startupdex_fts.sqlite', threadlocals=True)

class Entry(Model):
    title = CharField()
    content = TextField()


    class Meta:
        database = ftsdb


class FTSEntry(FTSModel):
    entry = ForeignKeyField(Entry, primary_key=True)
    content = TextField()


    class Meta:
        database = ftsdb


class FTSStartup(FTSModel):
    # id is implicit
    startupdex_id = TextField()
    angelco_id = TextField()
    name = TextField()
    content = TextField()
    quick_info = TextField()
    short_info = TextField()
    thumb_url = TextField()
    ranking = TextField()


    class Meta:
        database = ftsdb


# this function is meant for correcting empty fields so they are properly
# committed to the postgresql database
def fix_integer_fields(db_dict):
    integer_fields = ("id",
                "hidden",
                "community_profile",
                "quality",
                "follower_count",
                "angelco_quality",
                "angelco_follower_count",
                "company_size",
                "company_status",
                )
    for field in integer_fields:
        if field in db_dict:
            if db_dict[field] == "":
                db_dict[field] = 0
            elif db_dict[field] is True:
                db_dict[field] = 1

def get_images_from_angelco(index, thumb_url, logo_url):
    import requests
    import os
    print(str(index))
    folder_group = str(int(math.ceil(index / 10000.0) * 10000.0))
    fpath = '/var/www/startupdex/images/startups/thumbs/'+folder_group+'/'
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    try:
        print(str(thumb_url))
        f = open(fpath+str(index)+'.jpg', 'wb')
    except ValueError:
        print("thumb_url is undefined for index " + str(index))
    f.write(requests.get(thumb_url).content)
    f.close()
    fpath = '/var/www/startupdex/images/startups/logos/'+folder_group+'/'
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    try:
        print(str(logo_url))
        f = open(fpath+str(index)+'.jpg', 'wb')
    except ValueError:
        print("logo_url is undefined for index " + str(index))
    f.write(requests.get(logo_url).content)
    f.close()

    #fpath = '/home/taylor/projects/startupdex/startupdex/static/images/startups/logos/'+folder_group+'/'
    #if not os.path.exists(fpath):
        #os.makedirs(fpath)
    #f = open(fpath+str(index)+'.jpg', 'wb')
    #f.write(requests.get(logo_url).content)
    #f.close()



class Startup(Base):
    """ The SQLAlchemy declarative model class for a Startup object. """
    __tablename__ = 'startups'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    status = Column(Text)
    headquarters = Column(Text)
    locations = Column(Text)
    country = Column(Text)
    state_province = Column(Text)
    city = Column(Text)
    startupdex_url = Column(Text)
    home_url = Column(Text)
    twitter_url = Column(Text)
    blog_url = Column(Text)
    facebook_url = Column(Text)
    logo_url = Column(Text)
    thumb_url = Column(Text)
    header_info = Column(Text)
    quick_info = Column(Text)
    short_info = Column(Text)
    long_info = Column(Text)
    primary_category = Column(Text)
    categories = Column(Text)
    founders = Column(Text)
    about = Column(Text)
    startupdex_ranking = Column(Text)
    angelco_quality = Column(Integer)
    angelco_follower_count = Column(Integer)
    created_at = Column(Text)
    updated_at = Column(Text)
    angelco_status = Column(Text)
    company_size = Column(Text)
    company_status = Column(Integer)



#logo_url
#thumb_url
#screenshots

class AngelCoMirror(Base):
    __tablename__ = 'angelcomirror'
    startupdex_id = Column(Integer, primary_key=True)
    id = Column(Integer)
    hidden = Column(Integer)
    community_profile = Column(Integer)
    name = Column(Text)
    angellist_url = Column(Text)
    logo_url = Column(Text)
    thumb_url = Column(Text)
    quality = Column(Integer)
    product_desc = Column(Text)
    high_concept = Column(Text)
    follower_count = Column(Integer)
    company_url = Column(Text)
    company_size = Column(Text)
    company_type = Column(Text)  # json list
    created_at = Column(Text)
    updated_at = Column(Text)
    twitter_url = Column(Text)
    facebook_url = Column(Text)
    linkedin_url = Column(Text)
    blog_url = Column(Text)
    crunchbase_url = Column(Text)
    video_url = Column(Text)
    markets = Column(Text)  # json list
    locations = Column(Text)  # json list
    status = Column(Text)  # json object
    screenshots = Column(Text)  # json list
    launch_date = Column(Text)
    fundraising = Column(Text)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    password = Column(Text)
    status = Column(Text)
    location = Column(Text)
    country = Column(Text)
    state_province = Column(Text)
    city = Column(Text)
    local_url = Column(Text)
    home_url = Column(Text)
    twitter_url = Column(Text)
    blog_url = Column(Text)
    facebook_url = Column(Text)


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    startupdex_id = Column(Integer)
    author_name = Column(Text)
    author_id = Column(Integer)
    title = Column(Text)
    subtitle = Column(Text)
    lead_text = Column(Text)
    story = Column(Text)
    date_published = Column(Text)
    date_edited = Column(Text)
    thumb_url = Column(Text)
    header_image = Column(Text)
    other_images = Column(Text)


#Index('my_index', MyModel.name, unique=True, mysql_length=255)
