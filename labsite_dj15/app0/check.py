from django.db import models

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

def check_format(directory, spec):
    """
    Check if the directory is satisfying the spec.
    """
    pass

def compile_single(user, submission, subpath, command=None):
    """
    Compile a single folder.

    @user: A TA user who wants to compile the code
    @submission: A Submission instance
    @subpath: Subpath from the 
    @command: the compile command
    """
    pass

def compile_submission(user, submission):
    """
    compile a whole submission recursively

    @user: A TA user who wants to compile the code
    """
    pass

def similarity_check(fpath1, fpath2):
    """
    Check the files from fpath1 and fpath2. If their content are the same,
    it's a copy. If their different lines are less than d%, hand it to human
    with the 'diff' message to justify.
    """
    pass
