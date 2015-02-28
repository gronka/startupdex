from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
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
    location = Column(Text)
    country = Column(Text)
    state_province = Column(Text)
    city = Column(Text)
    local_url = Column(Text)
    home_url = Column(Text)
    twitter_url = Column(Text)
    blog_url = Column(Text)
    facebook_url = Column(Text)
    logo_url = Column(Text)
    logo_th_url = Column(Text)
    header_info = Column(Text)
    quick_info = Column(Text)
    short_info = Column(Text)
    long_info = Column(Text)
    primary_category = Column(Text)
    categories = Column(Text)
    founders = Column(Text)
    about = Column(Text)
    local_ranking = Column(Text)


#Index('my_index', MyModel.name, unique=True, mysql_length=255)
