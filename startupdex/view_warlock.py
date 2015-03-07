from pyramid.view import (
    notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPNotFound,
    )


class ViewWarlock(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.static_url = request.static_url('startupdex:static/')

        self.gibs = {'static_url': self.static_url,
                     'application_url': self.request.route_url('frontpage'),
                     }

    @notfound_view_config(append_slash=True)
    def notfound(self):
        return HTTPNotFound("Http not found")
