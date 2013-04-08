from django.db import models
from django.conf import settings
from django import forms
import os

class Spec:
    """
    Spec example:

    dir('', [
        dir('LE_01'),
        dir('LE_02'),
        dir('LE_03'),
        dir('PC_01'),
        dir('PC_03'),
        dir('DEBUG'),
        txt('answers.txt'),
        dir('3.16'),
        dir('3.17'),
        ])

    members:
    childs
    name
    """
    DIR = 'dir'
    TXT = 'txt'

    @staticmethod
    def from_str(specStr):
        return eval(specStr, {
            'dir': Spec.dir, 
            'txt': Spec.txt,
            })

    @staticmethod
    def dir(name, data=None):
        spec = Spec(name, Spec.DIR)
        spec.childs = data or []
        return spec

    @staticmethod
    def txt(name):
        spec = Spec(name, Spec.TXT)
        return spec

    def __init__(self, name, type):
        self.type = type
        self.name = name
        self.childs = []

    def code_dirs(self):
        # iter method
        yield self.name
        for child in self.childs:
            for subpath in child.code_dirs():
                yield os.path.join(self.name, subpath)

    def check(self, path):
        # TODO
        pass

    def html(self):
        # TODO
        return ''

if __name__ == '__main__':
    spec = Spec.from_str("""dir('', [
    dir('A', [txt('t2'), txt('t3')]),
    dir('B'),
    txt('t1'),
    ])""")
    for p in spec.code_dirs():
        print p
    exit(0)

class Assignment(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    duetime = models.DateTimeField()
    spec_str = models.TextField()
    dest_dir = models.FilePathField(max_length=512)
    spec_example_path = models.FilePathField(blank=True, max_length=512)

    @property
    def spec(self):
        if not hasattr(self, '_spec'):
            self._spec = Spec.from_str(self.spec_str)
        return self._spec

    def spec_example_url(self):
        # TODO
        return ''

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
        fields = ('title', 'description', 'duetime', 'spec_str')

class AssignmentModifyForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'duetime', 'spec_str')

