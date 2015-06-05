#from pyramid.response import Response
from pyramid.view import (
    view_config,
    #notfound_view_config
    )
from pyramid.httpexceptions import (
    HTTPFound,
    HTTPForbidden,
    #HTTPNotFound,
    )

from .models import (
    DBSession,
    User,
    Article,
    Startup,
    UserHasArticles,
    StartupHasArticles,
    UserHasStartups,
    CreateArticleSchema,
    ModifyArticleSchema,
    write_basic_image,
    title_to_local_url,
    )

from startupdex.view_warlock import ViewWarlock

import logging
import colander
from itsdangerous import URLSafeTimedSerializer

import hashlib
import uuid
import math

log = logging.getLogger(__name__)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer('somesecret')
    return serializer.dumps(email, salt='secretsalt')


# 604800 seconds = 1 week
def confirm_token(token, expiration=604800):
    serializer = URLSafeTimedSerializer('somesecret')
    try:
        email = serializer.loads(
            token,
            salt='secretsalt',
            max_age=expiration,
        )
    except:
        return False
    return email


def login_user(login_params):
    #user_lookup = DBSession.execute(
        #"SELECT * FROM users WHERE email=:param ORDER BY id DESC",
        #{"param": user.email}
        #).first()
    user_lookup = DBSession.query(User).filter(User.email == login_params.email).first()
    if user_lookup is None:
        print("returned FALSE")
        return False
    print("email found. testing password")
    if check_password(login_params.email, login_params.password) is True:
        print("login succeeded")
        return True
    else:
        print("other error - login failed")
        return False


def update_password(email, password):
    user = DBSession.query(User).filter(User.email == email).first()
    salt1 = uuid.uuid4().hex
    salt2 = user.email[1:7]
    #combo = (salt2 + password + salt1)[0:32]
    combo = salt2 + password + salt1
    hashed_password = combo
    for i in range(0, 413):
        hashed_password = hashlib.sha512(hashed_password.encode()).hexdigest()

    password = Password(user_id=user.id,
                        salt1=salt1,
                        salt2=salt2,
                        password=hashed_password,
                        version=1,
                        )
    DBSession.add(password)


def check_password(email, password):
    user = DBSession.query(User).filter(User.email == email).first()
    pw = DBSession.query(Password).filter(Password.user_id == user.id).first()
    try:
        combo = pw.salt2 + password + pw.salt1
    except AttributeError:
        return False
    hashed_password = combo
    for i in range(0, 413):
        hashed_password = hashlib.sha512(hashed_password.encode()).hexdigest()
    if hashed_password == pw.password:
        return True
    else:
        return False





class ArticleView(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)


    @view_config(route_name='article_profile', renderer='templates/article/profile.jinja2')
    def article_profile(self):
        ident = self.request.matchdict['ident']
        article = DBSession.query(Article).filter(Article.local_url == ident).first()
        startup = DBSession.query(Startup).filter(Startup.id == article.startupdexid).first()

        return {'gibs': self.gibs,
                'ident': ident,
                'startup': startup,
                'article': article,
                }

    @view_config(route_name='create_article', renderer='templates/article/create.jinja2')
    def article_create(self):
        request = self.request
        params = self.request.params
        startups = []
        startups = DBSession.query(Startup) \
            .join(UserHasStartups) \
            .filter(UserHasStartups.userid == self.current_user['id']).all()
        if 'form.submitted' in params:
            schema = CreateArticleSchema()
            try:
                deserialized = schema.deserialize(params)
            except Exception as e:
                request.session.flash(e, queue='errors')
                return {'gibs': self.gibs,
                        'user': self.current_user,
                        }

            startupdexid = 0
            try:
                startupdexid = int(params['about'])
            except Exception as e:
                #article is not about a startup
                pass

            url_test = False
            local_url = title_to_local_url(deserialized['title'])
            num = 1
            local_url_num = local_url
            while not url_test:
                st = DBSession.query(Article).filter(Article.local_url == local_url_num).first()
                if st is None:
                    url_test = True
                else:
                    local_url_num = local_url + "-" + str(num)
                    num = num + 1

            article = Article(title=deserialized['title'],
                              tags=deserialized['tags'],
                              lead_text=deserialized['lead_text'],
                              story=deserialized['story'],
                              local_url=local_url_num,
                              startupdexid=startupdexid,
                              authorid=self.current_user.id,
                              )

            DBSession.add(article)
            DBSession.flush()
            article = DBSession.query(Article).filter(Article.local_url == local_url_num).first()
            user_has_article = UserHasArticles(userid=self.current_user.id,
                                               articleid=article.id
                                               )
            DBSession.add(user_has_article)
            startup_has_article = StartupHasArticles(startupid=startupdexid,
                                                     articleid=article.id
                                                     )
            DBSession.add(startup_has_article)
            request.session.flash(article.title + " published.",
                                queue='successes')
            return HTTPFound(location=request.route_url("upload_article_photo", id=article.id))

        return {'gibs': self.gibs,
                'user': self.current_user,
                'startups': startups,
                }

    @view_config(route_name='modify_article', renderer='templates/article/modify_article.jinja2')
    def modify_article(self):
        request = self.request
        params = request.params
        articleid = request.matchdict['id']
        article = DBSession.query(Article).filter(Article.id == articleid).first()
        startups = []
        startups = DBSession.query(Startup) \
            .join(UserHasStartups) \
            .filter(UserHasStartups.userid == self.current_user['id']).all()

        return {'gibs': self.gibs,
                'user': self.current_user,
                'article': article,
                'startups': startups,
                }

    @view_config(route_name='upload_article_photo', renderer='templates/article/upload_article_photo.jinja2')
    def upload_article_photo(self):
        request = self.request
        params = request.params
        articleid = request.matchdict['id']
        article = DBSession.query(Article).filter(Article.id == articleid).first()

        if 'form.submitted' in params:
            image = request.params['photo']
            folder_group = str(int(math.ceil(article.id / 10000.0) * 10000.0))
            imagename = str(articleid) + '.jpg'
            photo_url = 'articles/photos/' + folder_group + '/' + imagename
            article.photo_url = photo_url

            photo_dir = '/var/www/startupdex/images/articles/photos/' + folder_group + '/'
            write_basic_image(image, photo_dir, imagename)

            request.session.flash("Article photo uploaded.",
                                queue='successes')
            return HTTPFound(location=request.route_url("manage_articles"))

        return {'gibs': self.gibs,
                'user': self.current_user,
                'article': article,
                }

    @view_config(name='modify_article_save_changes.json', renderer='json')
    def modify_article_save_changes(self):
        request = self.request
        article_json = request.json_body
        schema = ModifyArticleSchema()
        try:
            deserialized = schema.deserialize(article_json)
        except colander.Invalid as e:
            request.session.flash(e, queue='errors')
            return ("Fail, reload")

        article = DBSession.query(Article).filter(Article.id == article_json['articleid']).first()
        for key, prop in deserialized.items():
            if prop == "None":
                prop = None
            elif prop == "":
                prop = None
            elif prop == "False":
                prop = False
            elif prop == "True":
                prop = True
            if prop != getattr(article, key):
                setattr(article, key, prop)
        return ("Success")
