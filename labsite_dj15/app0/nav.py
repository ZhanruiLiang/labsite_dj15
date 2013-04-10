from django.template.loader import get_template
from django.template import Template, Context, RequestContext
from django.conf import settings
from django.contrib.auth.models import AnonymousUser

def render_nav_html(user):
    navItems = [
            ('Home', settings.HOME_URL),
            ('Assignment', settings.ASSIGNMENT_URL),
            ]
    if isinstance(user, AnonymousUser):
        navItems.extend([
            ('Register', settings.REGISTER_URL),
            ('Login', settings.LOGIN_URL),
            ])
    else:
        if user.usertype == 'TA':
            navItems.extend([
                ('Post', settings.POST_URL),
                ])
        elif user.usertype == 'student':
            navItems.extend([
                # ('Submissions', settings.SUBMISSIONS_URL),
                ])
        navItems.extend([
            ('Logout', settings.LOGOUT_URL),
            ])
    return get_template('nav.html').render(Context({'navItems': navItems, 'user': user}))
