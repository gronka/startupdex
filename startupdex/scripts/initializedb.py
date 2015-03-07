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
        model = Startup(name='startup5000',
                        quick_info='This is an example startup',
                        logo_url='https://www.google.com/images/srpr/logo11w.png',
                        )
        DBSession.add(model)
        model = Startup(name='agile',
                        quick_info='This is an example startup',
                        logo_url='https://www.google.com/images/srpr/logo11w.png',
                        )
        DBSession.add(model)
        model = Startup(name='30DaySkill',
                        quick_info='This is an example startup',
                        logo_url='https://www.google.com/images/srpr/logo11w.png',
                        )
        DBSession.add(model)
        model = Startup(name='Passion',
                        quick_info='This is an example startup',
                        logo_url='http://www.elpassion.com/wp-content/themes/ELPassion/images/logo.png',
                        )
        DBSession.add(model)
        model = User(name='admin',
                     password='admin',
                     status='active',
                     city='Durham',
                     )
        DBSession.add(model)
