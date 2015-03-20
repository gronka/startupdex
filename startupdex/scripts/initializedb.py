import os
import sys
import transaction

from sqlalchemy import engine_from_config

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from ..models import (
    DBSession,
    Startup,
    Article,
    User,
    Base,
    )


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.create_all(engine)
    with transaction.manager:
        startup = Startup(name='Startup5000',
                          quick_info='Startup5000 delivers feature rich content to your apps',
                          logo_url='images/startups/1.jpg',
                          logo_thumb_url='images/startups/1_thumb.jpg',
                          headquarters="115 Lee Rd, Springfield, Illinois, USA",
                          country="USA",
                          state_province="Illinois",
                          city="Springfield",
                          home_url="https://www.startup.5000",
                          )
        article1 = Article(startupdex_id=1,
                           author_name="Taylor Gronka",
                           author_id=2,
                           title="Startup5000 launches iOS app",
                           lead_text="Within a month of the Android app launch, Startup5000 has already entered the iOS market.",
                           thumb_url="images/articles/1_1_thumb.jpg",
                           )
        article2 = Article(startupdex_id=1,
                           author_name="Ben - Founder",
                           author_id=2,
                           title="Message from the founder",
                           lead_text="I wanted to take a moment to let everyone know where we are, and to thank those who have...",
                           thumb_url="images/articles/1_2_thumb.jpg",
                           )
        article3 = Article(startupdex_id=1,
                           author_name="Ben - Founder",
                           author_id=2,
                           title="Where we are today",
                           lead_text="Recent changes have caused concerns among our clients - but everything from here will be uphill",
                           thumb_url="images/articles/1_3_thumb.jpg",
                           )
        article4 = Article(startupdex_id=1,
                           author_name="Taylor Gronka",
                           author_id=2,
                           title="Why we will be delaying the iOS app",
                           lead_text="After much consideration, we ",
                           thumb_url="images/articles/1_4_thumb.jpg",
                           )
        article5 = Article(startupdex_id=1,
                           author_name="Forbes",
                           author_id=2,
                           title="Startup5000 - Potential winner or loser?",
                           lead_text="Forbes looks at some strong yet risky startups",
                           thumb_url="images/articles/1_5_thumb.jpg",
                           )
        article6 = Article(startupdex_id=1,
                           author_name="Ben - Founder",
                           author_id=2,
                           title="Startup5000 - greetings to StartupDex",
                           lead_text="Here in Springfield, Illinois, it has been hard to find experienced entrereneurs like us... ",
                           thumb_url="images/articles/1_6_thumb.jpg",
                           )
        article7 = Article(startupdex_id=1,
                           author_name="Andres (blogger)",
                           author_id=2,
                           title="Searching for investors",
                           lead_text="An interesting new company in Springfield, Illinois has had a hard time securing investors.",
                           thumb_url="images/articles/1_7_thumb.jpg",
                           )
        article8 = Article(startupdex_id=1,
                           author_name="Taylor Gronka",
                           author_id=2,
                           title="Startup5000 Founded",
                           lead_text="Startup5000 was founded in Springfield, Illinois on Feb. 1, 2015.",
                           thumb_url="images/articles/1_8_thumb.jpg",
                           )
        DBSession.add(startup)
        DBSession.add(article1)
        DBSession.add(article2)
        DBSession.add(article3)
        DBSession.add(article4)
        DBSession.add(article5)
        DBSession.add(article6)
        DBSession.add(article7)
        DBSession.add(article8)
        startup = Startup(name='Startup6000',
                          quick_info="Tired of other companies that just don't cut it?",
                          logo_url='https://www.google.com/images/srpr/logo11w.png',
                          logo_thumb_url='images/startups/1_thumb.jpg',
                          headquarters="115 Lee Rd, Springfield, Illinois, USA",
                          country="USA",
                          state_province="Illinois",
                          city="Springfield",
                          home_url="https://www.startup.5000",
                          )
        DBSession.add(startup)
        startup = Startup(name='30DaySkill',
                          quick_info='Learn a new skill every 30 days with 30DaySkill! Neat!',
                          logo_url='https://www.google.com/images/srpr/logo11w.png',
                          logo_thumb_url='images/startups/1_thumb.jpg',
                          headquarters="115 Lee Rd, Springfield, Illinois, USA",
                          country="USA",
                          state_province="Illinois",
                          city="Springfield",
                          home_url="https://www.startup.5000",
                          )
        DBSession.add(startup)
        startup = Startup(name='Passion',
                          quick_info='This is an example startup',
                          logo_url='http://www.elpassion.com/wp-content/themes/ELPassion/images/logo.png',
                          logo_thumb_url='images/startups/1_thumb.jpg',
                          headquarters="115 Lee Rd, Springfield, Illinois, USA",
                          country="USA",
                          state_province="Illinois",
                          city="Springfield",
                          home_url="https://www.startup.5000",
                          )
        DBSession.add(startup)
        #startupdex_id = Column(Integer)
        #author_name = Column(Text)
        #author_id = Column(Integer)
        #title = Column(Text)
        #subtitle = Column(Text)
        #lead_text = Column(Text)
        #story = Column(Text)
        #date_published = Column(Text)
        #date_edited = Column(Text)
        #thumb_url = Column(Text)
        #header_image = Column(Text)
        #other_images = Column(Text)
        user = User(name='admin',
                     password='admin',
                     status='active',
                     city='Durham',
                     )
        DBSession.add(user)
        user = User(name='gronka',
                     password='admin',
                     status='active',
                     city='Durham',
                     )
        DBSession.add(user)
