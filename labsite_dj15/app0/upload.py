from django.db import models
from account import User
from spec import Assignment
from django import forms
from errors import *
from dictfield import JSONField
import os

class Submission(models.Model):
    # required
    user = models.ForeignKey(User, related_name='submissions')
    assignment = models.ForeignKey(Assignment)
    time = models.DateTimeField(auto_now_add=True)
    path = models.FilePathField(blank=True, max_length=512)
    # calculated
    retcode = models.IntegerField(blank=True)
    message = models.TextField(blank=True, default='')
    # afterward
    grader = models.ForeignKey(User, blank=True, null=True, 
            related_name='graded_submissions')
    finished = models.BooleanField(default=False)

    @property
    def filename(self):
        return os.path.split(self.path)[1]

    def delete(self):
        try:
            os.remove(self.path)
        except OSError:
            pass
        super(Submission, self).delete()

    def total_score(self):
        return sum(s.score for s in self.score_set.all())

    def get_score(self, problem_name):
        try:
            score = self.score_set.get(problem_name=problem_name)
        except:
            score = None
        return score

    def url(self):
        return '/m/subm/{}/'.format(self.id)

class Score(models.Model):
    submission = models.ForeignKey(Submission, related_name='score_set')
    problem_name = models.CharField(max_length=20)
    score = models.IntegerField()
    comment = models.TextField(default='', blank=True)

class ScoreForm(forms.ModelForm):
    class Meta:
        model = Score
        exclude = ('submission',)
    sid = forms.CharField()

# Max size in bytes
MAX_SIZE = 1024 * 1024 * 10

class UploadForm(forms.Form):
    file = forms.FileField(
            label='Select a file',
            help_text='maxsize: %d MB' % (MAX_SIZE/2**20),
            )

def upload(user, assID, file):
    # return: submission
    try:
        ass = Assignment.objects.get(id=assID)
    except:
        raise CheckError('Assignment with this id does not exist')
    if file.size > MAX_SIZE:
        raise UploadError('File too large.')
    submission = Submission(
            user=user, 
            assignment=ass,
            retcode=UploadError.code,
            message='unknown error',
            )
    submission.save(False)
    name = u'{}-{}-{}'.format(submission.id, user.studentID, file.name)
    path = os.path.join(ass.dest_dir, name)
    with open(path, 'wb') as outf:
        if file.multiple_chunks():
            for chunk in file.chunks():
                outf.write(chunk)
        else:
            outf.write(file.read())
    submission.path = path
    return submission

def query_progress(user, submission):
    # return: a number in [0, 1]
    pass
