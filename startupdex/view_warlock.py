class ViewWarlock(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.static_url = request.static_url('startupdex:static/')

        self.gibs = {'static_url': self.static_url,
                     }
