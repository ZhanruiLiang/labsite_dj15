from django.db import models
from account import User
from spec import Assignment
from django import forms
import os

class Submission(models.Model):
    # required
    user = models.ForeignKey(User, related_name='submissions')
    assignment = models.ForeignKey(Assignment)
    time = models.DateTimeField(auto_now=True)
    # calculated
    path = models.FilePathField(blank=True, max_length=512)
    # afterward
    grader = models.ForeignKey(User, blank=True, null=True, 
            related_name='graded_submissions')
    score = models.SmallIntegerField(null=True, blank=True)
    comment = models.TextField(blank=True)

    @property
    def filename(self):
        return os.path.split(self.path)[1]

    def delete(self):
        try:
            os.remove(self.path)
        except OSError:
            pass
        super(Submission, self).delete()

# Max size in bytes
MAX_SIZE = 1024 * 1024 * 10

class UploadForm(forms.Form):
    file = forms.FileField(
            label='Select a file',
            help_text='maxsize: %d MB' % (MAX_SIZE/2**20),
            )

class UploadError(Exception): 
    def html(self):
        return self.message

def upload(user, assID, file):
    # return: submission
    try:
        ass = Assignment.objects.get(id=assID)
    except:
        raise UploadError('Assignment with this id does not exist')
    name = '{}-{}-{}'.format(assID, user.studentID, file.name)
    path = os.path.join(ass.dest_dir, name)
    with open(path, 'wb') as outf:
        if file.multiple_chunks():
            for chunk in file.chunks():
                outf.write(chunk)
        else:
            outf.write(file.read())
    submission = Submission(
            user=user, 
            assignment=ass,
            )
    submission.path = path
    return submission

def query_progress(user, submission):
    # return: a number in [0, 1]
    pass
