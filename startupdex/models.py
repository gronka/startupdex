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

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


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
    logo_thumb_url = Column(Text)
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
    company_size = Column(Integer)
    company_status = Column(Integer)


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
