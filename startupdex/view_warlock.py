from pyramid.security import authenticated_userid
from pyramid.view import (
    notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPNotFound,
    )
from .models import (
    DBSession,
)


class ViewWarlock(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.static_url = request.static_url('startupdex:static/')
        self.images_url = request.static_url('startupdex:images/')
        self.userid_from_cookie = authenticated_userid(request)

        self.privilege = "anonymous"
        self.current_user = {'email': 'NotLoggedIn'}
        self.logged_in = False

        if request.path != 'logout':
        #print(self.userid_from_cookie)
            if self.userid_from_cookie is not None:
                self.logged_in = True
                self.current_user = DBSession.execute(
                    "SELECT * FROM users WHERE id=:param",
                    {"param": self.userid_from_cookie}
                    ).first()
                if self.userid_from_cookie == '1':
                    self.privilege = "admin"
        #flashmsgs = request.session.pop_flash()

        application_url = self.request.route_url('frontpage')
        if application_url == 'http://127.0.0.1/':
            request.session.flash("Local server", queue='warnings')


        #TODO: store timezone offset in self.gibs
        # for anonymous users, send it from the browser and store it in the
        # cookie?

        self.gibs = {'application_url': self.request.route_url('frontpage'),
                     'static_url': self.static_url,
                     'images_url': self.images_url,
                     'userid_from_cookie': self.userid_from_cookie,
                     'logged_in': self.logged_in,
                     'current_user_email': self.current_user['email'],
                     'privilege': self.privilege,
                     }

    @notfound_view_config(append_slash=True)
    def notfound(self):
        return HTTPNotFound("Http not found")
