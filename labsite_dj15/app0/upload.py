from django.db import models
from account import User
from spec import Assignment

class Submission(models.Model):
    # required
    user = models.ForeignKey(User, related_name='submissions')
    assignment = models.ForeignKey(Assignment)
    time = models.DateTimeField(auto_now=True)
    # calculated
    dest_dir = models.FilePathField(blank=True, max_length=512)
    # afterward
    grader = models.ForeignKey(User, blank=True, null=True, related_name='graded_submissions')
    score = models.SmallIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)

def upload(user, assID, file):
    # return: submission
    pass

def query_progress(user, submission):
    # return: a number in [0, 1]
    pass
