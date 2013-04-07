from django.db import models
from django.conf import settings
from django import forms
import os

class Spec:
    """
    Spec example:

    spec_hw2 = Spec({
        'answers.txt': Spec.Text,
        '3.16': Spec.Codes,
        '3.17': Spec.Codes,
        })
    spec_lab2 = Spec({
        'LE_01': Spec.Codes,
        'LE_02': Spec.Codes,
        'LE_03': Spec.Codes,
        'DEBUG': Spec.Codes,
        'PC_01': Spec.Codes,
        'PC_03': Spec.Codes,
        })
    """
    Codes = object()
    Text = object()
    def __init__(self, specStr):
        self.struct = specStr
        # TODO: eval specStr

class Assignment(models.Model):
    title = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    duetime = models.DateTimeField()
    spec_str = models.TextField()
    dest_dir = models.FilePathField(max_length=512)

    @property
    def spec(self):
        if not hasattr(self, '_spec'):
            self._spec = Spec(self.spec_str)
        return self._spec

    def spec_html(self):
        spec = self.spec
        return str(spec.struct)

def make_ass_dir(assignment):
    base = settings.ASSIGNMENT_BASE_DIR
    name = '{}'.format(assignment.title.replace(' ', '_'))
    dest = os.path.join(base, name)
    if not os.path.exists(dest):
        os.mkdir(dest)
    elif not os.path.isdir(dest):
        return (False, "Directory exists.")
    return (True, dest)

class AssignmentCreationForm(forms.ModelForm):
    # title = forms.CharField(Assignment._meta.get_field('title').max_length)
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'duetime', 'spec_str')
