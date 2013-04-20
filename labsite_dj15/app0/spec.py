from django.db import models
from django.conf import settings
from django import forms
from errors import *
import os, subprocess
import json

class Problem(object):
    CODE = 'code'
    TEXT = 'text'
    def __init__(self, type, name, points):
        assert type in (self.CODE, self.TEXT)
        self.type = type
        self.name = name
        self.points = int(points)

    def points_range(self):
        return list(range(self.points+1))

class Spec(object):
    """
    JSON: {
        problems: [
            {name: 'LE_01', type: 'code', points: 1},
            {name: 'LE_02', type: 'code', points: 1},
            {name: 'LE_03', type: 'code', points: 1},
            {name: 'DEBUG', type: 'code', points: 2},
            {name: 'PC_01', type: 'code', points: 3},
            {name: 'PC_03', type: 'code', points: 3},
            ]
    }
    """
    @staticmethod
    def from_json(data):
        data = json.loads(data)
        spec = Spec(data['root'])
        for probData in data['problems']:
            prob = Problem(probData['type'], probData['name'], probData['points'])
            spec.problems.append(prob)
        return spec

    def code_dirs(self):
        for prob in self.problems:
            if prob.type == Problem.CODE:
                yield os.path.join(self.name, prob.name)

    def to_json(self):
        return json.dumps({
            'root': self.name,
            'problems': [{
                'type': prob.type, 'name': prob.name, 'points': prob.points
                } for prob in self.problems]
            })

    def check(self, path):
        """
        Check the files from path with the spec structure:

            spec root         file root (path)
               prob1              prob1         
               prob2              prob2         
               prob3 <-mismatch-> probb3   

        @return: None
        @exceptions: Raise FormatError if check failed.
        """
        errors = []
        if not os.path.exists(os.path.join(path, self.name)):
            if len([f for f in os.listdir(path) if f!='__MACOSX']) != 1:
                errors.append("""Please, put all the files into one directory before compressing your files.
For example:
    $> ls
    LE_01/ LE_02/ 3.12.txt 3.13.txt
    $> mkdir HW1
    $> cp -r LE_01 LE_02 3.12.txt 3.13.txt HW1/
    $> zip -r HW1_10389084.zip HW1
    $> ls
    LE_01/ LE_02/ 3.12.txt 3.13.txt HW1/ HW1_10389084.zip""")
            else:
                errors.append('File/directory \'{}\' not found.'.format(self.name))
        else:
            path = os.path.join(path, self.name)
            files = os.listdir(path)
            for prob in self.problems:
                # check if the file exist
                if prob.name not in files:
                    errors.append('File/directory \'{}\' not found.'.format(os.path.join(self.name, prob.name)))
                else:
                    if prob.type == Problem.TEXT:
                        if os.path.isdir(os.path.join(path, prob.name)):
                            errors.append('{}: Except a text file but directory found'.format(prob.name)) 
                    elif prob.type == Problem.CODE:
                        if not os.path.isdir(os.path.join(path, prob.name)):
                            errors.append('{}: Except a directory'.format(prob.name)) 
        if errors:
            errors.extend(['-'*80, 'Archive tree:', get_tree(path)])
            raise FormatError('\n'.join(errors))

    def html(self):
        lines = []
        lines.append('<b>{}</b>:'.format(self.name))
        for prob in self.problems:
            lines.append('    <b>{name}</b>: type:({type}), points:{points}'.format(
                        name=prob.name,
                        type='codes/directory' if prob.type == Problem.CODE else 'plain text',
                        points=prob.points))
        return '\n'.join(lines)

    def __init__(self, name):
        self.name = name
        self.problems = []

class Assignment(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField()
    duetime = models.DateTimeField()
    spec_str = models.TextField()
    dest_dir = models.FilePathField(max_length=512)
    example = models.FileField(
            upload_to=lambda ass,fname: 'examples/{}/{}'.format(ass.title, fname),
            help_text='An example submission')

    @property
    def spec(self):
        if not hasattr(self, '_spec'):
            self._spec = Spec.from_json(self.spec_str)
        return self._spec

    def url(self):
        return '/m/ass/{}/'.format(self.id)

    def count(self):
        return self.submission_set.filter(retcode=0).count()

    def is_submitted(self, user):
        return user.submissions.filter(assignment=self, retcode=0).count() > 0

def make_ass_dir(assignment):
    base = settings.ASSIGNMENT_BASE_DIR
    name = '{}'.format(assignment.title.replace(' ', '_'))
    dest = os.path.join(base, name)
    if not os.path.exists(dest):
        os.mkdir(dest)
    elif not os.path.isdir(dest):
        return (False, "File exists but is not a directory.")
    assignment.dest_dir = dest
    return (True, dest)

class AssignmentCreationForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'duetime', 'spec_str', 'example')
    def clean_spec_str(self):
        s = self.cleaned_data.get('spec_str')
        try:
            json.loads(s)
        except:
            raise forms.ValidationError(u'Spec format invalid')
        return s

AssignmentModifyForm = AssignmentCreationForm

# utils 
def get_tree(path):
    base, sub = os.path.split(path)
    p = subprocess.Popen(['tree', sub], cwd=base, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.poll() == 0:
        output = p.stdout.read()
        return output
    else:
        return p.stderr.read()
