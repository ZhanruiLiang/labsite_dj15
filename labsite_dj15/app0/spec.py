from django.db import models
from django.conf import settings
from django import forms
from errors import *
import os, subprocess

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

        self._html = None

    def code_dirs(self):
        # iter method
        yield self.name
        for child in self.childs:
            for subpath in child.code_dirs():
                yield os.path.join(self.name, subpath)

    def get_tree(self, path):
        p = subprocess.Popen(['tree', path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        if p.poll() == 0:
            return p.stdout.read()
        else:
            return p.stderr.read()

    def check(self, path):
        errors = []
        self._check(path, '', errors)
        if errors:
            treeOutput = self.get_tree(path)
            errors.extend(['Archive tree:', treeOutput])
            raise FormatError('\n'.join(errors))

    def _check(self, path, subpath, errors):
        files = os.listdir(path)
        nextSubpath = os.path.join(subpath, self.name)
        if self.name not in files:
            errors.append('File/directory \'{}\' not found in archive.'.format(nextSubpath))
        else:
            nextPath = os.path.join(path, self.name)
            for child in self.childs:
                child._check(nextPath, nextSubpath, errors)

    def html(self):
        if self._html is None:
            self._html = '\n'.join(self._gen_html(0, []))
        return self._html

    def _gen_html(self, depth, lines):
        if self.type == Spec.DIR:
            typeDesc = 'Directory'
        elif self.type == Spec.TXT:
            typeDesc = 'ASCII text'
        else:
            typeDesc = 'Any'
        lines.append('{indent}<b>{name}</b>({type}){end}'.format(
                indent='  '*depth,
                name=self.name,
                type=typeDesc,
                end=(': ...', ':')[bool(self.childs)]
                ))
        for child in self.childs:
            child._gen_html(depth + 1, lines)
        return lines

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
    description = models.TextField()
    duetime = models.DateTimeField()
    spec_str = models.TextField()
    dest_dir = models.FilePathField(max_length=512)
    example = models.FileField(
            blank=True,
            upload_to=lambda ass,fname: 'examples/{}/{}'.format(ass.title, fname),
            help_text='An example submission')

    @property
    def spec(self):
        if not hasattr(self, '_spec'):
            self._spec = Spec.from_str(self.spec_str)
        return self._spec

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

class AssignmentModifyForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'duetime', 'spec_str', 'example')

