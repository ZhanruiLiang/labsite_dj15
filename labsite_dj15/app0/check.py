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
import difflib
import threading

logger = logging.getLogger(__name__)

# class Compilation:
class Compilation(models.Model):
    subpath = models.FilePathField(max_length=100, blank=True)
    submission = models.ForeignKey(Submission)
    time = models.DateTimeField(auto_now_add=True, null=True)
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
    time = models.DateTimeField(auto_now_add=True, null=True)
    type = models.TextField(max_length=64)
    def delete(self, *args, **kwargs):
        try:
            shutil.rmtree(self.path)
        except e:
            pass
            # logger.debug('remove "{}" failed: {}'.format(self.path, e))
        super(Decompression, self).delete(*args, **kwargs)

class DiffResult(models.Model):
    assignment = models.ForeignKey('Assignment')
    problem = models.CharField(max_length=50)
    subm1 = models.ForeignKey(Submission, related_name='diff_sumbs1')
    subm2 = models.ForeignKey(Submission, related_name='diff_subms2')
    file1 = models.FilePathField(max_length=512)
    file2 = models.FilePathField(max_length=512)
    rate = models.FloatField()
    result = models.TextField()

    def lines_with_mark(self):
        lines = self.result.splitlines()
        return [(x[:2], x) for x in lines]

    def get_text1(self):
        fullpath = os.path.join(self.subm1.decompression.path, self.file1)
        return open(fullpath).read()

    def get_text2(self):
        fullpath = os.path.join(self.subm2.decompression.path, self.file2)
        return open(fullpath).read()

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

MIN_DIFF_RATE = 0.80
MIN_LINES = 30

def get_fullpath(subm, fpath):
    """
    subm: submission object
    fpath: for example 'HW5/3.14/xx.cpp'
    """
    return os.path.join(subm.decompression.path, fpath)

def compare(problem, subm1, fpath1, subm2, fpath2, force=False):
    """
    Check the files from fpath1 and fpath2. If their content are the same,
    it's a copy. If their different lines are less than d%, hand it to human
    with the 'diff' message to justify.

    fpath must be fullpath
    """
    try:
        dr = DiffResult.objects.get(subm1=subm1, subm2=subm2, 
                problem=problem.name, file1=fpath1, file2=fpath2)
        if force: dr.delete()
        else: return dr
    except DiffResult.DoesNotExist:
        pass
    fullpath1 = get_fullpath(subm1, fpath1)
    fullpath2 = get_fullpath(subm2, fpath2)
    # logger.debug('simcheck:\n  path1:{}\n  path2:{}'.format(fullpath1, fullpath2))
    text1 = open(fullpath1, 'r').read().splitlines()
    text2 = open(fullpath2, 'r').read().splitlines()
    # proc = subprocess.Popen(['diff', '--suppress-common-lines', 
    #     fullpath1, fullpath2], stdout=subprocess.PIPE])
    # proc.wait()
    if len(text1) > MIN_LINES and len(text2) > MIN_LINES:
        matcher = difflib.SequenceMatcher(a=text1, b=text2)
        rate = matcher.ratio()
        if rate >= MIN_DIFF_RATE:
            differ = difflib.Differ()
            result = []
            for line in differ.compare(text1, text2):
                mark = line[:2]
                if mark == '+ ' or mark == '- ':
                    result.append(line)
            result = '\n'.join(result)
        else:
            result = '(suppressed)'
    else:
        rate = 0
        result = '(too short)'
    dr = DiffResult(assignment=subm1.assignment, subm1=subm1, subm2=subm2,
            problem=problem.name, file1=fpath1, file2=fpath2, rate=rate, result=result)
    dr.save()

def need_compare(fname):
    return os.path.splitext(fname)[-1] in ['.h', '.cpp', '.hpp', '.cxx', '.cc', '.c']

# use lock to make sure only one check runing at anytime
gDiffCheckLock = threading.Lock()

def start_diff_check(assignment, force=False):
    if gDiffCheckLock.locked():
        return 1
    gDiffCheckLock.acquire()
    th = threading.Thread(target=diff_check, args=(assignment, force))
    th.start()
    gDiffCheckLock.release()
    return 0

def diff_check(assignment, force=False):
    if force:
        assignment.diffresult_set.all().delete()
    subms0 = list(assignment.submission_set.filter(retcode=0))
    subms = []
    for subm in subms0:
        try:
            subm.decompression.path
            subms.append(subm)
        except: pass
    n = len(subms)
    root = assignment.spec.name
    def get_dir(subm, problem):
        # try:
        #     subm.decompression.path
        # except:
        #     logger.debug('subm:{s.id}'.format(s=subm))
        dirpath = os.path.join(subm.decompression.path, root, problem.name)
        files = filter(need_compare, os.listdir(dirpath))
        return [os.path.join(root, problem.name, f) for f in files]

    for problem in assignment.problems:
        files = {}
        for subm in subms:
            files[subm] = get_dir(subm, problem)
        if problem.type == 'code':
            for i1 in xrange(n):
                files1 = files[subms[i1]]
                for i2 in xrange(i1+1, n):
                    if subms[i2].user == subms[i1].user:
                        continue
                    files2 = files[subms[i2]]
                    for fpath1 in files1:
                        for fpath2 in files2:
                            compare(problem, subms[i1], fpath1, subms[i2], fpath2)
        elif problem.type == 'text':
            for i1 in xrange(n):
                fpath1 = fpath2 = os.path.join(root, problem.name)
                for i2 in xrange(i1+1, n):
                    compare(problem, subms[i1], fpath1, subms[i2], fpath2)

