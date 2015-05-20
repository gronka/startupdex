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
    Password,
    Startup,
    Article,
    UserHasArticles,
    UserHasStartups,
    RegisterUserSchema,
    write_basic_image,
    send_mail
    )

from pyramid.security import (
    remember,
    forget,
    )

from startupdex.view_warlock import ViewWarlock

import logging
import colander
from itsdangerous import URLSafeTimedSerializer
from pyramid_mailer.message import Message

import hashlib
import uuid
import datetime
import math

logger = logging.getLogger(__name__)


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





class UserView(ViewWarlock):
    def __init__(self, context, request):
        ViewWarlock.__init__(self, context, request)

    @view_config(route_name='register', renderer='templates/user/register.jinja2')
    def register(self):
        request = self.request
        params = request.params
        referrer = request.referrer
        register_url = request.route_url('register')
        if referrer == register_url:
            referrer = '/'
        came_from = params.get('came_from', referrer)

        dont_add_user = False
        if 'form.submitted' in params:
            if params['email'] != params['verify_email']:
                request.session.flash('Email addresses do not match', queue='errors')
                dont_add_user = True
            if params['password'] != params['verify_password']:
                request.session.flash('Passwords do not match', queue='errors')
                dont_add_user = True

            schema = RegisterUserSchema()
            try:
                deserialized = schema.deserialize(params)
                check_user = DBSession.query(User).filter(User.email == deserialized['email']).first()
                if check_user is not None:
                    request.session.flash("Email address is in use by another user.", queue='errors')
                    dont_add_user = True
            except colander.Invalid as e:
                request.session.flash(e, queue='errors')
                dont_add_user = True

            if dont_add_user is True:
                self.gibs['email'] = params['email']
                self.gibs['verify_email'] = params['verify_email']
                self.gibs['fullname'] = params['fullname']
                self.gibs['phone'] = params['phone']
                self.gibs['company'] = params['company']
                return {'gibs': self.gibs,
                        'came_from': came_from,
                        }
            else:
                user = User(email=deserialized['email'],
                            fullname=deserialized['fullname'],
                            )
                DBSession.add(user)
                update_password(deserialized['email'], deserialized['password'])
                token = generate_confirmation_token(user.email)
                url = request.route_url('frontpage')
                url = 'http://' + self.gibs.application_url + '/confirm_email/'
                print("++++++++++++++++++++++++")
                print("++++++++++++++++++++++++")
                print(str(url))
                confirmation_url = url + token
                body = """<p>Thanks for joining!</p>
                <p>Click the following link to complete your registration: </p>
                {confirmation_url}
                """.format(confirmation_url=confirmation_url)
                subject="Startupdex: New Member Confirmation"
                sender="Startupdex <noreply@startupdex.com>"
                recipients = [user.fullname + " <"+user.email+">",]
                message = Message(subject=subject,
                                  #sender="mail@startupdex.com",
                                  sender=sender,
                                  recipients=recipients,
                                  body=body,
                                  )
                send_mail(to=recipients,
                            fro=sender,
                            subject=subject,
                            text=body,
                            )
                #mailer = request.registry['mailer']
                #try:
                    #mailer.send(message)
                    #mailer.send_to_queue(message)
                    #mailer.send_immediately(message, fail_silently=False)
                #except ValueError as e:
                    #log.error("Email failed to send" + e)


                request.session.flash('Please verify the email address ' + str(user.email) + ' to complete your registration.',
                                    queue='successes')
                request.session.flash('Don\'t forget to check your spam.',
                                    queue='successes')
                request.session.flash(confirmation_url,
                                    queue='successes')
                return HTTPFound(location = came_from)
        return {'gibs': self.gibs,
                'came_from': came_from,
                }

    @view_config(route_name='login', renderer='templates/user/login.jinja2')
    def login(self):
        request = self.request
        params = request.params
        if self.logged_in:
            return HTTPForbidden()
        login_url = request.route_url('login')
        referrer = request.referrer
        if referrer == login_url:
            referrer = '/'
        came_from = request.params.get('came_from', referrer)
        if 'form.submitted' in params:
            user = DBSession.execute(
                "SELECT * FROM users WHERE email=:param ORDER BY id DESC",
                {"param": params['email']}
                ).first()

            if user is not None:
                if user.confirmed is False:
                    request.session.flash('Account must be activated before logging in.',
                                          queue='notifications')
                elif check_password(params['email'], params['password']):
                    userid = user.id
                    print("userid: " + str(userid))
                    print("email: " + str(user.email))
                    headers = remember(request, str(userid))
                    self.gibs['current_user'] = user.email
                    request.session.flash('Successfully logged in as ' + str(user.email),
                                        queue='successes')
                    return HTTPFound(location=came_from,
                                    headers=headers)

            request.session.flash('Email or password was incorrect, or user does not exist.',
                                  queue='warnings')
        return {'gibs': self.gibs,
                'came_from': came_from,
                }

    @view_config(route_name='logout')
    def logout(self):
        headers = forget(self.request)
        #url = self.request.route_url('frontpage')
        url = self.request.referrer
        if url is None:
            url = self.gibs['application_url']

        self.request.session.flash('Successfully logged out',
                              queue='notifications')
        return HTTPFound(location=url,
                         headers=headers)

    #@view_config(route_name='confirm_email', renderer='templates/.jinja2')
    @view_config(route_name='confirm_email')
    def confirm_email(self):
        request = self.request
        token = self.request.matchdict['token']
        try:
            email = confirm_token(token)
        except:
            request.session.flash('Confirmation link is invalid or expired.',
                                  queue='errors')

        if email is not False:
            print(str(email))
            print(str(type(email)))
            user = DBSession.query(User).filter(User.email == email).first()
            if user.confirmed:
                request.session.flash('User has already been confirmed.',
                                    queue='notifications')
            else:
                user.confirmed = True
                DBSession.add(user)
                request.session.flash('User account activated!',
                                    queue='successes')
        return HTTPFound(location=request.route_url('frontpage'))


    @view_config(route_name='manage_articles', renderer='templates/user/manage_articles.jinja2')
    def manage_articles(self):
        articles = []
        #articles = DBSession.query(Article) \
            #.join(UserHasArticles) \
            #.filter(UserHasArticles.userid == self.current_user['id']).all()
        articles = DBSession.query(Article).filter(Article.authorid == self.current_user['id']).all()

        return {'gibs': self.gibs,
                'user': self.current_user,
                'articles': articles,
                }

    @view_config(route_name='manage_startups', renderer='templates/user/manage_startups.jinja2')
    def manage_startups(self):
        startups = []
        #startups = DBSession.query(Startup) \
            #.join(UserHasStartups) \
            #.filter(UserHasStartups.userid == self.current_user['id']).all()
        startups = DBSession.query(Startup).filter(Startup.userid_creator == self.current_user['id']).all()

        return {'gibs': self.gibs,
                'user': self.current_user,
                'startups': startups,
                }

    @view_config(route_name='loggedin_profile', renderer='templates/user/profile.jinja2')
    def loggedin_profile(self):
        return {'gibs': self.gibs,
                'user': self.current_user,
                }

    @view_config(route_name='modify_profile', renderer='templates/user/modify_profile.jinja2')
    def modify_profile(self):
        return {'gibs': self.gibs,
                'user': self.current_user,
                }

    @view_config(name='modify_profile_save_changes.json', renderer='json')
    def modify_profile_save_changes(self):
        request = self.request
        user_json = request.json_body
        user = DBSession.query(User).filter(User.id == user_json['id']).first()
        for key, prop in user_json.items():
            if prop == "None":
                prop = None
            elif prop == "":
                prop = None
            elif prop == "False":
                prop = False
            elif prop == "True":
                prop = True
            if prop != getattr(user, key):
                setattr(user, key, prop)
        return ("Success")

    @view_config(route_name='modify_billing', renderer='templates/user/modify_billing.jinja2')
    def modify_billing(self):
        return {'gibs': self.gibs,
                'user': self.current_user,
                }

    @view_config(route_name='upload_profile_photo')
    def upload_profile_photo(self):
        request = self.request
        params = request.params
        user = self.current_user
        user = DBSession.query(User).filter(User.id == self.current_user.id).first()

        if 'form.submitted' in params:
            image = request.params['photo']
            folder_group = str(int(math.ceil(user.id / 10000.0) * 10000.0))
            imagename = str(user.id) + '.jpg'
            photo_url = 'users/photo/' + folder_group + '/' + imagename
            user.photo_url = photo_url

            photo_dir = '/var/www/startupdex/images/users/photo/' + folder_group + '/'
            write_basic_image(image, photo_dir, imagename)

            request.session.flash("Profile picture uploaded.",
                                queue='successes')
            return HTTPFound(location=request.route_url("modify_profile"))

        return HTTPFound(location=request.route_url("modify_profile"))

    @view_config(route_name='user_profile', renderer='templates/user/profile.jinja2')
    def user_profile(self):
        #ident = self.request.matchdict['ident']
        return {'gibs': self.gibs,
                'test': self.gibs,
                }

    @view_config(route_name='user_create', renderer='templates/user/create.jinja2')
    def user_create(self):
        params = self.request.params
        if 'form.submitted' in params:
            try:
                user = User(params)
            except Exception as err:
                print(err.__class__)
                print(err)

        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='user_edit', renderer='templates/user/edit.jinja2')
    def user_edit(self):
        #identifier = self.request.matchdict['id']
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

    @view_config(route_name='user_delete', renderer='templates/user/delete.jinja2')
    def user_delete(self):
        #ident = self.request.matchdict['ident']
        return {'data': 'test_data',
                'gibs': self.gibs,
                }

