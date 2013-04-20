# -*- encoding=utf-8 -*-
from django.db import models
from django.template import Template, Context 
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
import subprocess
import re, os, sys, shutil
import tempfile
from errors import *
from spec import Assignment
from upload import Submission
import logging

logger = logging.getLogger(__name__)

# class Compilation:
class Compilation(models.Model):
    subpath = models.FilePathField(max_length=100, blank=True)
    submission = models.ForeignKey(Submission)
    cmd = models.TextField(blank=True, default='')
    exe = models.FilePathField(blank=True, max_length=512)
    result = models.TextField(blank=True, default='')

    @property
    def assignment(self):
        return self.submission.assignment

    def delete(self):
        try:
            os.remove(self.exe)
        except: pass
        super(Compilation, self).delete()

class Decompression(models.Model):
    submission = models.OneToOneField(Submission, related_name='decompression')
    result = models.TextField(blank=True, default='')
    path = models.FilePathField(max_length=512)
    type = models.TextField(max_length=64)
    def delete(self, *args, **kwargs):
        try:
            shutil.rmtree(self.path)
        except e: 
            pass
            # logger.debug('remove "{}" failed: {}'.format(self.path, e))
        super(Decompression, self).delete(*args, **kwargs)

def pre_delete_deccompression(sender, *args, **kwargs):
    submission = kwargs['instance']
    try: 
        dec = submission.decompression
        dec.delete()
    except: pass
    try:
        submission.compilation_set.delete()
    except: pass
pre_delete.connect(pre_delete_deccompression, sender=Submission)

def check_file_type(path):
    try:
        p = subprocess.Popen(['file', '--mime-type', '-b', path], stdout=subprocess.PIPE)
        p.wait()
        result = p.stdout.read()
        return result
    except OSError:
        return None

DecompressHandlers = {
        'application/x-gzip': lambda s, d: ['tar', 'xf', s, '-C', d],
        'application/zip': lambda s, d: ['unzip', '-qqo', s, '-d', d],
        # 'application/x-rar': lambda s, d: ['unrar', 'x', '-y', s, d],
        'application/x-bzip2': lambda s, d: ['tar', 'xf', s, '-C', d],
        'application/x-tar': lambda s, d: ['tar', 'xf', s, '-C', d],
        }
SupportArchiveFormats = ('gzip', 'zip', 'bzip2', 'tar')

def decompress(submission):
    srcpath = submission.path
    base, name = os.path.split(srcpath)
    destpath = os.path.join(base, name+'.dec')
    type = check_file_type(srcpath).rstrip()
    if type not in DecompressHandlers:
        raise CheckError('Unknown archive format. Please Use {}.'.format(
            ', '.join(SupportArchiveFormats)))
    if os.path.exists(destpath):
        raise CheckError('Folder exists')
    os.mkdir(destpath)
    # create Decompression instance
    dec = Decompression(submission=submission, type=type, path=destpath)
    cmd = DecompressHandlers[type](srcpath, destpath)
    logger.debug('cmd:{}'.format(cmd))
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.poll() != 0:
        result = '\n'.join([p.stderr.read(), p.stdout.read()])
        dec.result = result
        dec.save()
        raise CheckError(result)
    dec.save()
    return dec

def check_submission(submission):
    dec = decompress(submission)
    submission.assignment.spec.check(dec.path)
    compile_submission(submission, dec.path)

def is_cpp(fname):
    return fname.endswith('.cpp') or fname.endswith('.cxx') or fname.endswith('.cc')

def compile_submission(submission, path):
    """
    compile a whole submission recursively
    @path: path to the decompressed files
    """
    spec = submission.assignment.spec
    for subpath in spec.code_dirs():
        fullpath = os.path.join(path, subpath)
        files = []
        cpp11 = False
        for fname in os.listdir(fullpath):
            if is_cpp(fname):
                files.append(fname.decode('utf8'))
            if fname == '.c++11':
                cpp11 = True
        if not files: continue
        exe = 'exe'
        if cpp11:
            cmd = ['g++', '-std=c++11', '-o', exe] + files
        else:
            cmd = ['g++', '-o', exe] + files
        comp = Compilation(subpath=subpath,
                submission=submission,
                cmd=repr(cmd),
                exe=os.path.join(fullpath, exe),
                )
        try:
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, cwd=fullpath)
            p.wait()
            if p.poll() != 0:
                result = comp.result = ' '.join(cmd) + '\n' + p.stderr.read().decode('utf8')
                raise CompileError(result)
            comp.result = 'success'
        except OSError as err:
            comp.result = err.message
            raise CompileError(err.message)
        finally:
            comp.save()

def similarity_check(fpath1, fpath2):
    """
    Check the files from fpath1 and fpath2. If their content are the same,
    it's a copy. If their different lines are less than d%, hand it to human
    with the 'diff' message to justify.
    """
    pass
