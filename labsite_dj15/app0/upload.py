from django.db import models
from account import User

class Submission(models.Model):
    user = models.ForeignKey(User, related_name='submissions')
    grader = models.ForeignKey(User, related_name='graded_submissions')
    time = models.DateTimeField(auto_now=True)
    score = models.SmallIntegerField(null=True, blank=True)
    comment = models.TextField()

def upload(user, assID, file):
    # return: submission
    pass

def query_progress(user, submission):
    # return: a number in [0, 1]
    pass
