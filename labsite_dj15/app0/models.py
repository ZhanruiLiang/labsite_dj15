from django.db import models
from django.contrib import admin

from account import User
from check import Compilation
from grade import Run
from upload import Submission
from spec import Assignment

admin.site.register(User)
admin.site.register(Submission)
admin.site.register(Assignment)
# admin.site.register(User)
