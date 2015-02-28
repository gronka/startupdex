import cgi
from docutils.core import publish_parts

from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPNotFound,
    )

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    Startup,
    )

from startupdex.view_warlock import ViewWarlock


class ViewFrontpage(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='frontpage', renderer='templates/frontpage.jinja2')
    def frontpage(self):
        print('++++++++++++++++++++++++++++++++++++++++++++')
        print(self.gibs)
        print('++++++++++++++++++++++++++++++++++++++++++++')
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

# regular expression used to find WikiWords

    #return HTTPFound(location = request.route_url('view_page',
                                                  #pagename='FrontPage'))

@view_config(route_name='startup_profile', renderer='templates/startup/profile.jinja2')
def startup_profile(request):
    pass
    #pagename = request.matchdict['pagename']
    #page = DBSession.query(Page).filter_by(name=pagename).first()
    #if page is None:
        #return HTTPNotFound('No such page')

    #def check(match):
        #word = match.group(1)
        #exists = DBSession.query(Page).filter_by(name=word).all()
        #if exists:
            #view_url = request.route_url('view_page', pagename=word)
            #return '<a href="%s">%s</a>' % (view_url, cgi.escape(word))
        #else:
            #add_url = request.route_url('add_page', pagename=word)
            #return '<a href="%s">%s</a>' % (add_url, cgi.escape(word))

    #content = publish_parts(page.data, writer_name='html')['html_body']
    #content = wikiwords.sub(check, content)
    #edit_url = request.route_url('edit_page', pagename=pagename)
    #return dict(page=page, content=content, edit_url=edit_url)

#@view_config(route_name='startup/create', renderer='templates/edit.pt')
#def add_page(request):
    #pagename = request.matchdict['pagename']
    #if 'form.submitted' in request.params:
        #body = request.params['body']
        #page = Page(name=pagename, data=body)
        #DBSession.add(page)
        #return HTTPFound(location = request.route_url('view_page',
                                                      #pagename=pagename))
    #save_url = request.route_url('add_page', pagename=pagename)
    #page = Page(name='', data='')
    #return dict(page=page, save_url=save_url)

#@view_config(route_name='startup/edit', renderer='templates/edit.pt')
#def edit_page(request):
    #pagename = request.matchdict['pagename']
    #page = DBSession.query(Page).filter_by(name=pagename).one()
    #if 'form.submitted' in request.params:
        #page.data = request.params['body']
        #DBSession.add(page)
        #return HTTPFound(location = request.route_url('view_page',
                                                      #pagename=pagename))
    #return dict(
        #page=page,
        #save_url = request.route_url('edit_page', pagename=pagename),
        #)


#@view_config(route_name='home', renderer='templates/mytemplate.pt')
#def my_view(request):
    #try:
        #one = DBSession.query(Page).filter(MyModel.name == 'one').first()
    #except DBAPIError:
        #return Response(conn_err_msg, content_type='text/plain', status_int=500)
    #return {'one': one, 'project': 'startupdex'}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_startupdex_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
