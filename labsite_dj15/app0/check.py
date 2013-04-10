from django.db import models
from django.template import Template, Context 
import subprocess
import re, os, sys
import tempfile
from errors import *

class CompileState:
    compiling = 'compiling'
    error = 'error'
    finished = 'finished'
    
class Compilation(models.Model):
    srcdir = models.CharField("source directory", max_length=512)
    exec_path = models.CharField("executable file path", max_length=512)
    state = models.CharField(
            "compiling state, may be: compiling, error, finished.",
            max_length=20, default=CompileState.compiling)
    error = models.TextField(default='')

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
        'application/zip': lambda s, d: ['unzip', s, '-d', d],
        'application/x-rar': lambda s, d: ['unrar', 'x', '-y', s, d],
        'application/x-bzip2': lambda s, d: ['tar', 'xf', s, '-C', d],
        'application/x-tar': lambda s, d: ['tar', 'xf', s, '-C', d],
        }
SupportArchiveFormats = ('gzip', 'zip', 'rar', 'bzip2', 'tar')

def decompress(srcpath):
    destpath = tempfile.mkdtemp()
    type = check_file_type(srcpath).rstrip()
    if type not in DecompressHandlers:
        raise CheckError('Unknown archive format. Please Use {}.'.format(
            ', '.join(SupportArchiveFormats)))
    cmd = DecompressHandlers[type](srcpath, destpath)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    if p.poll() != 0:
        raise CheckError('\n'.join([p.stderr.read(), p.stdout.read()]))
    sub = os.listdir(destpath)
    # if len(sub) == 1:
    #     return os.path.join(destpath, sub[0])
    # else:
    return destpath

def check_submission(submission):
    dest = decompress(submission.path)
    submission.assignment.spec.check(dest)
    compile_submission(submission, dest)

def is_cpp(fname):
    return fname.endswith('.cpp') or fname.endswith('.cxx') or fname.endswith('.cc')

def compile_single(path, command=None):
    """
    Compile a single folder.

    @path: Subpath from the 
    @command: the compile command
    """
    cmd = ['g++', '-o', tempfile.mktemp()]
    files = []
    for fname in os.listdir(path):
        if is_cpp(fname):
            files.append(os.path.join(path, fname))
    if files:
        try:
            cmd += files
            p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            p.wait()
            if p.poll() != 0:
                raise CompileError(' '.join(cmd) + '\n' + p.stderr.read())
        except OSError as err:
            raise CompileError(err.message)

def compile_submission(submission, path):
    """
    compile a whole submission recursively
    @path: path to the decompressed files
    """
    spec = submission.assignment.spec
    for subpath in spec.code_dirs():
        fullpath = os.path.join(path, subpath)
        compile_single(fullpath)

def similarity_check(fpath1, fpath2):
    """
    Check the files from fpath1 and fpath2. If their content are the same,
    it's a copy. If their different lines are less than d%, hand it to human
    with the 'diff' message to justify.
    """
    pass
