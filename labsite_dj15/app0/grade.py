from django.db import models
from upload import Submission, Score

class Run(models.Model):
    """
    state: running, finished.
    """
    procID = models.CharField(max_length=10)
    state = models.CharField(max_length=10)

    def get_proc(self):
        pass

def get_file_tree(user, submission):
    """
    @user: TA user.
    @return: A tree represented by recusive dicts, each leaf node is a fileID.

    Example returned value:
        {'LE_01': {'a.h':'fileID1', 'a.cpp':'fileID2'},
         'LE_01': {'a.h':'fileID3', 'a.cpp':'fileID4'},
         ...
         }
    """
    pass

def grade(user, submission, score):
    pass

def comment(user, submission, msg):
    pass

def run(user, compilation):
    # return an run instance
    pass
